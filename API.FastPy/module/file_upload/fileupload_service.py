"""
File upload service for handling file operations
"""
import os
import zipfile
import uuid
import magic
import aiofiles
import httpx
import time
import logging
from typing import List, Tuple, Optional
from fastapi import UploadFile, HTTPException
from datetime import datetime
from .FileUploadDTO import FileUploadResponse, FileTypeEnum, FileUploadStatus, MultipleFileUploadResponse, ZipFileUploadResponse
from .FileUploadModel import UploadedFile
from .fileupload_repository import fileupload_repository
from module.report.GeneratedReportModel import GeneratedReport, ReportInputFile
from config.database import SessionLocal
from config.rabbitmq import get_rabbitmq_service

logger = logging.getLogger(__name__)

class FileUploadService:
    def __init__(self):
        self.fileupload_repository = fileupload_repository
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")
        self.GENERATED_DIR = os.getenv("GENERATED_DIR", "storage/generated")
        self.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        self.EXTERNAL_API_URL = "http://4.194.234.149:8000/generate-report"
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.GENERATED_DIR, exist_ok=True)
        self.rabbitmq_service = get_rabbitmq_service()

    # Supported MIME types
    EXCEL_MIMETYPES = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        'application/vnd.ms-excel'  # .xls
    ]
    
    PDF_MIMETYPES = [
        'application/pdf'
    ]
    
    ZIP_MIMETYPES = [
        'application/zip',
        'application/x-zip-compressed'
    ]
    
    
    def _publish_upload_message(self, upload_paths: List[str], template_path: str = "", user_id: Optional[int] = None):
        """
        Publish file upload completion message to RabbitMQ
        """
        try:
            self.rabbitmq_service.publish_file_upload_message(
                upload_paths=upload_paths,
                template_path=template_path,
                user_id=user_id
            )
        except Exception as e:
            # Log error but don't fail the upload process
            logger.error(f"Failed to publish RabbitMQ message: {str(e)}")

    def _validate_file_type(self, file_content: bytes, filename: str) -> Tuple[bool, Optional[FileTypeEnum]]:
        """
        Validate file type based on MIME type detection
        """
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            
            if mime_type in self.EXCEL_MIMETYPES:
                return True, FileTypeEnum.EXCEL
            elif mime_type in self.PDF_MIMETYPES:
                return True, FileTypeEnum.PDF
            elif mime_type in self.ZIP_MIMETYPES:
                return True, None  # ZIP files are handled separately
            else:
                return False, None
        except Exception as e:
            logger.warning(f"File type validation error for {filename}: {str(e)}")
            return False, None
    
    def _validate_file_size(self, file_size: int) -> bool:
        """
        Validate file size
        """
        return file_size <= self.MAX_FILE_SIZE
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename to prevent conflicts
        """
        file_extension = os.path.splitext(original_filename)[1]
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    async def _save_file(self, file: UploadFile, stored_filename: str) -> str:
        """
        Save uploaded file to storage directory
        """
        file_path = os.path.join(self.UPLOAD_DIR, stored_filename)
        
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
            await file.seek(0)  # Reset file pointer
        
        return file_path
    
    def _save_to_database(self, file_info: dict) -> UploadedFile:
        """
        Save file information to database
        """
        db = SessionLocal()
        try:
            return self.fileupload_repository.create_uploaded_file(db, file_info)
        finally:
            db.close()

    def _save_generated_report_to_database(
        self, 
        report_info: dict, 
        template_file: UploadedFile, 
        input_files: List[UploadedFile], 
        user_id: Optional[int] = None,
        report_name: Optional[str] = None
    ) -> GeneratedReport:
        """
        Save generated report information to database
        """
        db = SessionLocal()
        try:
            # Prepare input files information
            input_file_ids = [file.id for file in input_files]
            input_files_info = [
                {
                    "id": file.id,
                    "original_filename": file.original_filename,
                    "stored_filename": file.stored_filename,
                    "file_path": file.file_path,
                    "file_type": file.file_type,
                    "file_size": file.file_size,
                    "uploaded_at": file.uploaded_at.isoformat()
                }
                for file in input_files
            ]
            
            # Create generated report record
            generated_report = GeneratedReport(
                report_name=report_name,  # Use provided report_name
                report_filename=report_info["generated_filename"],
                report_file_path=report_info["generated_file_path"],
                report_file_size=report_info["file_size"],
                report_content_type=report_info["content_type"],
                
                template_file_id=template_file.id,
                template_filename=template_file.original_filename,
                template_file_path=template_file.file_path,
                
                input_file_ids=input_file_ids,
                input_files_info=input_files_info,
                
                generated_by=user_id,
                generation_status="success",
                generation_time_seconds=report_info.get("generation_time_seconds"),
                
                external_api_url=self.EXTERNAL_API_URL,
                external_api_response=report_info.get("api_response"),
                
                is_downloaded=False,
                download_count=0
            )
            
            db.add(generated_report)
            db.commit()
            db.refresh(generated_report)
            
            # Create relationship records
            for input_file in input_files:
                relation = ReportInputFile(
                    report_id=generated_report.id,
                    input_file_id=input_file.id
                )
                db.add(relation)
            
            db.commit()
            db.refresh(generated_report)

            return generated_report
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving generated report to database: {str(e)}")
            raise e
        finally:
            db.close()
    
    def get_uploaded_files(self, page: int = 1, size: int = 10, search: Optional[str] = None) -> List[FileUploadResponse]:
        """
        Get uploaded files with pagination and filtering, including uploader's name.
        """
        db = SessionLocal()
        try:
            skip = (page - 1) * size
            uploaded_files = self.fileupload_repository.get_uploaded_files(db, skip, size, search)
            
            file_responses = []
            for uploaded_file in uploaded_files:
                file_response = FileUploadResponse(
                    filename=uploaded_file.stored_filename,
                    original_filename=uploaded_file.original_filename,
                    file_type=FileTypeEnum(uploaded_file.file_type),
                    file_size=uploaded_file.file_size,
                    status=FileUploadStatus(uploaded_file.status),
                    message=uploaded_file.error_message,
                    file_path=uploaded_file.file_path,
                    uploaded_by_user=uploaded_file.uploaded_by_user, # Assign the user's name
                    uploaded_at=uploaded_file.uploaded_at.isoformat()
                )
                file_responses.append(file_response)
            return file_responses
        finally:
            db.close()

    def get_uploaded_files_count(self, search: Optional[str] = None) -> int:
        """
        Get total count of uploaded files with filtering.
        """
        db = SessionLocal()
        try:
            return self.fileupload_repository.get_uploaded_files_count(db, search)
        finally:
            db.close()

    def _get_uploaded_file_by_path(self, file_path: str) -> Optional[UploadedFile]:
        """
        Get uploaded file record by file path
        """
        db = SessionLocal()
        try:
            # Use the repository method
            return db.query(UploadedFile).filter(UploadedFile.file_path == file_path).first()
        finally:
            db.close()
    
    async def upload_single_file(self, file: UploadFile, user_id: Optional[int] = None, send_rabbitmq_message: bool = True) -> FileUploadResponse:
        """
        Handle single file upload
        """
        try:
            # Read file content for validation
            content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Validate file size
            if not self._validate_file_size(len(content)):
                return FileUploadResponse(
                    filename="",
                    original_filename=file.filename,
                    file_type=FileTypeEnum.PDF,  # Default
                    file_size=len(content),
                    status=FileUploadStatus.ERROR,
                    message=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE/1024/1024:.1f}MB",
                    uploaded_at=datetime.now().isoformat()
                )
            
            # Validate file type
            is_valid, file_type = self._validate_file_type(content, file.filename)
            if not is_valid:
                return FileUploadResponse(
                    filename="",
                    original_filename=file.filename,
                    file_type=FileTypeEnum.PDF,  # Default
                    file_size=len(content),
                    status=FileUploadStatus.ERROR,
                    message="Unsupported file type. Only Excel (.xlsx) and PDF files are allowed.",
                    uploaded_at=datetime.now().isoformat()
                )
            
            # Generate unique filename and save file
            stored_filename = self._generate_unique_filename(file.filename)
            file_path = await self._save_file(file, stored_filename)
            
            # Save to database
            file_info = {
                "original_filename": file.filename,
                "stored_filename": stored_filename,
                "file_path": file_path,
                "file_type": file_type.value,
                "file_size": len(content),
                "mimetype": magic.from_buffer(content, mime=True),
                "uploaded_by": user_id,
                "status": "success"
            }
            
            db_file = self._save_to_database(file_info)
            
            # Publish RabbitMQ message for successful upload (only if requested)
            if send_rabbitmq_message:
                self._publish_upload_message(
                    upload_paths=[file_path],
                    template_path="",  # No template for single file upload
                    user_id=user_id
                )
            
            return FileUploadResponse(
                filename=stored_filename,
                original_filename=file.filename,
                file_type=file_type,
                file_size=len(content),
                status=FileUploadStatus.SUCCESS,
                message="File uploaded successfully",
                file_path=file_path,
                uploaded_at=db_file.uploaded_at.isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error uploading single file {file.filename}: {str(e)}")
            return FileUploadResponse(
                filename="",
                original_filename=file.filename if file.filename else "unknown",
                file_type=FileTypeEnum.PDF,  # Default
                file_size=0,
                status=FileUploadStatus.ERROR,
                message=f"Upload failed: {str(e)}",
                uploaded_at=datetime.now().isoformat()
            )
    
    async def upload_multiple_files(self, files: List[UploadFile], user_id: Optional[int] = None) -> MultipleFileUploadResponse:
        """
        Handle multiple file uploads
        """
        results = []
        successful_count = 0
        successful_file_paths = []
        
        for file in files:
            result = await self.upload_single_file(file, user_id, send_rabbitmq_message=False)
            results.append(result)
            
            if result.status == FileUploadStatus.SUCCESS:
                successful_count += 1
                if result.file_path:
                    successful_file_paths.append(result.file_path)
        
        # Publish RabbitMQ message for successful uploads
        if successful_file_paths:
            self._publish_upload_message(
                upload_paths=successful_file_paths,
                template_path="",  # No template for multiple file upload
                user_id=user_id
            )
        
        failed_count = len(files) - successful_count
        overall_status = FileUploadStatus.SUCCESS if failed_count == 0 else (
            FileUploadStatus.ERROR if successful_count == 0 else FileUploadStatus.PROCESSING
        )
        
        return MultipleFileUploadResponse(
            total_files=len(files),
            successful_uploads=successful_count,
            failed_uploads=failed_count,
            files=results,
            overall_status=overall_status
        )
    
    async def upload_zip_file(self, file: UploadFile, user_id: Optional[int] = None) -> ZipFileUploadResponse:
        """
        Handle ZIP file upload with extraction
        """
        try:
            # Read and validate ZIP file
            content = await file.read()
            await file.seek(0)
            
            # Validate file size
            if not self._validate_file_size(len(content)):
                return ZipFileUploadResponse(
                    zip_filename=file.filename,
                    extracted_files=[],
                    total_extracted=0,
                    successful_uploads=0,
                    failed_uploads=1,
                    overall_status=FileUploadStatus.ERROR
                )
            
            # Validate ZIP MIME type
            mime_type = magic.from_buffer(content, mime=True)
            if mime_type not in self.ZIP_MIMETYPES:
                raise HTTPException(status_code=400, detail="File is not a valid ZIP archive")
            
            # Create temporary file for ZIP extraction
            temp_zip_path = os.path.join(self.UPLOAD_DIR, f"temp_{uuid.uuid4()}.zip")
            
            async with aiofiles.open(temp_zip_path, 'wb') as temp_file:
                await temp_file.write(content)
            
            extracted_files = []
            successful_count = 0
            successful_file_paths = []
            
            try:
                # Extract ZIP file
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    for zip_info in zip_ref.infolist():
                        if zip_info.is_dir():
                            continue
                            
                        # Extract file content
                        with zip_ref.open(zip_info) as extracted_file:
                            file_content = extracted_file.read()
                            
                            # Validate extracted file
                            is_valid, file_type = self._validate_file_type(file_content, zip_info.filename)
                            
                            if is_valid and self._validate_file_size(len(file_content)):
                                # Create a mock UploadFile object
                                stored_filename = self._generate_unique_filename(zip_info.filename)
                                file_path = os.path.join(self.UPLOAD_DIR, stored_filename)
                                
                                # Save extracted file
                                async with aiofiles.open(file_path, 'wb') as output_file:
                                    await output_file.write(file_content)
                                
                                # Save to database
                                file_info = {
                                    "original_filename": zip_info.filename,
                                    "stored_filename": stored_filename,
                                    "file_path": file_path,
                                    "file_type": file_type.value,
                                    "file_size": len(file_content),
                                    "mimetype": magic.from_buffer(file_content, mime=True),
                                    "uploaded_by": user_id,
                                    "status": "success"
                                }
                                
                                db_file = self._save_to_database(file_info)
                                
                                extracted_files.append(FileUploadResponse(
                                    filename=stored_filename,
                                    original_filename=zip_info.filename,
                                    file_type=file_type,
                                    file_size=len(file_content),
                                    status=FileUploadStatus.SUCCESS,
                                    message="File extracted and uploaded successfully",
                                    file_path=file_path,
                                    uploaded_at=db_file.uploaded_at.isoformat()
                                ))
                                successful_count += 1
                                successful_file_paths.append(file_path)
                            else:
                                extracted_files.append(FileUploadResponse(
                                    filename="",
                                    original_filename=zip_info.filename,
                                    file_type=FileTypeEnum.PDF,  # Default
                                    file_size=len(file_content) if file_content else 0,
                                    status=FileUploadStatus.ERROR,
                                    message="File type not supported or file too large",
                                    uploaded_at=datetime.now().isoformat()
                                ))
                
            finally:
                # Clean up temporary ZIP file
                if os.path.exists(temp_zip_path):
                    os.remove(temp_zip_path)
            
            # Publish RabbitMQ message for successful extracted files
            if successful_file_paths:
                self._publish_upload_message(
                    upload_paths=successful_file_paths,
                    template_path="",  # No template for ZIP extraction
                    user_id=user_id
                )
            
            failed_count = len(extracted_files) - successful_count
            overall_status = FileUploadStatus.SUCCESS if failed_count == 0 else (
                FileUploadStatus.ERROR if successful_count == 0 else FileUploadStatus.PROCESSING
            )
            
            return ZipFileUploadResponse(
                zip_filename=file.filename,
                extracted_files=extracted_files,
                total_extracted=len(extracted_files),
                successful_uploads=successful_count,
                failed_uploads=failed_count,
                overall_status=overall_status
            )
            
        except Exception as e:
            logger.error(f"Error uploading ZIP file {file.filename}: {str(e)}")
            return ZipFileUploadResponse(
                zip_filename=file.filename,
                extracted_files=[],
                total_extracted=0,
                successful_uploads=0,
                failed_uploads=1,
                overall_status=FileUploadStatus.ERROR
            )

    async def upload_with_template(self, files: List[UploadFile], template_file: UploadFile, user_id: Optional[int] = None) -> dict:
        """
        Handle file uploads with a template file
        
        Args:
            files: List of files to upload
            template_file: Template file to use
            user_id: ID of the user uploading files
            
        Returns:
            Dictionary containing upload results and template information
        """
        # Upload template file first
        template_result = await self.upload_single_file(template_file, user_id, send_rabbitmq_message=False)
        
        if template_result.status != FileUploadStatus.SUCCESS:
            return {
                "template_upload": template_result,
                "file_uploads": None,
                "status": "error",
                "message": "Template upload failed"
            }
        
        # Upload data files
        files_result = await self.upload_multiple_files(files, user_id)
        
        # Get successful file paths
        successful_file_paths = [
            file.file_path for file in files_result.files 
            if file.status == FileUploadStatus.SUCCESS and file.file_path
        ]
        
        # Publish RabbitMQ message with template and data files
        if successful_file_paths and template_result.file_path:
            self._publish_upload_message(
                upload_paths=successful_file_paths,
                template_path=template_result.file_path,
                user_id=user_id
            )
        
        return {
            "template_upload": template_result,
            "file_uploads": files_result,
            "status": "success" if files_result.successful_uploads > 0 else "error",
            "message": f"Uploaded {files_result.successful_uploads} files with template"
        }

    async def _call_external_generate_report_api(self, template_path: str, document_paths: List[str]) -> dict:
        """
        Call external API to generate report
        
        Args:
            template_path: Path to template file
            document_paths: List of paths to document files
            
        Returns:
            Dictionary containing API response and saved file info
        """
        start_time = time.time()
        
        try:
            files = {}
            
            # Prepare template file
            async with aiofiles.open(template_path, 'rb') as f:
                template_content = await f.read()
                template_filename = os.path.basename(template_path)
                
                # Determine content type based on file extension
                if template_filename.lower().endswith('.xlsx'):
                    template_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                elif template_filename.lower().endswith('.pdf'):
                    template_content_type = 'application/pdf'
                else:
                    template_content_type = 'application/octet-stream'
                    
                files['template'] = (template_filename, template_content, template_content_type)
            
            # Prepare document files
            documents = []
            for doc_path in document_paths:
                async with aiofiles.open(doc_path, 'rb') as f:
                    doc_content = await f.read()
                    doc_filename = os.path.basename(doc_path)
                    
                    # Determine content type based on file extension
                    if doc_filename.lower().endswith('.pdf'):
                        doc_content_type = 'application/pdf'
                    elif doc_filename.lower().endswith('.xlsx'):
                        doc_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    else:
                        doc_content_type = 'application/octet-stream'
                    
                    documents.append(('documents', (doc_filename, doc_content, doc_content_type)))
            
            # Add documents to files
            files.update(dict(documents))
            
            # Call external API
            async with httpx.AsyncClient(timeout=httpx.Timeout(3000.0)) as client:  # 50 minute timeout
                api_call_start = time.time()
                response = await client.post(
                    self.EXTERNAL_API_URL,
                    files=files
                )
                api_call_time = time.time() - api_call_start
                
                if response.status_code == 200:
                    # Save the generated file
                    generated_filename = f"generated_report_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # Determine file extension from response headers
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        generated_filename += '.pdf'
                    elif 'excel' in content_type or 'spreadsheet' in content_type:
                        generated_filename += '.xlsx'
                    elif 'zip' in content_type:
                        generated_filename += '.zip'
                    else:
                        # Try to get from content-disposition header
                        content_disposition = response.headers.get('content-disposition', '')
                        if 'filename=' in content_disposition:
                            # Extract filename from content-disposition
                            import re
                            filename_match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
                            if filename_match:
                                original_filename = filename_match.group(1).strip('"\'')
                                _, ext = os.path.splitext(original_filename)
                                if ext:
                                    generated_filename += ext
                                else:
                                    generated_filename += '.bin'
                            else:
                                generated_filename += '.bin'
                        else:
                            generated_filename += '.bin'
                    
                    generated_file_path = os.path.join(self.GENERATED_DIR, generated_filename)
                    
                    # Save the generated file
                    async with aiofiles.open(generated_file_path, 'wb') as f:
                        await f.write(response.content)
                    
                    total_time = time.time() - start_time
                    
                    return {
                        "success": True,
                        "generated_file_path": generated_file_path,
                        "generated_filename": generated_filename,
                        "file_size": len(response.content),
                        "content_type": content_type,
                        "generation_time_seconds": int(total_time),
                        "api_call_time_seconds": int(api_call_time),
                        "api_response": {
                            "status_code": response.status_code,
                            "headers": dict(response.headers),
                            "response_size": len(response.content)
                        },
                        "message": "Report generated successfully"
                    }
                else:
                    total_time = time.time() - start_time
                    logger.error(f"External API error {response.status_code}: {response.text}")
                    return {
                        "success": False,
                        "error": f"External API returned status {response.status_code}",
                        "message": response.text,
                        "generation_time_seconds": int(total_time),
                        "api_response": {
                            "status_code": response.status_code,
                            "headers": dict(response.headers),
                            "response_text": response.text
                        }
                    }
                    
        except httpx.TimeoutException:
            total_time = time.time() - start_time
            logger.error("External API call timed out after 50 minutes")
            return {
                "success": False,
                "error": "Request timeout",
                "message": "External API call timed out after 50 minutes",
                "generation_time_seconds": int(total_time)
            }
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Error calling external API: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to call external API: {str(e)}",
                "generation_time_seconds": int(total_time)
            }

    async def upload_with_template_and_generate(self, files: List[UploadFile], template_file: UploadFile, user_id: Optional[int] = None, report_name: Optional[str] = None) -> dict:
        """
        Handle file uploads with template and call external API to generate report
        
        Args:
            files: List of files to upload
            template_file: Template file to use
            user_id: ID of the user uploading files
            report_name: Name for the generated report

        Returns:
            Dictionary containing upload results, template information, and generated report
        """
        # Upload template file first
        template_result = await self.upload_single_file(template_file, user_id, send_rabbitmq_message=False)
        
        if template_result.status != FileUploadStatus.SUCCESS:
            return {
                "template_upload": template_result,
                "file_uploads": None,
                "generated_report": None,
                "status": "error",
                "message": "Template upload failed"
            }
        
        # Upload data files
        files_result = await self.upload_multiple_files(files, user_id)
        
        if files_result.successful_uploads == 0:
            return {
                "template_upload": template_result,
                "file_uploads": files_result,
                "generated_report": None,
                "status": "error",
                "message": "No files were uploaded successfully"
            }
        
        # Get successful file paths
        successful_file_paths = [
            file.file_path for file in files_result.files 
            if file.status == FileUploadStatus.SUCCESS and file.file_path
        ]
        
        # Call external API to generate report
        if template_result.file_path:
            # Get MOCK_EXTERNAL_API from environment variable
            mock_external_api = os.getenv('MOCK_EXTERNAL_API', 'false').lower() in ('true', '1', 'yes', 'on')

            # Call external API to generate report or use mock
            if mock_external_api:
                # Use simulated API response
                api_result = await self._simulate_external_api_response(
                    template_path=template_result.file_path,
                    document_paths=successful_file_paths
                )
            else:
                # Use real external API
                api_result = await self._call_external_generate_report_api(
                    template_path=template_result.file_path,
                    document_paths=successful_file_paths
                )

            # Log api_result for debugging
            logger.info(f"External API result: {api_result}")

            # Save generated report to database if API call was successful
            generated_report_db = None
            if api_result.get("success", False):
                try:
                    # Get database records for template and input files
                    template_file_db = self._get_uploaded_file_by_path(template_result.file_path)
                    input_files_db = [
                        self._get_uploaded_file_by_path(path) 
                        for path in successful_file_paths
                    ]
                    input_files_db = [f for f in input_files_db if f is not None]
                    
                    if template_file_db and input_files_db:
                        generated_report_db = self._save_generated_report_to_database(
                            report_info=api_result,
                            template_file=template_file_db,
                            input_files=input_files_db,
                            user_id=user_id,
                            report_name=report_name  # Pass report_name to database save method
                        )
                        
                        # Add database ID to API result
                        api_result["report_id"] = generated_report_db.id
                        api_result["database_saved"] = True
                        
                except Exception as e:
                    # Log error but don't fail the whole operation
                    logger.error(f"Error saving generated report to database: {str(e)}")
                    api_result["database_error"] = str(e)
                    api_result["database_saved"] = False

            # Still publish RabbitMQ message regardless of API call result
            self._publish_upload_message(
                upload_paths=successful_file_paths,
                template_path=template_result.file_path,
                user_id=user_id
            )
            
            return {
                "template_upload": template_result,
                "file_uploads": files_result,
                "generated_report": api_result,
                "status": "success" if api_result.get("success", False) else "partial_success",
                "message": f"Uploaded {files_result.successful_uploads} files with template. " + 
                          (api_result.get("message", "") if api_result.get("success") else f"Generated AI error : {api_result.get('message', 'Unknown error')}")
            }
        else:
            return {
                "template_upload": template_result,
                "file_uploads": files_result,
                "generated_report": None,
                "status": "error",
                "message": "Template file path not available"
            }

    async def upload_with_template_and_generate_extended(
        self,
        files: Optional[List[UploadFile]] = None,
        template_file: Optional[UploadFile] = None,
        file_ids: Optional[List[int]] = None,
        template_id: Optional[int] = None,
        user_id: Optional[int] = None,
        report_name: Optional[str] = None
    ) -> dict:
        """
        Extended method to handle file uploads with template and generate report.
        Can work with both new uploads and existing files/templates.

        Args:
            files: List of new files to upload (optional)
            template_file: New template file to upload (optional)
            file_ids: List of existing file IDs to use (optional)
            template_id: ID of existing template to use (optional)
            user_id: ID of the user
            report_name: Name for the generated report

        Returns:
            Dictionary containing upload results, template information, and generated report

        Logic:
            - If template_file is provided, it takes priority over template_id
            - If both files and file_ids are provided, both are used
            - At least one template source and one data source must be provided
        """
        from module.template.template_repository import template_repository
        from config.database import SessionLocal

        db = SessionLocal()
        try:
            # Handle template source (prioritize uploaded template over template_id)
            template_result = None
            template_path = None
            template_file_db = None

            if template_file and template_file.filename:
                # Upload new template file
                template_result = await self.upload_single_file(template_file, user_id, send_rabbitmq_message=False)

                if template_result.status != FileUploadStatus.SUCCESS:
                    return {
                        "template_upload": template_result,
                        "file_uploads": None,
                        "generated_report": None,
                        "status": "error",
                        "message": "Template upload failed"
                    }
                template_path = template_result.file_path
                template_file_db = self._get_uploaded_file_by_path(template_path)

            elif template_id:
                # Use existing template
                template_db_record = template_repository.get_template_by_id(db, template_id)
                if not template_db_record:
                    return {
                        "template_upload": None,
                        "file_uploads": None,
                        "generated_report": None,
                        "status": "error",
                        "message": f"Template with ID {template_id} not found"
                    }

                # Check if user has access to this template (if needed)
                # Add access control logic here if required

                template_path = template_db_record.file_path
                # Create a mock template_result for consistency
                template_result = FileUploadResponse(
                    filename=template_db_record.name,
                    original_filename=template_db_record.name,
                    file_type=FileTypeEnum.EXCEL if template_db_record.file_path.endswith(('.xlsx', '.xls')) else FileTypeEnum.PDF,
                    file_size=0,  # Template model doesn't store size
                    status=FileUploadStatus.SUCCESS,
                    message="Using existing template",
                    file_path=template_path,
                    uploaded_at=template_db_record.created_at.isoformat() if template_db_record.created_at else ""
                )
                # For existing templates, we need to find the corresponding uploaded file
                template_file_db = self._get_uploaded_file_by_path(template_path)

            else:
                return {
                    "template_upload": None,
                    "file_uploads": None,
                    "generated_report": None,
                    "status": "error",
                    "message": "No template provided. Either upload a template file or provide template_id"
                }

            # Handle data files
            successful_file_paths = []
            input_files_db = []
            files_result = None

            # Process new file uploads
            if files and len(files) > 0:
                # Filter out empty files
                valid_files = [f for f in files if f.filename]
                if valid_files:
                    files_result = await self.upload_multiple_files(valid_files, user_id)

                    # Get successful file paths from new uploads
                    new_file_paths = [
                        file.file_path for file in files_result.files
                        if file.status == FileUploadStatus.SUCCESS and file.file_path
                    ]
                    successful_file_paths.extend(new_file_paths)

                    # Get database records for new files
                    new_files_db = [
                        self._get_uploaded_file_by_path(path)
                        for path in new_file_paths
                    ]
                    input_files_db.extend([f for f in new_files_db if f is not None])

            # Process existing file IDs
            if file_ids and len(file_ids) > 0:
                existing_files_db = []
                for file_id in file_ids:
                    file_db = self.fileupload_repository.get_uploaded_file_by_id(db, file_id)
                    if file_db:
                        # Check if user has access to this file (if needed)
                        # Add access control logic here if required
                        existing_files_db.append(file_db)
                        successful_file_paths.append(file_db.file_path)
                        input_files_db.append(file_db)
                    else:
                        logger.warning(f"File with ID {file_id} not found")

                # If we have existing files but no new uploads, create a mock files_result
                if not files_result and existing_files_db:
                    mock_file_responses = []
                    for file_db in existing_files_db:
                        mock_response = FileUploadResponse(
                            filename=file_db.stored_filename,
                            original_filename=file_db.original_filename,
                            file_type=FileTypeEnum.EXCEL if file_db.file_type == 'excel' else FileTypeEnum.PDF,
                            file_size=file_db.file_size,
                            status=FileUploadStatus.SUCCESS,
                            message="Using existing file",
                            file_path=file_db.file_path,
                            uploaded_at=file_db.uploaded_at.isoformat() if file_db.uploaded_at else ""
                        )
                        mock_file_responses.append(mock_response)

                    files_result = MultipleFileUploadResponse(
                        total_files=len(existing_files_db),
                        successful_uploads=len(existing_files_db),
                        failed_uploads=0,
                        files=mock_file_responses,
                        overall_status=FileUploadStatus.SUCCESS
                    )

            # Check if we have any data files
            if not successful_file_paths:
                return {
                    "template_upload": template_result,
                    "file_uploads": files_result,
                    "generated_report": None,
                    "status": "error",
                    "message": "No data files available. Either upload files or provide valid file_ids"
                }

            # Create default files_result if none exists
            if not files_result:
                files_result = MultipleFileUploadResponse(
                    total_files=0,
                    successful_uploads=0,
                    failed_uploads=0,
                    files=[],
                    overall_status=FileUploadStatus.SUCCESS
                )

            # Call external API to generate report
            if template_path:
                # Get MOCK_EXTERNAL_API from environment variable
                mock_external_api = os.getenv('MOCK_EXTERNAL_API', 'false').lower() in ('true', '1', 'yes', 'on')

                # Call external API to generate report or use mock
                if mock_external_api:
                    # Use simulated API response
                    api_result = await self._simulate_external_api_response(
                        template_path=template_path,
                        document_paths=successful_file_paths
                    )
                else:
                    # Use real external API
                    api_result = await self._call_external_generate_report_api(
                        template_path=template_path,
                        document_paths=successful_file_paths
                    )

                # Log api_result for debugging
                logger.info(f"External API result: {api_result}")

                # Save generated report to database if API call was successful
                generated_report_db = None
                if api_result.get("success", False):
                    try:
                        if template_file_db and input_files_db:
                            generated_report_db = self._save_generated_report_to_database(
                                report_info=api_result,
                                template_file=template_file_db,
                                input_files=input_files_db,
                                user_id=user_id,
                                report_name=report_name
                            )

                            # Add database ID to API result
                            api_result["report_id"] = generated_report_db.id
                            api_result["database_saved"] = True

                    except Exception as e:
                        # Log error but don't fail the whole operation
                        logger.error(f"Error saving generated report to database: {str(e)}")
                        api_result["database_error"] = str(e)
                        api_result["database_saved"] = False

                # Publish RabbitMQ message
                self._publish_upload_message(
                    upload_paths=successful_file_paths,
                    template_path=template_path,
                    user_id=user_id
                )

                total_files = len(successful_file_paths)
                return {
                    "template_upload": template_result,
                    "file_uploads": files_result,
                    "generated_report": api_result,
                    "status": "success" if api_result.get("success", False) else "partial_success",
                    "message": f"Processed {total_files} files with template. " +
                              (api_result.get("message", "") if api_result.get("success") else f"Generated AI error : {api_result.get('message', 'Unknown error')}")
                }
            else:
                return {
                    "template_upload": template_result,
                    "file_uploads": files_result,
                    "generated_report": None,
                    "status": "error",
                    "message": "Template file path not available"
                }

        finally:
            db.close()

    def get_generated_reports(self, user_id: Optional[int] = None, limit: int = 100, offset: int = 0, search: Optional[str] = None) -> List[GeneratedReport]:
        """
        Get list of generated reports
        """
        db = SessionLocal()
        try:
            query = db.query(GeneratedReport)
            # if user_id:
            #     query = query.filter(GeneratedReport.generated_by == user_id)
            
            # Add search functionality
            if search:
                search_term = f"%{search}%"
                from sqlalchemy import or_
                query = query.filter(
                    or_(
                        GeneratedReport.report_name.ilike(search_term),
                        GeneratedReport.template_filename.ilike(search_term),
                        GeneratedReport.report_filename.ilike(search_term)
                    )
                )
            
            return query.order_by(GeneratedReport.generated_at.desc()).offset(offset).limit(limit).all()
        finally:
            db.close()
    
    def get_generated_report_by_id(self, report_id: int) -> Optional[GeneratedReport]:
        """
        Get a specific generated report by ID
        """
        db = SessionLocal()
        try:
            return db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
        finally:
            db.close()
    
    def mark_report_as_downloaded(self, report_id: int):
        """
        Mark a report as downloaded and increment download count
        """
        db = SessionLocal()
        try:
            report = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
            if report:
                report.is_downloaded = True
                report.download_count += 1
                db.commit()
        finally:
            db.close()
    
    def update_report_name(self, report_id: int, new_name: str) -> bool:
        """
        Update the name of a generated report
        """
        db = SessionLocal()
        try:
            report = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
            if report:
                report.report_name = new_name if new_name else None
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    
    def delete_generated_report(self, report_id: int) -> bool:
        """
        Delete a generated report and its associated file
        """
        db = SessionLocal()
        try:
            report = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
            if not report:
                return False
            
            # Delete physical file
            try:
                if os.path.exists(report.report_file_path):
                    os.remove(report.report_file_path)
            except Exception:
                # Log error but continue with database deletion
                pass
            
            # Delete relationship records first
            db.query(ReportInputFile).filter(ReportInputFile.report_id == report_id).delete()
            
            # Delete report record
            db.delete(report)
            db.commit()
            return True
            
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    async def _simulate_external_api_response(self, template_path: str, document_paths: List[str]) -> dict:
        """
        Simulate external API response for testing purposes

        Args:
            template_path: Path to template file
            document_paths: List of paths to document files

        Returns:
            Dictionary containing simulated API response
        """
        logger.info("Using simulated external API response (MOCK_EXTERNAL_API=True)")

        # Generate realistic filenames and paths
        generated_filename = f"generated_report_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        generated_file_path = os.path.join(self.GENERATED_DIR, generated_filename)

        # Create a dummy file for testing
        os.makedirs(self.GENERATED_DIR, exist_ok=True)
        dummy_content = f"Simulated generated report content\nTemplate: {os.path.basename(template_path)}\nInput files: {[os.path.basename(p) for p in document_paths]}\nGenerated at: {datetime.now().isoformat()}"

        async with aiofiles.open(generated_file_path, 'w') as f:
            await f.write(dummy_content)

        # Calculate file size
        file_size = len(dummy_content.encode('utf-8'))

        return {
            "success": True,
            "generated_file_path": generated_file_path,
            "generated_filename": generated_filename,
            "file_size": file_size,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "generation_time_seconds": 2,  # Simulated quick response
            "api_call_time_seconds": 1,
            "api_response": {
                "status_code": 200,
                "headers": {"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
                "response_size": file_size
            },
            "message": "Report generated successfully (SIMULATED - MOCK_EXTERNAL_API=True)"
        }
