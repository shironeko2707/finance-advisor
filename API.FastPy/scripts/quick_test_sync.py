"""
Quick test script to check if the new endpoint is working
Run this after starting the FastAPI server
"""
import requests
import json

# Test the async endpoint first (should work)
def test_async_endpoint():
    print("Testing existing async endpoint...")
    # This is just to check if server is running
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print("❌ Server not responding")
            return False
    except:
        print("❌ Cannot connect to server")
        return False

# Test if the new endpoint exists
def test_sync_endpoint_exists():
    print("Checking if sync endpoint exists...")
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            if "/files/upload/with-template-sync" in paths:
                print("✅ Sync endpoint found in OpenAPI spec")
                return True
            else:
                print("❌ Sync endpoint not found in OpenAPI spec")
                print("Available file endpoints:")
                for path in paths:
                    if "/files/" in path:
                        print(f"  - {path}")
                return False
    except Exception as e:
        print(f"❌ Error checking OpenAPI spec: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Quick Health Check for New Sync Endpoint")
    print("=" * 50)
    
    # Check if server is running
    if test_async_endpoint():
        # Check if new endpoint is available
        test_sync_endpoint_exists()
        
        print("\n📝 To test the endpoint manually:")
        print("1. Start the server: python main.py")
        print("2. Go to: http://localhost:8000/docs")
        print("3. Look for: POST /files/upload/with-template-sync")
        print("4. Use the test script: python scripts/test_sync_upload.py")
    
    print("\n🌐 External API target: http://4.194.234.149:8000/generate-report")
