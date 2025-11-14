#!/usr/bin/env python3
"""
Test script for authentication endpoints.
This script tests the login functionality and token validation.
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Test the login endpoint"""
    print("🧪 Testing Authentication...")
    print("-" * 50)
    
    # Test login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("1. Testing login endpoint...")
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            print("✅ Login successful!")
            print(f"   Token Type: {login_result['token_type']}")
            print(f"   Expires in: {login_result['expires_in']} seconds ({login_result['expires_in']//3600} hours)")
            print(f"   User ID: {login_result['user_id']}")
            print(f"   Username: {login_result['username']}")
            print(f"   Role: {login_result['role']}")
            
            token = login_result['access_token']
            print(f"   Token (first 50 chars): {token[:50]}...")
            
            # Test authenticated request
            print("\n2. Testing authenticated request...")
            headers = {"Authorization": f"Bearer {token}"}
            users_response = requests.get(f"{BASE_URL}/users/", headers=headers)
            
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"✅ Authenticated request successful! Found {len(users)} users.")
            else:
                print(f"❌ Authenticated request failed: {users_response.status_code}")
                print(f"   Error: {users_response.text}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_invalid_credentials():
    """Test login with invalid credentials"""
    print("\n3. Testing invalid credentials...")
    
    invalid_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=invalid_data)
        
        if response.status_code == 401:
            print("✅ Invalid credentials correctly rejected")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            
    except requests.ConnectionError:
        print("❌ Could not connect to the API")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    print("\n4. Testing unauthorized access...")
    
    try:
        response = requests.get(f"{BASE_URL}/users/")
        
        if response.status_code == 401:
            print("✅ Unauthorized access correctly blocked")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            
    except requests.ConnectionError:
        print("❌ Could not connect to the API")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_login()
    test_invalid_credentials()
    test_unauthorized_access()
    print("\n" + "=" * 50)
    print("🏁 Authentication tests completed!")
