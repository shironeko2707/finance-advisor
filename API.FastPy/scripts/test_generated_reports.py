"""
Test script for new generated reports endpoints
Run this after starting the FastAPI server
"""
import requests
import json
import os

BASE_URL = "http://localhost:8001"

def get_auth_token():
    """Get authentication token for testing"""
    # You may need to adjust this based on your auth system
    login_data = {
        "username": "admin@example.com",  # Replace with actual test user
        "password": "admin123"            # Replace with actual test password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_new_endpoints(token):
    """Test the new generated reports endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing new endpoints...")
    print("=" * 50)
    
    # Test 1: List generated reports
    print("1. Testing GET /files/generated/reports")
    try:
        response = requests.get(f"{BASE_URL}/files/generated/reports", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Reports found: {data.get('total', 0)}")
            if data.get('reports'):
                print(f"   First report ID: {data['reports'][0]['id']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Check if sync endpoint exists
    print("\n2. Testing POST /files/upload/with-template-sync (check availability)")
    try:
        # Just check if endpoint exists in OpenAPI
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            if "/files/upload/with-template-sync" in openapi_spec.get("paths", {}):
                print("   ✅ Sync endpoint found in API spec")
            else:
                print("   ❌ Sync endpoint not found in API spec")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: List old generated files (file system)
    print("\n3. Testing GET /files/generated (file system)")
    try:
        response = requests.get(f"{BASE_URL}/files/generated", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Files found: {data.get('total', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

def test_server_running():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🧪 Testing Generated Reports Features")
    print("=" * 60)
    
    if not test_server_running():
        print("❌ Server is not running on http://localhost:8001")
        print("Please start the server first:")
        print("  1. Set IS_PRODUCTION=false")
        print("  2. Run: python main.py")
        exit(1)
    
    print("✅ Server is running")
    
    # Test without auth first
    print("\n📡 Testing endpoints without authentication...")
    
    # Check OpenAPI spec
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            file_endpoints = [path for path in paths if "/files/" in path]
            print(f"File endpoints found: {len(file_endpoints)}")
            
            new_endpoints = [
                "/files/upload/with-template-sync",
                "/files/generated/reports",
                "/files/generated/reports/{report_id}",
                "/files/generated/reports/{report_id}/download"
            ]
            
            for endpoint in new_endpoints:
                if endpoint in paths:
                    methods = list(paths[endpoint].keys())
                    print(f"✅ {endpoint} [{', '.join(methods).upper()}]")
                else:
                    print(f"❌ {endpoint} [MISSING]")
    except Exception as e:
        print(f"❌ Error checking API spec: {e}")
    
    print("\n📝 Next steps:")
    print("1. Create a test user or use existing credentials")
    print("2. Use /files/upload/with-template-sync to generate a report")
    print("3. Check /files/generated/reports to see tracked reports")
    print("4. Use /files/generated/reports/{id}/download to download")
    
    print(f"\n🌐 API Documentation: {BASE_URL}/docs")
