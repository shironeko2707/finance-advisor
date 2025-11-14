"""
Demo script to test file upload APIs
"""
import requests
import json
import os
from io import BytesIO
import zipfile

# API base URL  
BASE_URL = "http://localhost:8000"

def create_sample_pdf():
    """Create a sample PDF file"""
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj

xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
196
%%EOF"""
    return BytesIO(pdf_content)

def create_sample_zip():
    """Create a sample ZIP file with PDFs"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        pdf_content = create_sample_pdf().getvalue()
        zip_file.writestr("document1.pdf", pdf_content)
        zip_file.writestr("document2.pdf", pdf_content)
        zip_file.writestr("invalid.txt", b"This is a text file")
    zip_buffer.seek(0)
    return zip_buffer

def login():
    """Login and get access token"""
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": "admin",  # You may need to adjust this
        "password": "admin123"  # You may need to adjust this
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        print(f"Login failed: {response.text}")
        return None

def test_multiple_upload(headers):
    """Test multiple file upload"""
    print("\n=== Testing Multiple Files Upload ===")
    
    pdf1 = create_sample_pdf()
    pdf2 = create_sample_pdf()
    
    response = requests.post(
        f"{BASE_URL}/files/upload/multiple",
        headers=headers,
        files=[
            ("files", ("document1.pdf", pdf1, "application/pdf")),
            ("files", ("document2.pdf", pdf2, "application/pdf"))
        ]
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_zip_upload(headers):
    """Test ZIP file upload"""
    print("\n=== Testing ZIP File Upload ===")
    
    zip_file = create_sample_zip()
    
    response = requests.post(
        f"{BASE_URL}/files/upload/zip",
        headers=headers,
        files={"file": ("documents.zip", zip_file, "application/zip")}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_list_files(headers):
    """Test file listing"""
    print("\n=== Testing File List ===")
    
    response = requests.get(f"{BASE_URL}/files/list", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Main demo function"""
    print("=== File Upload API Demo ===")
    
    # Login first
    headers = login()
    if not headers:
        print("Failed to authenticate. Please check your credentials.")
        return
    
    print("Authentication successful!")
    
    # Test all endpoints
    test_multiple_upload(headers)
    test_zip_upload(headers)
    test_list_files(headers)
    
    print("\n=== Demo completed ===")

if __name__ == "__main__":
    main()
