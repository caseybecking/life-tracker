#!/usr/bin/env python3
"""
Test script to set up and verify finance categories
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_categories_setup():
    """Test the finance categories setup"""
    print("🧪 Testing Finance Categories Setup")
    print("=" * 50)
    
    # Test 1: Set up categories
    print("\n1. Setting up finance categories...")
    try:
        response = requests.post(f"{BASE_URL}/finance/setup/categories")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Categories created successfully!")
            print(f"   - Total groups: {result['categories_created']['total_groups']}")
            print(f"   - Total subcategories: {result['categories_created']['total_subcategories']}")
            print(f"   - Categories: {list(result['categories_created']['categories'].keys())}")
        else:
            print(f"❌ Failed to create categories: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating categories: {e}")
        return False
    
    # Test 2: Get categories
    print("\n2. Retrieving finance categories...")
    try:
        response = requests.get(f"{BASE_URL}/finance/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Retrieved {len(categories)} category groups:")
            for group in categories:
                print(f"   - {group['category_group']}: {len(group['subcategories'])} subcategories")
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting categories: {e}")
        return False
    
    # Test 3: Add some example transactions with new categories
    print("\n3. Testing transactions with new categories...")
    test_transactions = [
        {"account": "SF_Checking", "category": "Groceries", "amount": -85.50, "description": "Weekly groceries"},
        {"account": "SF_Checking", "category": "Gas & Fuel", "amount": -52.30, "description": "Car fuel"},
        {"account": "SF_Checking", "category": "Restaurants", "amount": -45.00, "description": "Dinner out"},
        {"account": "SF_Checking", "category": "Auto Payment", "amount": -350.00, "description": "Car payment"},
        {"account": "SF_Checking", "category": "Internet", "amount": -89.99, "description": "Monthly internet"},
        {"account": "SF_Checking", "category": "Gym", "amount": -29.99, "description": "Monthly gym membership"},
        {"account": "SF_Checking", "category": "Coffee Shops", "amount": -12.50, "description": "Coffee and snacks"},
        {"account": "SF_Checking", "category": "Movies & DVDs", "amount": -18.00, "description": "Movie tickets"},
        {"account": "SF_Checking", "category": "Home Improvement", "amount": -125.00, "description": "Home depot supplies"},
        {"account": "SF_Checking", "category": "Income", "amount": 2500.00, "description": "Salary deposit"}
    ]
    
    for i, transaction in enumerate(test_transactions, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/finance/transactions",
                params={
                    "account_name": transaction["account"],
                    "category": transaction["category"],
                    "amount": transaction["amount"],
                    "description": transaction["description"],
                    "notes": f"Test transaction {i}"
                }
            )
            if response.status_code == 200:
                print(f"   ✅ Added transaction: {transaction['category']} - ${transaction['amount']:.2f}")
            else:
                print(f"   ❌ Failed to add transaction {transaction['category']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error adding transaction {transaction['category']}: {e}")
    
    # Test 4: Get financial summary
    print("\n4. Getting financial summary...")
    try:
        response = requests.get(f"{BASE_URL}/finance/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Financial summary retrieved:")
            print(f"   - Total balance: ${summary['total_balance']:.2f}")
            print(f"   - Accounts: {len(summary['accounts'])}")
            print(f"   - Recent transactions: {len(summary['recent_transactions'])}")
        else:
            print(f"❌ Failed to get summary: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Finance categories test completed!")
    return True

if __name__ == "__main__":
    test_categories_setup() 