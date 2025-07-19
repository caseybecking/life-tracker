from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from . import models, schemas

# Noun operations
def get_noun(db: Session, noun_id: int) -> Optional[models.Noun]:
    return db.query(models.Noun).filter(models.Noun.id == noun_id).first()

def get_noun_by_name(db: Session, name: str) -> Optional[models.Noun]:
    return db.query(models.Noun).filter(models.Noun.name == name).first()

def get_nouns(db: Session, skip: int = 0, limit: int = 100) -> List[models.Noun]:
    return db.query(models.Noun).offset(skip).limit(limit).all()

def create_noun(db: Session, noun: schemas.NounCreate) -> models.Noun:
    db_noun = models.Noun(**noun.dict())
    db.add(db_noun)
    db.commit()
    db.refresh(db_noun)
    return db_noun

# Attribute operations
def get_attribute(db: Session, attribute_id: int) -> Optional[models.Attribute]:
    return db.query(models.Attribute).filter(models.Attribute.id == attribute_id).first()

def get_attributes_by_noun(db: Session, noun_id: int) -> List[models.Attribute]:
    return db.query(models.Attribute).filter(models.Attribute.noun_id == noun_id).all()

def get_attribute_by_name_and_noun(db: Session, noun_id: int, name: str) -> Optional[models.Attribute]:
    return db.query(models.Attribute).filter(
        and_(models.Attribute.noun_id == noun_id, models.Attribute.name == name)
    ).first()

def create_attribute(db: Session, attribute: schemas.AttributeCreate) -> models.Attribute:
    db_attribute = models.Attribute(**attribute.dict())
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute

# Value operations
def get_value(db: Session, value_id: int) -> Optional[models.Value]:
    return db.query(models.Value).filter(models.Value.id == value_id).first()

def get_values_by_attribute(db: Session, attribute_id: int) -> List[models.Value]:
    return db.query(models.Value).filter(models.Value.attribute_id == attribute_id).all()

def get_value_by_name_and_attribute(db: Session, attribute_id: int, name: str) -> Optional[models.Value]:
    return db.query(models.Value).filter(
        and_(models.Value.attribute_id == attribute_id, models.Value.name == name)
    ).first()

def create_value(db: Session, value: schemas.ValueCreate) -> models.Value:
    db_value = models.Value(**value.dict())
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value

# Data operations
def get_data(db: Session, data_id: int) -> Optional[models.Data]:
    return db.query(models.Data).filter(models.Data.id == data_id).first()

def get_data_by_value(db: Session, value_id: int, limit: int = 100) -> List[models.Data]:
    return db.query(models.Data).filter(models.Data.value_id == value_id).order_by(
        models.Data.date_recorded.desc()
    ).limit(limit).all()

