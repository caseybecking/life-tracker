#!/usr/bin/env python3
"""
Life Tracker CLI Commands

This script provides command-line tools for managing the Life Tracker application.
"""

import click
import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from app import models

@click.group()
def cli():
    """Life Tracker CLI - Manage your life tracking data"""
    pass

@cli.command("clear-finance-data")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def clear_finance_data(confirm):
    """Clear all finance data from the database"""
    
    print("=" * 60)
    print("CLEAR FINANCE DATA")
    print("=" * 60)
    print()
    print("WARNING: This will permanently delete all financial data!")
    print("This includes:")
    print("- All financial accounts")
    print("- All transactions")
    print("- All balance history")
    print("- All financial categories")
    print()
    
    if not confirm:
        confirm_input = input("Are you sure you want to continue? Type 'YES' to confirm: ")
        if confirm_input != "YES":
            print("Operation cancelled.")
            return
    
    print()
    print("Starting data cleanup...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Clear all financial transactions
        print("1. Clearing transactions...")
        transaction_count = db.query(models.Data).filter(
            models.Data.value_id.in_(
                db.query(models.Value.id).filter(
                    models.Value.attribute_id.in_(
                        db.query(models.Attribute.id).filter(
                            models.Attribute.noun_id == db.query(models.Noun.id).filter(
                                models.Noun.name == "Banking"
                            ).scalar()
                        )
                    )
                )
            )
        ).count()
        
        db.query(models.Data).filter(
            models.Data.value_id.in_(
                db.query(models.Value.id).filter(
                    models.Value.attribute_id.in_(
                        db.query(models.Attribute.id).filter(
                            models.Attribute.noun_id == db.query(models.Noun.id).filter(
                                models.Noun.name == "Banking"
                            ).scalar()
                        )
                    )
                )
            )
        ).delete()
        
        print(f"   - Deleted {transaction_count} transactions")
        
        # 2. Clear all financial values (categories, balances, etc.)
        print("2. Clearing financial values...")
        value_count = db.query(models.Value).filter(
            models.Value.attribute_id.in_(
                db.query(models.Attribute.id).filter(
                    models.Attribute.noun_id == db.query(models.Noun.id).filter(
                        models.Noun.name == "Banking"
                    ).scalar()
                )
            )
        ).count()
        
        db.query(models.Value).filter(
            models.Value.attribute_id.in_(
                db.query(models.Attribute.id).filter(
                    models.Attribute.noun_id == db.query(models.Noun.id).filter(
                        models.Noun.name == "Banking"
                    ).scalar()
                )
            )
        ).delete()
        
        print(f"   - Deleted {value_count} financial values")
        
        # 3. Clear all financial attributes (accounts, etc.)
        print("3. Clearing financial attributes...")
        attribute_count = db.query(models.Attribute).filter(
            models.Attribute.noun_id == db.query(models.Noun.id).filter(
                models.Noun.name == "Banking"
            ).scalar()
        ).count()
        
        db.query(models.Attribute).filter(
            models.Attribute.noun_id == db.query(models.Noun.id).filter(
                models.Noun.name == "Banking"
            ).scalar()
        ).delete()
        
        print(f"   - Deleted {attribute_count} financial attributes")
        
        # 4. Clear finance categories
        print("4. Clearing finance categories...")
        finance_categories_noun = db.query(models.Noun).filter(models.Noun.name == "Finance_Categories").first()
        category_value_count = 0
        category_attribute_count = 0
        
        if finance_categories_noun:
            # Delete all values in finance categories
            category_value_count = db.query(models.Value).filter(
                models.Value.attribute_id.in_(
                    db.query(models.Attribute.id).filter(
                        models.Attribute.noun_id == finance_categories_noun.id
                    )
                )
            ).count()
            
            db.query(models.Value).filter(
                models.Value.attribute_id.in_(
                    db.query(models.Attribute.id).filter(
                        models.Attribute.noun_id == finance_categories_noun.id
                    )
                )
            ).delete()
            
            # Delete all attributes in finance categories
            category_attribute_count = db.query(models.Attribute).filter(
                models.Attribute.noun_id == finance_categories_noun.id
            ).count()
            
            db.query(models.Attribute).filter(
                models.Attribute.noun_id == finance_categories_noun.id
            ).delete()
            
            # Delete the finance categories noun itself
            db.delete(finance_categories_noun)
            
            print(f"   - Deleted {category_value_count} category values")
            print(f"   - Deleted {category_attribute_count} category attributes")
            print("   - Deleted Finance_Categories noun")
        
        # 5. Clear the Banking noun (this will remove all remaining financial data)
        print("5. Clearing Banking noun...")
        banking_noun = db.query(models.Noun).filter(models.Noun.name == "Banking").first()
        if banking_noun:
            db.delete(banking_noun)
            print("   - Deleted Banking noun")
        
        # Commit all changes
        db.commit()
        
        print()
        print("=" * 60)
        print("FINANCE DATA CLEARED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Summary of deleted data:")
        print(f"- {transaction_count} transactions")
        print(f"- {value_count} financial values")
        print(f"- {attribute_count} financial attributes")
        if finance_categories_noun:
            print(f"- {category_value_count} category values")
            print(f"- {category_attribute_count} category attributes")
        print("- All financial nouns (Banking, Finance_Categories)")
        print()
        print("The database is now clean and ready for fresh data.")
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        db.rollback()
        print("Changes have been rolled back.")
        return
    
    finally:
        db.close()

@cli.command("finance-status")
def finance_status():
    """Check the status of finance data in the database"""
    
    print("=" * 60)
    print("FINANCE DATA STATUS")
    print("=" * 60)
    print()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check for financial data
        banking_noun = db.query(models.Noun).filter(models.Noun.name == "Banking").first()
        finance_categories_noun = db.query(models.Noun).filter(models.Noun.name == "Finance_Categories").first()
        
        # Count remaining data
        transaction_count = 0
        account_count = 0
        
        if banking_noun:
            transaction_count = db.query(models.Data).filter(
                models.Data.value_id.in_(
                    db.query(models.Value.id).filter(
                        models.Value.attribute_id.in_(
                            db.query(models.Attribute.id).filter(
                                models.Attribute.noun_id == banking_noun.id
                            )
                        )
                    )
                )
            ).count()
            
            account_count = db.query(models.Attribute).filter(
                models.Attribute.noun_id == banking_noun.id
            ).count()
        
        print("Current Finance Data:")
        print(f"- Banking noun exists: {'Yes' if banking_noun else 'No'}")
        print(f"- Finance categories exist: {'Yes' if finance_categories_noun else 'No'}")
        print(f"- Number of accounts: {account_count}")
        print(f"- Number of transactions: {transaction_count}")
        print()
        
        if banking_noun or finance_categories_noun:
            print("✅ Finance data found in database")
        else:
            print("📭 No finance data found in database")
            
    except Exception as e:
        print(f"Error checking status: {str(e)}")
    finally:
        db.close()

@cli.command("setup-example-data")
def setup_example_data():
    """Set up example finance data"""
    
    print("=" * 60)
    print("SETUP EXAMPLE DATA")
    print("=" * 60)
    print()
    
    # Get database session
    db = next(get_db())
    
    try:
        from app import crud
        
        print("Setting up example finance data...")
        
        # Setup categories
        categories_result = crud.setup_finance_categories(db)
        print(f"✅ Created {categories_result['total_groups']} category groups with {categories_result['total_subcategories']} subcategories")
        
        # Add some example accounts
        example_accounts = [
            {"name": "Main Checking", "balance": 5000, "institution": "Bank of America", "type": "checking"},
            {"name": "Savings", "balance": 15000, "institution": "Bank of America", "type": "savings"},
            {"name": "Credit Card", "balance": -2500, "institution": "Chase", "type": "credit"}
        ]
        
        for account in example_accounts:
            crud.add_account(db, account["name"], account["balance"], account["institution"], account["type"])
        
        print(f"✅ Created {len(example_accounts)} example accounts")
        print()
        print("Example data setup complete!")
        print("You can now visit the finance pages to see the example data.")
        
    except Exception as e:
        print(f"Error setting up example data: {str(e)}")
    finally:
        db.close()

@cli.command("setup-categories")
def setup_categories():
    """Set up finance categories only (no accounts or transactions)"""
    
    print("=" * 60)
    print("SETUP FINANCE CATEGORIES")
    print("=" * 60)
    print()
    
    # Get database session
    db = next(get_db())
    
    try:
        from app import crud
        
        print("Setting up finance categories...")
        
        # Setup categories only
        categories_result = crud.setup_finance_categories(db)
        print(f"✅ Created {categories_result['total_groups']} category groups")
        print(f"✅ Created {categories_result['total_subcategories']} subcategories")
        print()
        print("Categories setup complete!")
        print("You can now add accounts and transactions with proper categorization.")
        
    except Exception as e:
        print(f"Error setting up categories: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    cli() 