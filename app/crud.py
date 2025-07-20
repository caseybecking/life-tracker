from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any, Union
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

def create_value(db: Session, value) -> models.Value:
    """Create a new value, accepting either a schema object or a dictionary"""
    if hasattr(value, 'dict'):
        # It's a schema object
        value_data = value.dict()
    else:
        # It's a dictionary
        value_data = value
    
    db_value = models.Value(**value_data)
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

def create_data(db: Session, data) -> models.Data:
    """Create a new data entry, accepting either a schema object or a dictionary"""
    if hasattr(data, 'dict'):
        # It's a schema object
        data_dict = data.dict()
    else:
        # It's a dictionary
        data_dict = data
    
    db_data = models.Data(**data_dict)
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

def track_data(
    db: Session,
    noun_name: str,
    attribute_name: str,
    value_name: str,
    data_value: Union[str, float, int],
    data_type: str = "string",
    notes: str = None,
    required_spending: bool = False
) -> models.Data:
    """Track data with support for required spending flag"""
    
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
    
    # Create the data entry
    data_entry = models.Data(
        value_id=value.id,
        data_value=str(data_value),
        data_type=data_type,
        date_recorded=datetime.utcnow(),
        notes=notes
    )
    
    # Add required spending flag to metadata if specified
    if required_spending:
        import json
        metadata = {}
        if notes:
            try:
                metadata = json.loads(notes)
            except:
                metadata = {"notes": notes}
        metadata["required_spending"] = True
        data_entry.notes = json.dumps(metadata)
    
    db.add(data_entry)
    db.commit()
    db.refresh(data_entry)
    
    return data_entry

# Financial specific operations
def get_financial_accounts(db: Session) -> List[Dict[str, Any]]:
    """Get all financial accounts with their current balances"""
    banking_noun = get_noun_by_name(db, "Banking")
    if not banking_noun:
        return []
    
    accounts = []
    for attr in banking_noun.attributes:
        # Skip transaction attributes
        if "Transaction" in attr.name:
            continue
            
        # Get the balance value for this account
        balance_value = get_value_by_name_and_attribute(db, attr.id, "Balance")
        if balance_value:
            latest_balance = db.query(models.Data).filter(
                models.Data.value_id == balance_value.id
            ).order_by(models.Data.date_recorded.desc()).first()
            
            # Try to get account metadata from notes or description
            account_metadata = {}
            if latest_balance and latest_balance.notes:
                try:
                    # Parse metadata from notes if it's in JSON format
                    import json
                    metadata = json.loads(latest_balance.notes)
                    account_metadata = metadata
                except:
                    # If not JSON, use notes as institution
                    account_metadata = {"institution": latest_balance.notes}
            
            accounts.append({
                "id": attr.id,
                "institution": account_metadata.get("institution", "Banking"),
                "account_name": attr.name,
                "account_type": account_metadata.get("account_type", "checking"),
                "balance": float(latest_balance.data_value) if latest_balance else 0.0,
                "last_updated": latest_balance.date_recorded if latest_balance else None
            })
    
    return accounts

def add_account(db: Session, account_name: str, balance: float, institution: str = "Banking", 
                account_type: str = "checking", notes: str = None):
    """Add a new account"""
    # Create account metadata
    metadata = {
        "institution": institution,
        "account_type": account_type
    }
    
    # Store metadata in notes as JSON
    import json
    metadata_notes = json.dumps(metadata)
    
    # Create the account by adding a balance entry
    result = track_data(
        db=db,
        noun_name="Banking",
        attribute_name=account_name,
        value_name="Balance",
        data_value=str(balance),
        data_type="number",
        notes=metadata_notes
    )
    
    return {
        'id': result.id,
        'account_name': account_name,
        'institution': institution,
        'account_type': account_type,
        'balance': balance,
        'notes': notes
    }

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

