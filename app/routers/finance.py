from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import csv
import io
import json

from ..database import get_db
from .. import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/static/templates")

# HTML Page Routes (must come before API routes to avoid conflicts)
@router.get("/", response_class=HTMLResponse)
def finance_page(request: Request):
    """Main finance page with all tabs"""
    return templates.TemplateResponse("finance.html", {"request": request})

@router.get("/overview", response_class=HTMLResponse)
def finance_overview_page(request: Request):
    """Finance overview page"""
    return templates.TemplateResponse("finance_overview.html", {"request": request})

@router.get("/accounts", response_class=HTMLResponse)
def finance_accounts_page(request: Request):
    """Finance accounts page"""
    return templates.TemplateResponse("finance_accounts.html", {"request": request})

@router.get("/transactions", response_class=HTMLResponse)
def finance_transactions_page(request: Request):
    """Finance transactions page"""
    return templates.TemplateResponse("finance_transactions.html", {"request": request})

@router.get("/budget", response_class=HTMLResponse)
def finance_budget_page(request: Request):
    """Finance budget page"""
    return templates.TemplateResponse("finance_budget.html", {"request": request})

@router.get("/recurring", response_class=HTMLResponse)
def finance_recurring_page(request: Request):
    """Finance recurring transactions page"""
    return templates.TemplateResponse("finance_recurring.html", {"request": request})

# API Endpoints (using /api/ prefix to avoid conflicts)
@router.get("/api/summary")
def get_financial_summary(db: Session = Depends(get_db)):
    """Get financial summary data"""
    return crud.get_financial_summary(db)

@router.get("/api/categories")
def get_finance_categories(db: Session = Depends(get_db)):
    """Get all finance categories"""
    return crud.get_finance_categories(db)

@router.get("/api/accounts")
def get_accounts(db: Session = Depends(get_db)):
    """Get all financial accounts"""
    return crud.get_financial_accounts(db)

@router.post("/api/accounts")
def add_account(
    account_name: str = Form(...),
    balance: float = Form(...),
    institution: str = Form("Banking"),
    account_type: str = Form("checking"),
    notes: str = Form(None)
):
    """Add a new account"""
    db = next(get_db())
    try:
        result = crud.add_account(db, account_name, balance, institution, account_type, notes)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/api/accounts/{account_name}")
