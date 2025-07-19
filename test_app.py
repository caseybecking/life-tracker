#!/usr/bin/env python3
"""
Life Tracker - Test Script

This script tests the basic functionality of the Life Tracker application.
"""

import requests
import time
import subprocess
import sys
import os

def test_server_startup():
    """Test if the server can start and respond"""
    print("Testing server startup...")
    
    try:
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", "127.0.0.1", "--port", "8000"
        ])
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if response.status_code == 200:
            print("✓ Server started successfully")
            return server_process
        else:
            print("✗ Server health check failed")
            server_process.terminate()
            return None
            
    except Exception as e:
        print(f"✗ Server startup failed: {e}")
        return None

def test_api_endpoints(server_process):
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    tests = [
        ("GET /health", "http://127.0.0.1:8000/health"),
        ("GET /finance/summary", "http://127.0.0.1:8000/finance/summary"),
        ("GET /finance/accounts", "http://127.0.0.1:8000/finance/accounts"),
        ("GET /track/nouns", "http://127.0.0.1:8000/track/nouns"),
    ]
    
    passed = 0
    for test_name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {test_name}")
                passed += 1
            else:
                print(f"✗ {test_name} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {test_name} - Error: {e}")
    
    print(f"\nAPI Tests: {passed}/{len(tests)} passed")
    return passed == len(tests)

def test_example_data_setup(server_process):
    """Test example data setup"""
    print("\nTesting example data setup...")
    
    try:
        # Setup financial example data
        response = requests.post("http://127.0.0.1:8000/finance/setup/example-data", timeout=10)
        if response.status_code == 200:
            print("✓ Financial example data setup")
        else:
            print("✗ Financial example data setup failed")
            return False
        
        # Setup general tracking example data
        response = requests.post("http://127.0.0.1:8000/track/setup/example-data", timeout=10)
        if response.status_code == 200:
            print("✓ General tracking example data setup")
        else:
            print("✗ General tracking example data setup failed")
            return False
        
        # Test that data was created
        response = requests.get("http://127.0.0.1:8000/finance/summary", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("total_balance", 0) > 0:
                print("✓ Example data verified")
                return True
            else:
                print("✗ Example data not found")
                return False
        else:
            print("✗ Could not verify example data")
            return False
            
    except Exception as e:
        print(f"✗ Example data setup failed: {e}")
        return False

def test_frontend_pages(server_process):
    """Test frontend pages"""
    print("\nTesting frontend pages...")
    
    pages = [
        ("Home page", "http://127.0.0.1:8000/"),
        ("Finance page", "http://127.0.0.1:8000/finance"),
        ("Track page", "http://127.0.0.1:8000/track"),
    ]
    
    passed = 0
    for page_name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and "Life Tracker" in response.text:
                print(f"✓ {page_name}")
                passed += 1
            else:
                print(f"✗ {page_name} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {page_name} - Error: {e}")
    
    print(f"\nFrontend Tests: {passed}/{len(pages)} passed")
    return passed == len(pages)

def main():
    """Main test function"""
    print("🧪 Life Tracker Test Suite")
    print("=" * 50)
    
    # Test server startup
    server_process = test_server_startup()
    if not server_process:
        print("\n❌ Tests failed at server startup")
        sys.exit(1)
    
    try:
        # Test API endpoints
        api_success = test_api_endpoints(server_process)
        
        # Test example data setup
        data_success = test_example_data_setup(server_process)
        
        # Test frontend pages
        frontend_success = test_frontend_pages(server_process)
        
        # Summary
        print("\n" + "=" * 50)
        print("Test Results:")
        print(f"API Endpoints: {'✓ PASS' if api_success else '✗ FAIL'}")
        print(f"Example Data: {'✓ PASS' if data_success else '✗ FAIL'}")
        print(f"Frontend Pages: {'✓ PASS' if frontend_success else '✗ FAIL'}")
        
        if api_success and data_success and frontend_success:
            print("\n🎉 All tests passed! Life Tracker is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the application setup.")
            
    finally:
        # Clean up
        if server_process:
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main() 