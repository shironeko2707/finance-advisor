"""
File upload DTOs for request/response models
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class FileTypeEnum(str, Enum):
    EXCEL = "excel"
    PDF = "pdf"

class FileUploadStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error" 
    PROCESSING = "processing"

class FileUploadResponse(BaseModel):
    filename: str
    original_filename: str
    file_type: FileTypeEnum
    file_size: int
    status: FileUploadStatus
    message: Optional[str] = None
    file_path: Optional[str] = None
    uploaded_by_user: Optional[str] = None # Name of the user who uploaded the file
    uploaded_at: str

class MultipleFileUploadResponse(BaseModel):
    total_files: int
    successful_uploads: int
    failed_uploads: int
    files: List[FileUploadResponse]
    overall_status: FileUploadStatus

class ZipFileUploadResponse(BaseModel):
    zip_filename: str
    extracted_files: List[FileUploadResponse]
    total_extracted: int
    successful_uploads: int
    failed_uploads: int
    overall_status: FileUploadStatus

class FileInfo(BaseModel):
    filename: str
    size: int
    mimetype: str
    created_at: str

class TemplateWithFilesResponse(BaseModel):
    """Response for upload files with template and generate report"""
    template_upload: FileUploadResponse
    file_uploads: MultipleFileUploadResponse
    generated_report: Optional[dict] = None
    status: str
    message: str

class GeneratedReportInfo(BaseModel):
    """Information about a generated report"""
    id: int
    report_name: Optional[str] = None
    user_name: str = None
    report_filename: str
    report_file_path: str
    report_file_size: int
    report_content_type: str
    template_filename: str
    input_files_count: int
    input_files_info: List[dict]
    generated_at: str
    generated_by: Optional[int] = None
    generation_status: str
    generation_time_seconds: Optional[int] = None
    is_downloaded: bool
    download_count: int
    
    class Config:
        from_attributes = True

class GeneratedReportListResponse(BaseModel):
    """Response for listing generated reports"""
    reports: List[GeneratedReportInfo]
    total: int
    user_id: Optional[int] = None

class GeneratedReportDetailResponse(BaseModel):
    """Detailed response for a single generated report"""
    id: int
    report_name: Optional[str] = None
    report_filename: str
    report_file_path: str
    report_file_size: int
    report_content_type: str
    
    # Template details
    template_file_id: int
    template_filename: str
    template_file_path: str
    
    # Input files details
    input_files: List[dict]
    input_files_count: int
    
    # Generation metadata
    generated_at: str
    generated_by: Optional[int] = None
    generation_status: str
    generation_time_seconds: Optional[int] = None
    
    # API metadata
    external_api_url: Optional[str] = None
    external_api_response: Optional[dict] = None
    
    # Usage metadata
    is_downloaded: bool
    download_count: int
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
