from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/finance", tags=["finance"])

@router.get("/summary", response_model=Dict[str, Any])
def get_financial_summary(db: Session = Depends(get_db)):
    """Get comprehensive financial summary including total balance, accounts, and recent transactions"""
    return crud.get_financial_summary(db)

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

@router.get("/transactions", response_model=List[Dict[str, Any]])
def get_transactions(limit: int = 100, db: Session = Depends(get_db)):
    """Get recent transactions"""
    return crud.get_transactions(db, limit)

@router.post("/transactions")
def add_transaction(
    account_name: str,
    category: str,
    amount: float,
    description: str = None,
    transaction_date: datetime = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Add a new transaction"""
    try:
        result = crud.add_transaction(
            db, account_name, category, amount, transaction_date, notes
        )
        return {"message": "Transaction added successfully", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add transaction: {str(e)}"
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