#!/usr/bin/env python3
"""
Clear Finance Data Script

This script allows you to clear all financial data from the database including:
- All financial accounts
- All transactions
- All balance history
- All financial categories

WARNING: This will permanently delete all financial data!
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from app import models, crud

def clear_finance_data():
    """Clear all finance-related data from the database"""
    
    print("=" * 60)
    print("CLEAR FINANCE DATA SCRIPT")
    print("=" * 60)
    print()
    print("WARNING: This will permanently delete all financial data!")
    print("This includes:")
    print("- All financial accounts")
    print("- All transactions")
    print("- All balance history")
    print("- All financial categories")
    print()
    
    # Get confirmation from user
    confirm = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    if confirm != "YES":
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

def verify_cleanup():
    """Verify that all finance data has been cleared"""
    print()
    print("Verifying cleanup...")
    
    db = next(get_db())
    
    try:
        # Check for remaining financial data
        banking_noun = db.query(models.Noun).filter(models.Noun.name == "Banking").first()
        finance_categories_noun = db.query(models.Noun).filter(models.Noun.name == "Finance_Categories").first()
        
        if banking_noun:
            print("❌ Banking noun still exists")
        else:
            print("✅ Banking noun cleared")
            
        if finance_categories_noun:
            print("❌ Finance_Categories noun still exists")
        else:
            print("✅ Finance_Categories noun cleared")
        
        # Check for any remaining financial data
        remaining_data = db.query(models.Data).filter(
            models.Data.value_id.in_(
                db.query(models.Value.id).join(models.Attribute).join(models.Noun).filter(
                    models.Noun.name.in_(["Banking", "Finance_Categories"])
                )
            )
        ).count()
        
        if remaining_data > 0:
            print(f"❌ {remaining_data} financial data records still exist")
        else:
            print("✅ All financial data cleared")
            
    except Exception as e:
        print(f"Error during verification: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Finance Data Clear Script")
    print("This script will permanently delete all financial data from the database.")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("Error: Please run this script from the project root directory.")
        sys.exit(1)
    
    # Run the cleanup
    clear_finance_data()
    
    # Verify the cleanup
    verify_cleanup()
    
    print()
    print("Script completed.") 