def update_account_metadata(db: Session, account_name: str, institution: str = None, account_type: str = None, notes: str = None):
    """Update account metadata (institution, account type, notes)"""
    banking_noun = get_noun_by_name(db, "Banking")
    if not banking_noun:
        raise ValueError("Banking noun not found")
    
    account_attr = get_attribute_by_name_and_noun(db, banking_noun.id, account_name)
    if not account_attr:
        raise ValueError(f"Account '{account_name}' not found")
    
    balance_value = get_value_by_name_and_attribute(db, account_attr.id, "Balance")
    if not balance_value:
        raise ValueError(f"Balance value not found for account '{account_name}'")
    
    # Get the latest balance entry
    latest_balance = db.query(models.Data).filter(
        models.Data.value_id == balance_value.id
    ).order_by(models.Data.date_recorded.desc()).first()
    
    if not latest_balance:
        raise ValueError(f"No balance data found for account '{account_name}'")
    
    # Create new metadata
    metadata = {}
    if latest_balance.notes:
        try:
            import json
            metadata = json.loads(latest_balance.notes)
        except:
            # If not JSON, use existing notes as institution
            metadata = {"institution": latest_balance.notes}
    
    # Update metadata
    if institution is not None:
        metadata["institution"] = institution
    if account_type is not None:
        metadata["account_type"] = account_type
    
    # Store updated metadata
    import json
    metadata_notes = json.dumps(metadata)
    
    # Create a new balance entry with updated metadata
    result = track_data(
        db=db,
        noun_name="Banking",
        attribute_name=account_name,
        value_name="Balance",
        data_value=latest_balance.data_value,  # Keep the same balance
        data_type="number",
        notes=metadata_notes
    )
    
    return {
        'id': result.id,
        'account_name': account_name,
        'institution': metadata.get("institution", "Banking"),
        'account_type': metadata.get("account_type", "checking"),
        'balance': float(latest_balance.data_value),
        'notes': notes
    }

