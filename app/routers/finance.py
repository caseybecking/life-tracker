from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import csv
import io
import tempfile
import os
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/finance", tags=["finance"])

@router.get("/summary", response_model=Dict[str, Any])
def get_financial_summary(db: Session = Depends(get_db)):
    """Get comprehensive financial summary including total balance, accounts, and recent transactions"""
    return crud.get_financial_summary(db)

@router.get("/networth", response_model=Dict[str, Any])
def get_networth_data(db: Session = Depends(get_db)):
    """Get net worth data over time"""
    try:
        networth_data = crud.get_networth_history(db)
        return networth_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get net worth data: {str(e)}"
        )

@router.get("/spending", response_model=Dict[str, Any])
def get_spending_data(db: Session = Depends(get_db)):
    """Get spending data over time"""
    try:
        spending_data = crud.get_spending_over_time(db)
        return spending_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get spending data: {str(e)}"
        )

@router.get("/recent-transactions", response_model=List[Dict[str, Any]])
def get_recent_transactions(limit: int = 5, db: Session = Depends(get_db)):
    """Get most recent transactions across all accounts"""
    try:
        recent_transactions = crud.get_recent_transactions(db, limit)
        return recent_transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent transactions: {str(e)}"
        )

@router.get("/accounts", response_model=List[Dict[str, Any]])
def get_accounts(db: Session = Depends(get_db)):
    """Get all bank accounts with current balances"""
    return crud.get_financial_accounts(db)

