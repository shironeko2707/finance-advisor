#!/usr/bin/env python3
"""
Comprehensive test of all authentication and user management functionality.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

def test_complete_flow():
    print("🧪 Complete API Test")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1. Testing login...")
    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    
    token_data = login_response.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Login successful! Token expires in {token_data['expires_in']} seconds")
    
    # Step 2: List existing users
    print("\n2. Getting existing users...")
    users_response = client.get("/users/", headers=headers)
    assert users_response.status_code == 200, f"Get users failed: {users_response.json()}"
    
    users = users_response.json()
    print(f"✅ Found {len(users)} existing users")
    
    # Step 3: Create a new user
    print("\n3. Creating a new test user...")
    new_user = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "job_title": "QA Engineer",
        "role": "User",
        "status": "Active"
    }
    
    create_response = client.post("/users/", json=new_user, headers=headers)
    assert create_response.status_code == 201, f"Create user failed: {create_response.json()}"
    
    created_user = create_response.json()
    user_id = created_user["id"]
    print(f"✅ Created user with ID: {user_id}")
    
    # Step 4: Get the created user
    print(f"\n4. Getting user {user_id}...")
    get_user_response = client.get(f"/users/{user_id}", headers=headers)
    assert get_user_response.status_code == 200, f"Get user failed: {get_user_response.json()}"
    
    user_details = get_user_response.json()
    print(f"✅ Retrieved user: {user_details['username']} ({user_details['email']})")
    
    # Step 5: Update the user
    print(f"\n5. Updating user {user_id}...")
    update_data = {
        "job_title": "Senior QA Engineer",
        "first_name": "Updated Test"
    }
    
    update_response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200, f"Update user failed: {update_response.json()}"
    
    updated_user = update_response.json()
    print(f"✅ Updated user job title to: {updated_user['job_title']}")
    
    # Step 6: Search for users
    print("\n6. Searching for users...")
    search_response = client.get("/users/?search=test", headers=headers)
    assert search_response.status_code == 200, f"Search failed: {search_response.json()}"
    
    search_results = search_response.json()
    print(f"✅ Search found {len(search_results)} users matching 'test'")
    
    # Step 7: Test unauthorized access
    print("\n7. Testing unauthorized access...")
    no_auth_response = client.get("/users/")
    assert no_auth_response.status_code == 403, f"Expected 403, got {no_auth_response.status_code}"
    print("✅ Unauthorized access properly blocked")
    
    # Step 8: Delete the test user
    print(f"\n8. Deleting test user {user_id}...")
    delete_response = client.delete(f"/users/{user_id}", headers=headers)
    assert delete_response.status_code == 204, f"Delete failed: status {delete_response.status_code}, text: {delete_response.text}"
    print("✅ Test user deleted successfully")
    
    # Step 9: Verify user was deleted
    print(f"\n9. Verifying user {user_id} was deleted...")
    get_deleted_response = client.get(f"/users/{user_id}", headers=headers)
    assert get_deleted_response.status_code == 404, f"Expected 404, got {get_deleted_response.status_code}"
    print("✅ Confirmed user was deleted")
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Authentication and user management working perfectly!")

if __name__ == "__main__":
    test_complete_flow()
