"""
Test file upload functionality
"""
import pytest
import os
import tempfile
import zipfile
from fastapi.testclient import TestClient
from io import BytesIO
from main import app
from config.database import SessionLocal
from user_mgmt.UserModel import User
from file_upload.FileUploadModel import UploadedFile
from user_auth.security import create_access_token

client = TestClient(app)

@pytest.fixture
def test_user():
    """Create a test user"""
    db = SessionLocal()
    
    # Create test user if doesn't exist
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="$2b$12$dummy_hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create access token
    token = create_access_token(data={"sub": user.username})
    
    yield {"user": user, "token": token}
    
    # Cleanup uploaded files
    files = db.query(UploadedFile).filter(UploadedFile.uploaded_by == user.id).all()
    for file_record in files:
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        db.delete(file_record)
    db.commit()
    db.close()

@pytest.fixture
def auth_headers(test_user):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {test_user['token']}"}

@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing"""
    # Simple PDF content (minimal valid PDF)
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

@pytest.fixture
def sample_excel():
    """Create a sample Excel file for testing"""
    # Minimal XLSX file structure (simplified)
    xlsx_content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00'  # ZIP header for XLSX
    return BytesIO(xlsx_content)

def test_upload_multiple_files_success(auth_headers, sample_pdf):
    """Test successful multiple file upload"""
    pdf1 = BytesIO(sample_pdf.getvalue())
    pdf2 = BytesIO(sample_pdf.getvalue())
    
    response = client.post(
        "/files/upload/multiple",
        headers=auth_headers,
        files=[
            ("files", ("test1.pdf", pdf1, "application/pdf")),
            ("files", ("test2.pdf", pdf2, "application/pdf"))
        ]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_files"] == 2
    assert data["successful_uploads"] == 2
    assert data["failed_uploads"] == 0
    assert len(data["files"]) == 2

def test_upload_multiple_files_mixed_results(auth_headers, sample_pdf, sample_text):
    """Test multiple file upload with mixed results"""
    pdf_file = BytesIO(sample_pdf.getvalue())
    text_file = BytesIO(sample_text.getvalue())
    
    response = client.post(
        "/files/upload/multiple",
        headers=auth_headers,
        files=[
            ("files", ("test.pdf", pdf_file, "application/pdf")),
            ("files", ("test.txt", text_file, "text/plain"))
        ]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_files"] == 2
    assert data["successful_uploads"] == 1
    assert data["failed_uploads"] == 1

def test_upload_zip_file_success(auth_headers, sample_pdf):
    """Test successful ZIP file upload"""
    # Create a ZIP file with PDF content
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("document1.pdf", sample_pdf.getvalue())
        zip_file.writestr("document2.pdf", sample_pdf.getvalue())
    
    zip_buffer.seek(0)
    
    response = client.post(
        "/files/upload/zip",
        headers=auth_headers,
        files={"file": ("documents.zip", zip_buffer, "application/zip")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["zip_filename"] == "documents.zip"
    assert data["total_extracted"] == 2
    assert data["successful_uploads"] == 2

def test_list_user_files(auth_headers, test_user, sample_pdf):
    """Test listing user files"""
    # First upload a file
    client.post(
        "/files/upload",
        headers=auth_headers,
        files={"file": ("test.pdf", sample_pdf, "application/pdf")}
    )
    
    # Then list files
    response = client.get("/files/list", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert data["user_id"] == test_user["user"].id
    assert len(data["files"]) > 0

def test_delete_file(auth_headers, test_user, sample_pdf):
    """Test file deletion"""
    # First upload a file
    upload_response = client.post(
        "/files/upload",
        headers=auth_headers,
        files={"file": ("test.pdf", sample_pdf, "application/pdf")}
    )
    
    # Get file list to find the file ID
    list_response = client.get("/files/list", headers=auth_headers)
    files = list_response.json()["files"]
    file_id = files[0]["id"]
    
    # Delete the file
    delete_response = client.delete(f"/files/{file_id}", headers=auth_headers)
    
    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["message"]

def test_upload_without_authentication():
    """Test upload without authentication token"""
    response = client.post(
        "/files/upload",
        files={"file": ("test.pdf", BytesIO(b"dummy"), "application/pdf")}
    )
    
    assert response.status_code == 403

def test_upload_large_file(auth_headers):
    """Test upload of file exceeding size limit"""
    # Create a file larger than 50MB
    large_content = b'x' * (51 * 1024 * 1024)  # 51MB
    
    response = client.post(
        "/files/upload",
        headers=auth_headers,
        files={"file": ("large.pdf", BytesIO(large_content), "application/pdf")}
    )
    
    assert response.status_code == 400
    assert "exceeds maximum limit" in response.json()["detail"]