def get_transactions(db: Session, limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent transactions with required spending flag - supports both old and new formats"""
    banking_noun = get_noun_by_name(db, "Banking")
    if not banking_noun:
        return []
    
    transactions = []
    
    # Get all account attributes
    account_attrs = db.query(models.Attribute).filter(
        models.Attribute.noun_id == banking_noun.id
    ).all()
    
    for attr in account_attrs:
        # Skip balance attributes
        if attr.name.endswith('_Balance'):
            continue
            
        # Try new format first: look for "Transactions" value
        transactions_value = get_value_by_name_and_attribute(db, attr.id, "Transactions")
        if transactions_value:
            # New format: all transactions stored under "Transactions" value
            transaction_data = db.query(models.Data).filter(
                models.Data.value_id == transactions_value.id
            ).order_by(models.Data.date_recorded.desc()).limit(limit).all()
            
            for data in transaction_data:
                # Parse metadata
                metadata = {}
                required_spending = False
                if data.notes:
                    try:
                        import json
                        metadata = json.loads(data.notes)
                        required_spending = metadata.get("required_spending", False)
                    except:
                        # Fallback for old format
                        metadata = {"description": data.notes}
                
                transaction = {
                    'id': data.id,
                    'account': attr.name,
                    'amount': float(data.data_value),
                    'category': metadata.get("category", "Uncategorized"),
                    'description': metadata.get("description", ""),
                    'date': data.date_recorded,
                    'updated_at': data.updated_at,
                    'required_spending': required_spending
                }
                transactions.append(transaction)
        
        # Try old format: look for account-specific transaction attributes
        elif attr.name.endswith('_Transaction'):
            # Old format: each category is a separate value
            transaction_values = get_values_by_attribute(db, attr.id)
            for val in transaction_values:
                data_entries = get_data_by_value(db, val.id, limit)
                for data in data_entries:
                    # Parse metadata for old format
                    metadata = {}
                    required_spending = False
                    if data.notes:
                        try:
                            import json
                            metadata = json.loads(data.notes)
                            required_spending = metadata.get("required_spending", False)
                        except:
                            # Old format: notes is just description
                            metadata = {"description": data.notes}
                    
                    transaction = {
                        'id': data.id,
                        'account': attr.name.replace('_Transaction', ''),
                        'category': val.name,
                        'amount': float(data.data_value),
                        'description': metadata.get("description", ""),
                        'date': data.date_recorded,
                        'updated_at': data.updated_at,
                        'required_spending': required_spending
                    }
                    transactions.append(transaction)
    
    # Sort by date (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)
    return transactions[:limit]

def add_transaction(
    db: Session,
    account_name: str,
    amount: float,
    category: str,
    description: str = None,
    date_recorded: datetime = None,
    required_spending: bool = False
) -> Dict[str, Any]:
    """Add a new transaction with support for required spending flag"""
    if date_recorded is None:
        date_recorded = datetime.utcnow()
    
    # Create metadata for the transaction
    import json
    metadata = {
        "category": category,
        "description": description or "",
        "required_spending": required_spending
    }
    
    # Track the transaction
    result = track_data(
        db=db,
        noun_name="Banking",
        attribute_name=account_name,
        value_name="Transactions",
        data_value=amount,
        data_type="number",
        notes=json.dumps(metadata),
        required_spending=required_spending
    )
    
    return {
        'id': result.id,
        'account_name': account_name,
        'amount': amount,
        'category': category,
        'description': description,
        'date_recorded': result.date_recorded,
        'required_spending': required_spending
    }

def update_transaction(db: Session, transaction_id: int, account_name: str, category: str, amount: float, description: str = None, notes: str = None, transaction_date: datetime = None, required_spending: bool = False) -> Dict[str, Any]:
    """Update an existing transaction with required spending flag"""
    try:
        # Get the existing transaction
        db_transaction = db.query(models.Data).filter(models.Data.id == transaction_id).first()
        
        if not db_transaction:
            raise ValueError(f"Transaction with ID {transaction_id} not found")
        
        # Preserve original date if no new date provided
        if transaction_date is None:
            transaction_date = db_transaction.date_recorded
        
        # Get the old amount for balance adjustment
        old_amount = float(db_transaction.data_value)
        
        # Get the current value (category) and attribute (account)
        current_value = db.query(models.Value).filter(models.Value.id == db_transaction.value_id).first()
        if not current_value:
            raise ValueError(f"Value not found for transaction {transaction_id}")
        
        current_attribute = db.query(models.Attribute).filter(models.Attribute.id == current_value.attribute_id).first()
        if not current_attribute:
            raise ValueError(f"Attribute not found for transaction {transaction_id}")
        
        # Check if we need to update the category (value name)
        if current_value.name != category:
            # Find or create the new category value
            new_value = get_value_by_name_and_attribute(db, current_attribute.id, category)
            if not new_value:
                # Create new value for this category
                new_value = create_value(db, {
                    "name": category,
                    "attribute_id": current_attribute.id,
                    "data_type": "number"
                })
            
            # Update the transaction to point to the new value
            db_transaction.value_id = new_value.id
        
        # Create updated metadata
        import json
        metadata = {
            "category": category,
            "description": description or "",
            "required_spending": required_spending
        }
        
        # Update transaction record
        db_transaction.data_value = str(amount)
        db_transaction.notes = json.dumps(metadata)
        # Don't update date_recorded - preserve original transaction date
        # updated_at will be automatically updated by SQLAlchemy
        db.commit()
        db.refresh(db_transaction)
        
        # Adjust account balance (remove old amount, add new amount)
        balance_adjustment = amount - old_amount
        if balance_adjustment != 0:
            update_account_balance(db, account_name, balance_adjustment, f"Transaction update: {category}")
        
        return {
            'id': db_transaction.id,
            'account': account_name,
            'category': category,
            'amount': amount,
            'description': description,
            'notes': notes,
            'date': transaction_date.isoformat(),
            'required_spending': required_spending
        }
    except Exception as e:
        # Rollback the transaction on error
        db.rollback()
        print(f"Error updating transaction {transaction_id}: {str(e)}")
        raise ValueError(f"Failed to update transaction: {str(e)}")

def delete_transaction(db: Session, transaction_id: int) -> bool:
    """Delete a transaction"""
    # Get the existing transaction
    db_transaction = db.query(models.Data).filter(models.Data.id == transaction_id).first()
    
    if not db_transaction:
        raise ValueError(f"Transaction with ID {transaction_id} not found")
    
    # Get the amount for balance adjustment
    old_amount = float(db_transaction.data_value)
    
    # Get account name from the value's attribute
    value_obj = db.query(models.Value).filter(models.Value.id == db_transaction.value_id).first()
    if value_obj:
        attribute_obj = db.query(models.Attribute).filter(models.Attribute.id == value_obj.attribute_id).first()
        if attribute_obj:
            account_name = attribute_obj.name.replace('_Transaction', '')
            category = value_obj.name
            
            # Delete the transaction
            db.delete(db_transaction)
            db.commit()
            
            # Adjust account balance (remove the amount)
            if old_amount != 0:
                update_account_balance(db, account_name, -old_amount, f"Transaction deletion: {category}")
    
    return True

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

def get_networth_history(db: Session) -> Dict[str, Any]:
    """Get net worth history over time"""
    accounts = get_financial_accounts(db)
    
    # Get all balance history for each account
    all_balance_data = {}
    for account in accounts:
        account_name = account['account_name']
        balance_history = get_account_balance_history(db, account_name)
        all_balance_data[account_name] = balance_history
    
    # Combine all balance data by date
    networth_by_date = {}
    
    for account_name, balance_history in all_balance_data.items():
        for entry in balance_history:
            date_key = entry['date'].strftime('%Y-%m-%d')
            if date_key not in networth_by_date:
                networth_by_date[date_key] = {}
            networth_by_date[date_key][account_name] = entry['balance']
    
    # Calculate net worth for each date
    networth_history = []
    for date_str in sorted(networth_by_date.keys()):
        total_networth = sum(networth_by_date[date_str].values())
        networth_history.append({
            'date': date_str,
            'networth': total_networth,
            'accounts': networth_by_date[date_str]
        })
    
    return {
        'networth_history': networth_history,
        'total_accounts': len(accounts),
        'current_networth': get_total_balance(db)
    }

def get_spending_over_time(db: Session) -> Dict[str, Any]:
    """Get spending data over time"""
    # Get all transactions
    all_transactions = get_transactions(db, limit=10000)
    
    # Group transactions by month
    spending_by_month = {}
    
    for transaction in all_transactions:
        if transaction['amount'] < 0:  # Only spending (negative amounts)
            month_key = transaction['date'].strftime('%Y-%m')
            if month_key not in spending_by_month:
                spending_by_month[month_key] = {
                    'total_spending': 0,
                    'transactions': 0,
                    'categories': {}
                }
            
            spending_by_month[month_key]['total_spending'] += abs(transaction['amount'])
            spending_by_month[month_key]['transactions'] += 1
            
            # Track spending by category
            category = transaction['category']
            if category not in spending_by_month[month_key]['categories']:
                spending_by_month[month_key]['categories'][category] = 0
            spending_by_month[month_key]['categories'][category] += abs(transaction['amount'])
    
    # Convert to sorted list
    spending_history = []
    for month in sorted(spending_by_month.keys()):
        spending_history.append({
            'month': month,
            'total_spending': spending_by_month[month]['total_spending'],
            'transactions': spending_by_month[month]['transactions'],
            'categories': spending_by_month[month]['categories']
        })
    
    return {
        'spending_history': spending_history,
        'total_spending': sum(entry['total_spending'] for entry in spending_history)
    }

def get_recent_transactions(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """Get most recent transactions across all accounts"""
    all_transactions = []
    
    # Get transactions from all accounts
    accounts = get_financial_accounts(db)
    for account in accounts:
        account_transactions = get_account_transactions(db, account['account_name'], limit=100)
        all_transactions.extend(account_transactions)
    
    # Sort by date descending and return top N
    all_transactions.sort(key=lambda x: x['date'], reverse=True)
    return all_transactions[:limit]

def get_account_transactions(db: Session, account_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get transactions for a specific account including opening balance"""
    banking_noun = get_noun_by_name(db, "Banking")
    if not banking_noun:
        return []
    
    transactions = []
    
    # Get opening balance transaction
    account_attr = get_attribute_by_name_and_noun(db, banking_noun.id, account_name)
    if account_attr:
        balance_value = get_value_by_name_and_attribute(db, account_attr.id, "Balance")
        if balance_value:
            # Get the earliest balance entry as opening balance
            earliest_balance = db.query(models.Data).filter(
                models.Data.value_id == balance_value.id
            ).order_by(models.Data.date_recorded.asc()).first()
            
            if earliest_balance:
                transactions.append({
                    "id": f"balance_{earliest_balance.id}",
                    "account": account_name,
                    "category": "Opening Balance",
                    "amount": float(earliest_balance.data_value),
                    "date": earliest_balance.date_recorded,
                    "notes": earliest_balance.notes or "Initial account balance",
                    "type": "balance"
                })
    
    # Look for the specific account's transaction attribute
    account_transaction_attr = get_attribute_by_name_and_noun(db, banking_noun.id, f"{account_name}_Transaction")
    
    if account_transaction_attr:
        transaction_values = get_values_by_attribute(db, account_transaction_attr.id)
        for val in transaction_values:
            data_entries = get_data_by_value(db, val.id, limit)
            for data in data_entries:
                # Parse metadata for old format
                metadata = {}
                required_spending = False
                if data.notes:
                    try:
                        import json
                        metadata = json.loads(data.notes)
                        required_spending = metadata.get("required_spending", False)
                    except:
                        # Old format: notes is just description
                        metadata = {"description": data.notes}
                
                transactions.append({
                    "id": data.id,
                    "account": account_name,
                    "category": val.name,
                    "amount": float(data.data_value),
                    "date": data.date_recorded,
                    "updated_at": data.updated_at,
                    "description": metadata.get("description", ""),
                    "required_spending": required_spending,
                    "type": "transaction"
                })
    
    # Also check if there are any transactions from the main get_transactions function
    # that might not be caught by the account-specific lookup
    all_transactions = get_transactions(db, limit=1000)
    account_transactions = [t for t in all_transactions if t["account"] == account_name]
    
    # Merge and deduplicate transactions
    existing_ids = {t["id"] for t in transactions}
    for transaction in account_transactions:
        if transaction["id"] not in existing_ids:
            transactions.append(transaction)
    
    # Sort by date descending
    transactions.sort(key=lambda x: x["date"], reverse=True)
    return transactions[:limit]

def get_account_balance_history(db: Session, account_name: str) -> List[Dict[str, Any]]:
    """Get balance history for a specific account using stored balance snapshots"""
    banking_noun = get_noun_by_name(db, "Banking")
    if not banking_noun:
        return []
    
    balance_history = []
    account_attr = get_attribute_by_name_and_noun(db, banking_noun.id, account_name)
    
    if account_attr:
        balance_value = get_value_by_name_and_attribute(db, account_attr.id, "Balance")
        if balance_value:
            # Get all balance data entries
            data_entries = db.query(models.Data).filter(
                models.Data.value_id == balance_value.id
            ).order_by(models.Data.date_recorded.asc()).all()
            
            for data in data_entries:
                balance_history.append({
                    "date": data.date_recorded,
                    "balance": float(data.data_value),
                    "notes": data.notes
                })
    
    return balance_history

def calculate_and_store_daily_balance(db: Session, account_name: str, target_date: datetime = None) -> Dict[str, Any]:
    """Calculate and store the daily balance for an account based on transactions"""
    if target_date is None:
        target_date = datetime.now()
    
        # Get all transactions up to the target date
    transactions = get_account_transactions(db, account_name, limit=10000)
    
    # Filter transactions up to the target date
    target_date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    target_date_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Convert transaction dates to timezone-naive for comparison
    relevant_transactions = []
    for t in transactions:
        # Convert to timezone-naive datetime for comparison
        transaction_date = t["date"]
        if hasattr(transaction_date, 'tzinfo') and transaction_date.tzinfo is not None:
            transaction_date = transaction_date.replace(tzinfo=None)
        
        if transaction_date <= target_date_end:
            relevant_transactions.append(t)
    
    # Calculate running balance
    running_balance = 0.0
    
    # Get initial balance from the earliest balance update
    banking_noun = get_noun_by_name(db, "Banking")
    if banking_noun:
        account_attr = get_attribute_by_name_and_noun(db, banking_noun.id, account_name)
        if account_attr:
            balance_value = get_value_by_name_and_attribute(db, account_attr.id, "Balance")
            if balance_value:
                earliest_balance = db.query(models.Data).filter(
                    models.Data.value_id == balance_value.id
                ).order_by(models.Data.date_recorded.asc()).first()
                
                if earliest_balance:
                    running_balance = float(earliest_balance.data_value)
    
    # Add all transaction amounts
    for transaction in relevant_transactions:
        running_balance += transaction["amount"]
    
    # If no initial balance was found, start from 0
    if running_balance == 0.0 and relevant_transactions:
        # Start from 0 and add all transactions
        running_balance = sum(t["amount"] for t in relevant_transactions)
    
    # Store the calculated balance
    balance_notes = f"Calculated balance for {target_date.strftime('%Y-%m-%d')} based on {len(relevant_transactions)} transactions"
    
    # Use the existing track_data function to store the balance
    track_data(
        db=db,
        noun_name="Banking",
        attribute_name=account_name,
        value_name="Balance",
        data_value=str(running_balance),
        data_type="number",
        notes=balance_notes
    )
    
    return {
        "account_name": account_name,
        "date": target_date,
        "calculated_balance": running_balance,
        "transactions_count": len(relevant_transactions),
        "notes": balance_notes
    }

def get_account_summary(db: Session, account_name: str) -> Dict[str, Any]:
    """Get summary statistics for a specific account"""
    transactions = get_account_transactions(db, account_name, limit=1000)
    balance_history = get_account_balance_history(db, account_name)
    
    if not transactions:
        return {
            "total_transactions": 0,
            "total_income": 0,
            "total_expenses": 0,
            "net_change": 0,
            "average_transaction": 0,
            "largest_transaction": 0,
            "most_common_category": None,
            "balance_changes": len(balance_history)
        }
    
    # Calculate transaction statistics
    total_transactions = len(transactions)
    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    total_expenses = abs(sum(t["amount"] for t in transactions if t["amount"] < 0))
    net_change = sum(t["amount"] for t in transactions)
    average_transaction = net_change / total_transactions if total_transactions > 0 else 0
    
    # Find largest transaction
    largest_transaction = max(abs(t["amount"]) for t in transactions) if transactions else 0
    
    # Find most common category
    category_counts = {}
    for transaction in transactions:
        category = transaction["category"]
        category_counts[category] = category_counts.get(category, 0) + 1
    
    most_common_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
    
    # Count balance changes (including initial balance and transactions)
    balance_changes = len(balance_history)
    
    return {
        "total_transactions": total_transactions,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_change": net_change,
        "average_transaction": average_transaction,
        "largest_transaction": largest_transaction,
        "most_common_category": most_common_category,
        "balance_changes": balance_changes
    }

def get_finance_categories(db: Session) -> List[Dict[str, Any]]:
    """Get all available finance categories"""
    categories_noun = get_noun_by_name(db, "Finance_Categories")
    if not categories_noun:
        return []
    
    categories = []
    for attr in categories_noun.attributes:
        categories.append({
            "category_group": attr.name,
            "subcategories": [val.name for val in attr.values]
        })
    
    return categories

def setup_finance_categories(db: Session) -> Dict[str, Any]:
    """Set up comprehensive finance categories"""
    categories_data = {
        "Auto & Transport": [
            "Auto Insurance", "Auto Payment", "Gas & Fuel", "Parking", 
            "Public Transportation", "Service & Parts", "Erica Auto Payment", 
            "Erica Gas Fuel", "Erica Parking"
        ],
        "Bills & Utilities": [
            "Gardener", "Home Phone", "Internet", "Mobile Phone", "Television", 
            "Utilities", "Electric", "Gas", "Water and Trash"
        ],
        "Business Services": [
            "Advertising", "Legal", "Office Supplies", "Printing", "Shipping"
        ],
        "Education": [
            "Books & Supplies", "Student Loan", "Tuition"
        ],
        "Entertainment": [
            "Amusement", "Arts", "Movies & DVDs", "Music", "Newspapers & Magazines"
        ],
        "Fees & Charges": [
            "ATM Fee", "Credit Union Fee", "Finance Charge", "Late Fee", 
            "Service Fee", "Trade Commissions"
        ],
        "Financial": [
            "Financial Advisor", "Life Insurance"
        ],
        "Food & Dining": [
            "Alcohol & Bars", "Coffee Shops", "Fast Food", "Groceries", "Restaurants"
        ],
        "Gifts & Donations": [
            "Charity", "Gift"
        ],
        "Health & Fitness": [
            "Dentist", "Doctor", "Eyecare", "Gym", "Health Insurance", 
            "Pharmacy", "Sports"
        ],
        "Home": [
            "Furnishings", "Home Improvement", "Home Insurance", "Home Services", 
            "Home Supplies", "Lawn & Garden", "Mortgage & Rent"
        ],
        "Kids": [
            "Allowance", "Baby Supplies", "Babysitter & Daycare", "Child Support", 
            "Kids Activities", "Toys", "Clothing"
        ],
        "Personal Care": [
            "Hair", "Laundry", "Nail Salon", "Spa & Massage"
        ],
        "Pets": [
            "Pet Food & Supplies", "Pet Grooming", "Veterinary"
        ],
        "Shopping": [
            "Books", "Clothing", "Electronics & Software", "Hobbies", "Sporting Goods"
        ],
        "Taxes": [
            "Federal Tax", "Local Tax", "Property Tax", "Sales Tax", "State Tax"
        ],
        "Transfer": [
            "Credit Card Payment", "Transfer for Cash Spending"
        ],
        "Travel": [
            "Air Travel", "Car Rental & Taxi", "Hotel", "Vacation"
        ],
        "Uncategorized": [
            "Cash & ATM", "Check"
        ]
    }
    
    # Create the main categories noun
    categories_noun = get_noun_by_name(db, "Finance_Categories")
    if not categories_noun:
        categories_noun = create_noun(db, schemas.NounCreate(
            name="Finance_Categories",
            description="Comprehensive finance categories for tracking expenses and income"
        ))
    
    categories_created = {}
    
    # Create each category group and its subcategories
    for category_group, subcategories in categories_data.items():
        # Create the category group attribute
        category_attr = get_attribute_by_name_and_noun(db, categories_noun.id, category_group)
        if not category_attr:
            category_attr = create_attribute(db, schemas.AttributeCreate(
                noun_id=categories_noun.id,
                name=category_group,
                description=f"Category group for {category_group}"
            ))
        
        categories_created[category_group] = []
        
        # Create each subcategory
        for subcategory in subcategories:
            subcategory_value = get_value_by_name_and_attribute(db, category_attr.id, subcategory)
            if not subcategory_value:
                subcategory_value = create_value(db, schemas.ValueCreate(
                    attribute_id=category_attr.id,
                    name=subcategory,
                    data_type="string",
                    description=f"Subcategory: {subcategory}"
                ))
                categories_created[category_group].append(subcategory)
    
    return {
        "total_groups": len(categories_created),
        "total_subcategories": sum(len(subcats) for subcats in categories_created.values()),
        "categories": categories_created
    } 