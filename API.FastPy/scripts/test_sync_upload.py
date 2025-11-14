"""
Test script for sync upload with template endpoint
"""
import requests
import os

# API configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin@example.com"
PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(login_url, data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_sync_upload_with_template():
    """Test the new sync upload with template endpoint"""
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Create test files (you should replace these with actual file paths)
    test_files_dir = "storage/uploads"  # Use existing uploaded files or create test files
    
    # Find some test files
    template_file = None
    document_files = []
    
    if os.path.exists(test_files_dir):
        for filename in os.listdir(test_files_dir):
            file_path = os.path.join(test_files_dir, filename)
            if os.path.isfile(file_path):
                if filename.lower().endswith('.xlsx') and not template_file:
                    template_file = file_path
                elif filename.lower().endswith(('.pdf', '.xlsx')) and len(document_files) < 2:
                    document_files.append(file_path)
    
    if not template_file:
        print("No template file (.xlsx) found in storage/uploads")
        print("Please upload some files first using the regular upload endpoints")
        return
    
    if not document_files:
        print("No document files (.pdf or .xlsx) found in storage/uploads")
        print("Please upload some files first using the regular upload endpoints")
        return
    
    print(f"Using template: {template_file}")
    print(f"Using documents: {document_files}")
    
    # Prepare files for upload
    files = []
    
    # Add template file
    with open(template_file, 'rb') as f:
        template_content = f.read()
    files.append(('template', (os.path.basename(template_file), template_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')))
    
    # Add document files
    for doc_file in document_files:
        with open(doc_file, 'rb') as f:
            doc_content = f.read()
        
        content_type = 'application/pdf' if doc_file.lower().endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        files.append(('files', (os.path.basename(doc_file), doc_content, content_type)))
    
    # Call the sync endpoint
    upload_url = f"{BASE_URL}/files/upload/with-template-sync"
    
    print(f"\nCalling {upload_url}")
    print("This may take a while as it calls the external API...")
    
    try:
        response = requests.post(upload_url, headers=headers, files=files, timeout=300)  # 5 minute timeout
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text}")
        
        if response.status_code == 200:
            print("\n✅ Sync upload with template successful!")
            
            # Check if generated file was created
            generated_files_url = f"{BASE_URL}/files/generated"
            gen_response = requests.get(generated_files_url, headers=headers)
            
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                print(f"\nGenerated files count: {gen_data.get('total', 0)}")
                if gen_data.get('generated_files'):
                    latest_file = gen_data['generated_files'][0]
                    print(f"Latest generated file: {latest_file['filename']}")
                    print(f"File size: {latest_file['file_size']} bytes")
                    print(f"Created at: {latest_file['created_at']}")
        else:
            print(f"\n❌ Upload failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out (this is normal for large files or slow external API)")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_list_generated_files():
    """Test listing generated files"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/files/generated", headers=headers)
    
    print(f"\nGenerated files list:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total files: {data.get('total', 0)}")
        for file_info in data.get('generated_files', []):
            print(f"  - {file_info['filename']} ({file_info['file_size']} bytes)")

if __name__ == "__main__":
    print("🧪 Testing Sync Upload with Template Endpoint")
    print("=" * 50)
    
    # Test sync upload
    test_sync_upload_with_template()
    
    print("\n" + "=" * 50)
    
    # Test listing generated files
    test_list_generated_files()