def create_data(db: Session, data: schemas.DataCreate) -> models.Data:
    db_data = models.Data(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

# Hierarchical operations
def get_noun_with_attributes(db: Session, noun_name: str) -> Optional[Dict[str, Any]]:
    """Get a noun with all its attributes, values, and data"""
    noun = get_noun_by_name(db, noun_name)
    if not noun:
        return None
    
    result = {
        "noun": {
            "id": noun.id,
            "name": noun.name,
            "description": noun.description,
            "created_at": noun.created_at,
            "updated_at": noun.updated_at
        },
        "attributes": {}
    }
    
    for attr in noun.attributes:
        result["attributes"][attr.name] = {
            "attribute": {
                "id": attr.id,
                "noun_id": attr.noun_id,
                "name": attr.name,
                "description": attr.description,
                "created_at": attr.created_at,
                "updated_at": attr.updated_at
            },
            "values": {}
        }
        
        for val in attr.values:
            data_entries = get_data_by_value(db, val.id)
            result["attributes"][attr.name]["values"][val.name] = {
                "value": {
                    "id": val.id,
                    "attribute_id": val.attribute_id,
                    "name": val.name,
                    "data_type": val.data_type,
                    "description": val.description,
                    "created_at": val.created_at,
                    "updated_at": val.updated_at
                },
                "data": [
                    {
                        "id": data.id,
                        "value_id": data.value_id,
                        "data_value": data.data_value,
                        "date_recorded": data.date_recorded,
                        "notes": data.notes,
                        "created_at": data.created_at,
                        "updated_at": data.updated_at
                    }
                    for data in data_entries
                ]
            }
    
    return result

def track_data(db: Session, noun_name: str, attribute_name: str, value_name: str, 
               data_value: str, data_type: str = "string", notes: str = None) -> models.Data:
    """Track data using the EAV model. Creates nouns, attributes, and values if they don't exist."""
    
    # Get or create noun
    noun = get_noun_by_name(db, noun_name)
    if not noun:
        noun = create_noun(db, schemas.NounCreate(name=noun_name))
    
    # Get or create attribute
    attribute = get_attribute_by_name_and_noun(db, noun.id, attribute_name)
    if not attribute:
        attribute = create_attribute(db, schemas.AttributeCreate(
            noun_id=noun.id, name=attribute_name
        ))
    
    # Get or create value
    value = get_value_by_name_and_attribute(db, attribute.id, value_name)
    if not value:
        value = create_value(db, schemas.ValueCreate(
            attribute_id=attribute.id, name=value_name, data_type=data_type
        ))
    
    # Create data entry
    data = create_data(db, schemas.DataCreate(
        value_id=value.id, data_value=data_value, notes=notes
    ))
    
    return data

# Financial specific operations
def get_financial_accounts(db: Session) -> List[Dict[str, Any]]:
    """Get all financial accounts with their current balances"""
    banking_noun = get_noun_by_name(db, "Banking")
    if not banking_noun:
        return []
    
    accounts = []
    for attr in banking_noun.attributes:
        # Get the balance value for this account
        balance_value = get_value_by_name_and_attribute(db, attr.id, "Balance")
        if balance_value:
            latest_balance = db.query(models.Data).filter(
                models.Data.value_id == balance_value.id
            ).order_by(models.Data.date_recorded.desc()).first()
            
            accounts.append({
                "id": attr.id,
                "institution": "Banking",  # Could be made dynamic
                "account_name": attr.name,
                "balance": float(latest_balance.data_value) if latest_balance else 0.0,
                "last_updated": latest_balance.date_recorded if latest_balance else None
            })
    
    return accounts

def update_account_balance(db: Session, account_name: str, new_balance: float, notes: str = None):
    """Update the balance for a specific account"""
    return track_data(
        db=db,
        noun_name="Banking",
        attribute_name=account_name,
        value_name="Balance",
        data_value=str(new_balance),
        data_type="number",
        notes=notes
    )

def get_transactions(db: Session, limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent transactions"""
    banking_noun = get_noun_by_name(db, "Banking")
    if not banking_noun:
        return []
    
    transactions = []
    for attr in banking_noun.attributes:
        if "Transaction" in attr.name:
            # Get transaction data
            transaction_values = get_values_by_attribute(db, attr.id)
            for val in transaction_values:
                data_entries = get_data_by_value(db, val.id, limit)
                for data in data_entries:
                    transactions.append({
                        "id": data.id,
                        "account": attr.name,
                        "category": val.name,
                        "amount": float(data.data_value),
                        "date": data.date_recorded,
                        "notes": data.notes
                    })
    
    # Sort by date descending
    transactions.sort(key=lambda x: x["date"], reverse=True)
    return transactions[:limit]

def add_transaction(db: Session, account_name: str, category: str, amount: float, 
                   transaction_date: datetime = None, notes: str = None):
    """Add a new transaction"""
    if transaction_date is None:
        transaction_date = datetime.now()
    
    return track_data(
        db=db,
        noun_name="Banking",
        attribute_name=f"{account_name}_Transaction",
        value_name=category,
        data_value=str(amount),
        data_type="number",
        notes=notes
    )

# Utility functions
def get_total_balance(db: Session) -> float:
    """Calculate total balance across all accounts"""
    accounts = get_financial_accounts(db)
    return sum(account["balance"] for account in accounts)

def get_financial_summary(db: Session) -> Dict[str, Any]:
    """Get a comprehensive financial summary"""
    return {
        "total_balance": get_total_balance(db),
        "accounts": get_financial_accounts(db),
        "recent_transactions": get_transactions(db, limit=20)
    } 