def update_account_metadata(
    account_name: str,
    institution: str = Form(None),
    account_type: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update account metadata"""
    try:
        result = crud.update_account_metadata(db, account_name, institution, account_type, notes)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/accounts/{account_name}/balance")
def update_account_balance(
    account_name: str,
    balance: float = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update account balance"""
    try:
        result = crud.update_account_balance(db, account_name, balance, notes)
        return {"message": "Balance updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/accounts/{account_name}/calculate-balance")
def calculate_account_balance(
    account_name: str,
    db: Session = Depends(get_db)
):
    """Calculate and store account balance based on transactions"""
    try:
        result = crud.calculate_and_store_daily_balance(db, account_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating balance for {account_name}: {str(e)}")

@router.get("/api/transactions")
def get_transactions(limit: int = 100, db: Session = Depends(get_db)):
    """Get recent transactions"""
    return crud.get_transactions(db, limit)

@router.post("/api/transactions")
def add_transaction(
    account_name: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    description: str = Form(None),
    notes: str = Form(None),
    date: str = Form(...),
    required_spending: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Add a new transaction"""
    try:
        # Parse date
        transaction_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        result = crud.add_transaction(db, account_name, amount, category, description, transaction_date, required_spending)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/api/transactions/{transaction_id}")
def update_transaction(
    transaction_id: int,
    account_name: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    description: str = Form(None),
    notes: str = Form(None),
    date: str = Form(...),
    required_spending: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Update an existing transaction"""
    try:
        # Parse date
        transaction_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        result = crud.update_transaction(db, transaction_id, account_name, category, amount, description, notes, transaction_date, required_spending)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete a transaction"""
    try:
        result = crud.delete_transaction(db, transaction_id)
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/recent-transactions")
def get_recent_transactions(limit: int = 5, db: Session = Depends(get_db)):
    """Get most recent transactions"""
    return crud.get_recent_transactions(db, limit)

@router.get("/api/networth")
def get_networth_history(db: Session = Depends(get_db)):
    """Get net worth history"""
    return crud.get_networth_history(db)

@router.get("/api/spending")
def get_spending_over_time(db: Session = Depends(get_db)):
    """Get spending data over time"""
    return crud.get_spending_over_time(db)

# CSV Import/Export
@router.post("/api/accounts/import")
async def import_accounts_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import accounts from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        content = await file.read()
        csv_text = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_accounts = []
        for row in csv_reader:
            account_name = row.get('account_name', '').strip()
            balance = float(row.get('balance', 0))
            institution = row.get('institution', 'Banking').strip()
            account_type = row.get('account_type', 'checking').strip()
            notes = row.get('notes', '').strip()
            
            if account_name:
                result = crud.add_account(db, account_name, balance, institution, account_type, notes)
                imported_accounts.append(result)
        
        return {"message": f"Successfully imported {len(imported_accounts)} accounts", "accounts": imported_accounts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")

@router.get("/api/accounts/export")
def export_accounts_csv(db: Session = Depends(get_db)):
    """Export accounts to CSV file"""
    accounts = crud.get_financial_accounts(db)
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['account_name', 'balance', 'institution', 'account_type', 'notes'])
    
    for account in accounts:
        writer.writerow([
            account['account_name'],
            account['balance'],
            account['institution'],
            account['account_type'],
            account.get('notes', '')
        ])
    
    output.seek(0)
    return FileResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type='text/csv',
        filename='accounts_export.csv'
    )

@router.get("/api/accounts/export/csv")
def export_accounts_csv_alt(db: Session = Depends(get_db)):
    """Alternative CSV export endpoint"""
    return export_accounts_csv(db)

@router.get("/api/accounts/export/sample")
def get_sample_csv():
    """Get a sample CSV file for account import"""
    sample_data = """account_name,balance,institution,account_type,notes
Main Checking,5000.00,Bank of America,checking,Primary checking account
Savings Account,15000.00,Bank of America,savings,Emergency fund
Credit Card,-2500.00,Chase,credit,Main credit card
Investment Account,50000.00,Vanguard,investment,Retirement savings"""
    
    return FileResponse(
        io.BytesIO(sample_data.encode()),
        media_type='text/csv',
        filename='accounts_sample.csv'
    )

@router.get("/api/accounts/sample-csv")
def get_sample_csv_alt():
    """Alternative sample CSV endpoint"""
    return get_sample_csv()

@router.post("/api/accounts/import/csv")
async def import_accounts_csv_alt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Alternative CSV import endpoint"""
    return await import_accounts_csv(file, db)

# Account Details
@router.get("/api/accounts/{account_name}/details")
def get_account_details(account_name: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific account"""
    try:
        # Get account transactions
        transactions = crud.get_account_transactions(db, account_name, limit=1000)
        
        # Get account balance history
        balance_history = crud.get_account_balance_history(db, account_name)
        
        # Get account summary
        summary = crud.get_account_summary(db, account_name)
        
        # Get current account info
        accounts = crud.get_financial_accounts(db)
        current_account = next((acc for acc in accounts if acc['account_name'] == account_name), None)
        
        return {
            "account": current_account,
            "transactions": transactions,
            "balance_history": balance_history,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Setup endpoints
@router.post("/api/setup/example-data")
def setup_example_data(db: Session = Depends(get_db)):
    """Set up example finance data"""
    try:
        # Setup categories
        categories_result = crud.setup_finance_categories(db)
        
        # Add some example accounts
        example_accounts = [
            {"name": "Main Checking", "balance": 5000, "institution": "Bank of America", "type": "checking"},
            {"name": "Savings", "balance": 15000, "institution": "Bank of America", "type": "savings"},
            {"name": "Credit Card", "balance": -2500, "institution": "Chase", "type": "credit"}
        ]
        
        for account in example_accounts:
            crud.add_account(db, account["name"], account["balance"], account["institution"], account["type"])
        
        return {
            "message": "Example data setup complete",
            "categories": categories_result,
            "accounts_added": len(example_accounts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up example data: {str(e)}") 