@router.post("/accounts/{account_name}/balance")
def update_account_balance(
    account_name: str,
    balance: float,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Update the balance for a specific account"""
    try:
        result = crud.update_account_balance(db, account_name, balance, notes)
        return {"message": "Balance updated successfully", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update balance: {str(e)}"
        )

@router.get("/accounts/export/csv")
def export_accounts_csv(db: Session = Depends(get_db)):
    """Export all accounts to CSV format"""
    try:
        accounts = crud.get_financial_accounts(db)
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Account Name', 'Balance', 'Institution', 'Account Type', 'Notes', 'Last Updated'])
        
        # Write data
        for account in accounts:
            writer.writerow([
                account['account_name'],
                account['balance'],
                account.get('institution', ''),
                account.get('account_type', ''),
                account.get('notes', ''),
                account.get('last_updated', '').strftime('%Y-%m-%d %H:%M:%S') if account.get('last_updated') else ''
            ])
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(output.getvalue())
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            tmp_file_path,
            media_type='text/csv',
            filename=f'accounts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export accounts: {str(e)}"
        )

@router.get("/accounts/export/sample")
def download_sample_csv():
    """Download a sample CSV template for account import"""
    try:
        # Create sample CSV content
        sample_data = [
            ['Account Name', 'Balance', 'Institution', 'Account Type', 'Notes'],
            ['SF_Checking', '11818.71', 'Bank of America', 'checking', 'Primary checking account'],
            ['Cuna', '5000.00', 'Credit Union', 'savings', 'Emergency fund'],
            ['Credit_Card', '-1250.50', 'Chase', 'credit', 'Main credit card'],
            ['Investment_401k', '45000.00', 'Fidelity', 'investment', 'Retirement account'],
            ['Car_Loan', '-15000.00', 'Auto Finance', 'loan', 'Vehicle loan']
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(sample_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(output.getvalue())
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            tmp_file_path,
            media_type='text/csv',
            filename='accounts_sample_template.csv'
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sample CSV: {str(e)}"
        )

@router.post("/accounts/import/csv")
async def import_accounts_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import accounts from CSV file"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        content = await file.read()
        csv_text = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_accounts = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Validate required fields
                if not row.get('Account Name'):
                    errors.append(f"Row {row_num}: Account Name is required")
                    continue
                
                # Parse balance
                try:
                    balance = float(row.get('Balance', 0))
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid balance format")
                    continue
                
                # Update account
                notes = f"Imported from CSV - {row.get('Notes', '')}"
                result = crud.update_account_balance(
                    db, 
                    row['Account Name'], 
                    balance, 
                    notes
                )
                
                imported_accounts.append({
                    'account_name': row['Account Name'],
                    'balance': balance,
                    'institution': row.get('Institution', ''),
                    'account_type': row.get('Account Type', ''),
                    'notes': row.get('Notes', '')
                })
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "message": "CSV import completed",
            "imported_accounts": len(imported_accounts),
            "accounts": imported_accounts,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import CSV: {str(e)}"
        )

@router.get("/transactions", response_model=List[Dict[str, Any]])
def get_transactions(limit: int = 100, db: Session = Depends(get_db)):
    """Get recent transactions"""
    return crud.get_transactions(db, limit)

@router.post("/transactions")
def add_transaction(
    account_name: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    date: str = Form(None),
    db: Session = Depends(get_db)
):
    """Add a new transaction"""
    try:
        # Parse date if provided
        transaction_date = None
        if date:
            try:
                transaction_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        result = crud.add_transaction(
            db, account_name, category, amount, description, notes, transaction_date
        )
        return {"message": "Transaction added successfully", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add transaction: {str(e)}"
        )

@router.put("/transactions/{transaction_id}")
def update_transaction(
    transaction_id: int,
    account_name: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    date: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update an existing transaction"""
    try:
        # Parse date only if provided
        transaction_date = None
        if date:
            try:
                transaction_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        result = crud.update_transaction(
            db, transaction_id, account_name, category, amount, description, notes, transaction_date
        )
        return {"message": "Transaction updated successfully", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update transaction: {str(e)}"
        )

@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete a transaction"""
    try:
        crud.delete_transaction(db, transaction_id)
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete transaction: {str(e)}"
        )

@router.get("/balance/total")
def get_total_balance(db: Session = Depends(get_db)):
    """Get total balance across all accounts"""
    return {"total_balance": crud.get_total_balance(db)}

@router.get("/categories", response_model=List[Dict[str, Any]])
def get_finance_categories(db: Session = Depends(get_db)):
    """Get all available finance categories"""
    return crud.get_finance_categories(db)

@router.post("/setup/categories")
def setup_finance_categories(db: Session = Depends(get_db)):
    """Set up comprehensive finance categories"""
    try:
        result = crud.setup_finance_categories(db)
        return {"message": "Finance categories created successfully", "categories_created": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create categories: {str(e)}"
        )

# Example data endpoints for quick setup
@router.post("/setup/example-data")
def setup_example_financial_data(db: Session = Depends(get_db)):
    """Set up example financial data for testing"""
    try:
        # Create example accounts and balances
        crud.update_account_balance(db, "SF_Checking", 11818.71, "Initial balance")
        crud.update_account_balance(db, "Cuna", 5000.00, "Initial balance")
        
        # Add example transactions with proper categories
        crud.add_transaction(db, "SF_Checking", "Income", 2500.00, "Salary", notes="Monthly salary")
        crud.add_transaction(db, "SF_Checking", "Groceries", -150.00, "Grocery shopping", notes="Weekly groceries")
        crud.add_transaction(db, "SF_Checking", "Gas & Fuel", -45.00, "Fuel", notes="Car fuel")
        crud.add_transaction(db, "Cuna", "Income", 500.00, "Interest", notes="Monthly interest")
        
        return {"message": "Example financial data created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create example data: {str(e)}"
        ) 

@router.get("/accounts/{account_name}/details")
def get_account_details(account_name: str, db: Session = Depends(get_db)):
    """Get detailed account information including transactions and balance history"""
    try:
        # Get account information
        accounts = crud.get_financial_accounts(db)
        account = next((acc for acc in accounts if acc['account_name'] == account_name), None)
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account '{account_name}' not found"
            )
        
        # Get transactions for this account
        transactions = crud.get_account_transactions(db, account_name, limit=100)
        
        # Get balance history
        balance_history = crud.get_account_balance_history(db, account_name)
        
        # Calculate summary statistics
        summary = crud.get_account_summary(db, account_name)
        
        return {
            "account": account,
            "transactions": transactions,
            "balance_history": balance_history,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account details: {str(e)}"
        )

@router.get("/accounts/{account_name}/transactions")
def get_account_transactions(
    account_name: str, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get transactions for a specific account"""
    try:
        transactions = crud.get_account_transactions(db, account_name, limit)
        return transactions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account transactions: {str(e)}"
        )

@router.get("/accounts/{account_name}/balance-history")
def get_account_balance_history(account_name: str, db: Session = Depends(get_db)):
    """Get balance history for a specific account"""
    try:
        balance_history = crud.get_account_balance_history(db, account_name)
        return balance_history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get balance history: {str(e)}"
        )

@router.post("/accounts/{account_name}/calculate-balance")
def calculate_account_balance(
    account_name: str, 
    db: Session = Depends(get_db)
):
    """Calculate and store the daily balance for an account based on transactions"""
    try:
        result = crud.calculate_and_store_daily_balance(db, account_name)
        return {
            "message": "Balance calculated and stored successfully",
            "data": result
        }
    except Exception as e:
        import traceback
        print(f"Error calculating balance for {account_name}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate balance: {str(e)}"
        ) 