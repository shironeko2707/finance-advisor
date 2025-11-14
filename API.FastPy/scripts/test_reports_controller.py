"""
Test script for new generated reports controller
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_generated_reports_endpoints():
    """Test the new generated reports endpoints"""
    print("🧪 Testing Generated Reports Controller")
    print("=" * 60)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    print("✅ Server is running")
    
    # Check OpenAPI spec for new endpoints
    print("\n📡 Checking API endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            # New dedicated report endpoints
            report_endpoints = [
                ("/reports/", "GET"),
                ("/reports/{report_id}", "GET"),
                ("/reports/{report_id}/download", "GET"),
                ("/reports/{report_id}/name", "PUT"),
                ("/reports/{report_id}", "DELETE")
            ]
            
            print("New /reports/* endpoints:")
            for endpoint, expected_method in report_endpoints:
                if endpoint in paths:
                    methods = list(paths[endpoint].keys())
                    if expected_method.lower() in methods:
                        print(f"✅ {expected_method} {endpoint}")
                    else:
                        print(f"⚠️  {endpoint} exists but missing {expected_method} method")
                        print(f"    Available methods: {', '.join(methods).upper()}")
                else:
                    print(f"❌ {endpoint} [MISSING]")
            
            # Existing file endpoints (should still work)
            print("\nExisting /files/* endpoints:")
            file_endpoints = [
                "/files/upload/with-template-sync",
                "/files/generated/reports",
                "/files/generated/reports/{report_id}",
                "/files/generated/reports/{report_id}/download"
            ]
            
            for endpoint in file_endpoints:
                if endpoint in paths:
                    methods = list(paths[endpoint].keys())
                    print(f"✅ {endpoint} [{', '.join(methods).upper()}]")
                else:
                    print(f"❌ {endpoint} [MISSING]")
            
            # Summary
            total_report_endpoints = len([p for p in paths if p.startswith("/reports/")])
            total_file_endpoints = len([p for p in paths if p.startswith("/files/")])
            
            print(f"\n📊 Summary:")
            print(f"  /reports/* endpoints: {total_report_endpoints}")
            print(f"  /files/* endpoints: {total_file_endpoints}")
            print(f"  Total API endpoints: {len(paths)}")
            
    except Exception as e:
        print(f"❌ Error checking API spec: {e}")
    
    print(f"\n🌐 API Documentation: {BASE_URL}/docs")
    print("\n📝 Usage Examples:")
    print("# List all reports")
    print(f"curl -X GET '{BASE_URL}/reports/' -H 'Authorization: Bearer <token>'")
    print("\n# Get report details")
    print(f"curl -X GET '{BASE_URL}/reports/1' -H 'Authorization: Bearer <token>'")
    print("\n# Update report name")
    print(f"curl -X PUT '{BASE_URL}/reports/1/name' -H 'Authorization: Bearer <token>' -H 'Content-Type: application/json' -d '{{\"name\": \"My Custom Report\"}}'")
    print("\n# Download report")
    print(f"curl -X GET '{BASE_URL}/reports/1/download' -H 'Authorization: Bearer <token>' --output report.pdf")

if __name__ == "__main__":
    test_generated_reports_endpoints()
