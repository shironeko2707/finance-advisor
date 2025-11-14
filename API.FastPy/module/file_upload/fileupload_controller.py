"""
File upload controller with REST API endpoints
"""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Form
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from module.user_auth.provider.user import get_current_user
from module.user_mgmt.UserModel import User
from config.database import get_db
from .fileupload_service import FileUploadService
from .FileUploadDTO import MultipleFileUploadResponse, ZipFileUploadResponse, TemplateWithFilesResponse
from module.user_mgmt.user_service import user_service

router = APIRouter(
    prefix="/files",
    tags=["File Upload"],
    responses={404: {"description": "Not found"}},
)

file_service = FileUploadService()

@router.post("/upload/multiple",
             response_model=MultipleFileUploadResponse,
             summary="Upload multiple files",
             description="""
             Upload multiple files at once (Excel .xlsx or PDF only).
             
             **Supported file types:**
             - Excel files (.xlsx) - MIME: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet  
             - PDF files (.pdf) - MIME: application/pdf
             
             **File size limit:** 50MB per file
             
             **Validation:** Files are validated by MIME type, not file extension.
             
             **Behavior:** 
             - Continues processing even if some files fail
             - Returns detailed status for each file
             - Overall status indicates if all, some, or no files succeeded
             """)
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="Multiple files to upload (Excel or PDF only)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MultipleFileUploadResponse:
    """Upload multiple Excel or PDF files"""
    
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Check for empty filenames
    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more files have no filename"
            )
    
    result = await file_service.upload_multiple_files(files, current_user.id)
    return result

@router.post("/upload/zip",
             response_model=ZipFileUploadResponse, 
             summary="Upload and extract ZIP file",
             description="""
             Upload a ZIP file and extract its contents.
             
             **ZIP file requirements:**
             - Must be a valid ZIP archive
             - Maximum size: 50MB
             
             **Extracted file requirements:**
             - Only Excel (.xlsx) and PDF files will be processed
             - Invalid files inside ZIP will be skipped
             - Files are validated by MIME type, not extension
             
             **Behavior:**
             - Extracts all valid Excel and PDF files from ZIP
             - Invalid files are reported but don't stop processing
             - Returns detailed status for each extracted file
             - ZIP file itself is not stored, only extracted files
             """)
async def upload_zip_file(
    file: UploadFile = File(..., description="ZIP file containing Excel or PDF files"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ZipFileUploadResponse:
    """Upload a ZIP file and extract Excel/PDF files from it"""
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    result = await file_service.upload_zip_file(file, current_user.id)
    
    if result.overall_status == "error" and result.successful_uploads == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process ZIP file or no valid files found"
        )
    
    return result

@router.post("/upload/with-template",
             summary="Upload files with template",
             description="""
             Upload multiple files along with a template file.
             
             **Template file requirements:**
             - Must be Excel (.xlsx) or PDF file
             - Will be used as a template for processing the data files
             
             **Data files requirements:**
             - Multiple Excel (.xlsx) or PDF files
             - Will be processed using the provided template
             
             **File size limit:** 50MB per file
             
             **Behavior:**
             - Template is uploaded first
             - If template upload fails, data files are not processed
             - Publishes message to RabbitMQ with both template and data file paths
             """)
async def upload_files_with_template(
    files: List[UploadFile] = File(..., description="Data files to upload (Excel or PDF only)"),
    template: UploadFile = File(..., description="Template file (Excel or PDF)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple files with a template file"""
    
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data files provided"
        )
    
    if not template.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No template file provided"
        )
    
    # Check for empty filenames
    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more files have no filename"
            )
    
    result = await file_service.upload_with_template(files, template, current_user.id)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/upload/with-template-sync",
             response_model=TemplateWithFilesResponse,
             summary="Upload files with template and generate report (Sync)",
             description="""
             Upload multiple files along with a template file and generate report synchronously.
             
             **Template file requirements:**
             - Must be Excel (.xlsx) or PDF file
             - Will be used as a template for processing the data files
             
             **Data files requirements:**
             - Multiple Excel (.xlsx) or PDF files
             - Will be processed using the provided template
             
             **File size limit:** 50MB per file
             
             **Behavior:**
             - Template is uploaded first
             - If template upload fails, data files are not processed
             - Calls external API synchronously to generate report
             - Saves generated report to storage/generated folder
             - Also publishes message to RabbitMQ for async processing
             - Returns both upload results and generated report information
             """)
async def upload_files_with_template_sync(
        template: UploadFile = File(..., description="Template file (Excel or PDF)"),
        files: List[UploadFile] = File(..., description="Data files to upload (Excel or PDF only)"),
        report_name: Optional[str] = Form(None, description="Name for the generated report"),
        current_user: User = Depends(get_current_user),
        _: Session = Depends(get_db)
) -> TemplateWithFilesResponse:
    """Upload multiple files with a template file and generate report synchronously"""
    
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data files provided"
        )
    
    if not template.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No template file provided"
        )
    
    # Check for empty filenames
    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more files have no filename"
            )
    
    result = await file_service.upload_with_template_and_generate(files, template, current_user.id, report_name)

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    if result["status"] == "partial_success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )

    return TemplateWithFilesResponse(
        template_upload=result["template_upload"],
        file_uploads=result["file_uploads"],
        generated_report=result.get("generated_report"),
        status=result["status"],
        message=result["message"]
    )

@router.post("/upload/with-template-sync2",
           response_model=TemplateWithFilesResponse,
           summary="Upload files with template and generate report (Extended version)",
           description="""
           Upload multiple files with a template and generate report synchronously.
           Extended version supports both new uploads and existing files/templates.
           
           **Extended Features:**
           - Can use existing uploaded files via file_ids parameter
           - Can use existing templates via template_id parameter
           - If both template file and template_id are provided, uploaded template takes priority
           - Can mix new file uploads with existing file IDs
           
           **Parameters:**
           - files: New data files to upload (Excel or PDF only) - optional
           - template: New template file to upload (Excel or PDF) - optional
           - file_ids: IDs of existing uploaded files to use - optional
           - template_id: ID of existing template to use - optional
           - report_name: Custom name for the generated report - optional
           
           **Requirements:**
           - At least one template source (template file OR template_id) must be provided
           - At least one data source (files OR file_ids) must be provided
           - Template file takes priority over template_id when both are provided
           
           **File size limit:** 50MB per file
           
           **Behavior:**
           - Template is processed first (upload or retrieve existing)
           - Data files are processed (upload new files and/or retrieve existing files)
           - Calls external API synchronously to generate report
           - Saves generated report to storage/generated folder
           - Also publishes message to RabbitMQ for async processing
           - Returns both upload results and generated report information
           
           **Security:** Users can only access their own files and templates (if access control is enabled).
           """)
async def upload_files_with_template_sync_extended(
        template: UploadFile = File(None, description="New template file (Excel or PDF)"),
        template_id: Optional[int] = Form(None, description="ID of existing template to use"),
        files: List[UploadFile] = File(None, description="New data files to upload (Excel or PDF only)"),
        file_ids: Optional[str] = Form(None, description="Comma-separated IDs of existing uploaded files to use (e.g., '1,2,3')"),
        report_name: Optional[str] = Form(None, description="Name for the generated report"),
        current_user: User = Depends(get_current_user),
        _: Session = Depends(get_db)
) -> TemplateWithFilesResponse:
    """Upload files with template and generate report synchronously (Extended version)"""

    # Parse file_ids from comma-separated string to list of integers
    parsed_file_ids = None
    if file_ids:
        try:
            # Remove whitespace and split by comma, then convert to integers
            parsed_file_ids = [int(x.strip()) for x in file_ids.split(',') if x.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file_ids format. Use comma-separated integers (e.g., '1,2,3')"
            )

    # Validate that at least one template source is provided
    if not template and not template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one template source must be provided: either upload a template file or provide template_id"
        )

    # Validate that at least one data source is provided
    if (not files or len(files) == 0) and (not parsed_file_ids or len(parsed_file_ids) == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one data source must be provided: either upload files or provide file_ids"
        )

    # Check for empty filenames in uploaded files
    if files:
        for file in files:
            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more uploaded files have no filename"
                )

    # Check template filename if provided
    if template and not template.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template file has no filename"
        )

    result = await file_service.upload_with_template_and_generate_extended(
        files=files,
        template_file=template,
        file_ids=parsed_file_ids,
        template_id=template_id,
        user_id=current_user.id,
        report_name=report_name
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    if result["status"] == "partial_success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )

    return TemplateWithFilesResponse(
        template_upload=result["template_upload"],
        file_uploads=result["file_uploads"],
        generated_report=result.get("generated_report"),
        status=result["status"],
        message=result["message"]
    )

@router.post("/upload/with-template-sync-new",
           response_model=TemplateWithFilesResponse,
           summary="Upload NEW files with template and generate report",
           description="""
           Upload NEW files and template, generate report synchronously.
           This endpoint requires both files and template to be uploaded.
           """)
async def upload_new_files_with_template_sync(
    files: List[UploadFile] = File(..., description="New data files to upload (Excel or PDF only)"),
    template: UploadFile = File(..., description="New template file (Excel or PDF)"),
    report_name: Optional[str] = Form(None, description="Name for the generated report"),
    current_user: User = Depends(get_current_user),
    _: Session = Depends(get_db)
) -> TemplateWithFilesResponse:
    """Upload NEW files with template and generate report synchronously"""

    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data files provided"
        )

    if not template.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No template file provided"
        )

    # Check for empty filenames
    for file in files:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more files have no filename"
            )

    result = await file_service.upload_with_template_and_generate_extended(
        files=files,
        template_file=template,
        file_ids=None,
        template_id=None,
        user_id=current_user.id,
        report_name=report_name
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    if result["status"] == "partial_success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )

    return TemplateWithFilesResponse(
        template_upload=result["template_upload"],
        file_uploads=result["file_uploads"],
        generated_report=result.get("generated_report"),
        status=result["status"],
        message=result["message"]
    )

@router.post("/upload/with-template-sync-existing",
           response_model=TemplateWithFilesResponse,
           summary="Use EXISTING files/template and generate report",
           description="""
           Use existing uploaded files and/or template to generate report synchronously.
           This endpoint uses file IDs instead of file uploads.
           """)
async def use_existing_files_with_template_sync(
    file_ids: str = Form(..., description="Comma-separated IDs of existing uploaded files to use (e.g., '1,2,3')"),
    template_id: int = Form(..., description="ID of existing template to use"),
    report_name: Optional[str] = Form(None, description="Name for the generated report"),
    current_user: User = Depends(get_current_user),
    _: Session = Depends(get_db)
) -> TemplateWithFilesResponse:
    """Use existing files and template to generate report synchronously"""

    # Parse file_ids from comma-separated string to list of integers
    try:
        parsed_file_ids = [int(x.strip()) for x in file_ids.split(',') if x.strip()]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file_ids format. Use comma-separated integers (e.g., '1,2,3')"
        )

    if not parsed_file_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file ID must be provided"
        )

    result = await file_service.upload_with_template_and_generate_extended(
        files=None,
        template_file=None,
        file_ids=parsed_file_ids,
        template_id=template_id,
        user_id=current_user.id,
        report_name=report_name
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    if result["status"] == "partial_success":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )

    return TemplateWithFilesResponse(
        template_upload=result["template_upload"],
        file_uploads=result["file_uploads"],
        generated_report=result.get("generated_report"),
        status=result["status"],
        message=result["message"]
    )

@router.get("/list",
           summary="List uploaded files", 
           description="Get list of all files uploaded by the current user")
async def list_user_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10000
):
    """List files uploaded by current user"""
    from .FileUploadModel import UploadedFile, ResponseListFile
    
    # files = db.query(UploadedFile).filter(
    #     UploadedFile.uploaded_by == current_user.id
    # ).offset(skip).limit(limit).all()

    files = db.query(UploadedFile).order_by(UploadedFile.uploaded_at.desc()).offset(skip).limit(limit).all()
    dir_name = {}
    for file in files:
        user = user_service.get_user_by_id(db, file.uploaded_by)
        dir_name[file.uploaded_by] = f"{user.first_name or ''} {user.last_name or ''}".strip()

    response_files = [
        ResponseListFile(
            id=str(file.id),
            original_filename=file.original_filename,
            stored_filename=file.stored_filename,
            file_path=file.file_path,
            file_type=file.file_type,
            file_size=str(file.file_size),
            mimetype=file.mimetype,
            uploaded_by=str(file.uploaded_by),
            uploaded_at=file.uploaded_at.isoformat(),
            status=file.status,
            error_message=file.error_message or "",
            uploader=dir_name.get(file.uploaded_by, "Unknown")
        )
        for file in files
    ]
    
    return {
        "files": response_files,
        "total": len(files),
        "user_id": current_user.id
    }

@router.delete("/{file_id}",
              summary="Delete uploaded file",
              description="Delete a file uploaded by the current user")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an uploaded file"""
    from .FileUploadModel import UploadedFile
    import os
    
    # Find file owned by current user
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        # UploadedFile.uploaded_by == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or not owned by current user"
        )
    
    # Delete physical file
    try:
        file_path = str(file_record.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log error but continue with database deletion
        pass
    
    # Delete database record
    db.delete(file_record)
    db.commit()
    
    return {"message": "File deleted successfully", "file_id": file_id}

@router.get("/{file_id}/download",
           summary="Download uploaded file",
           description="Download a file by its ID. Only the user who uploaded the file can download it.")
async def download_file(
    file_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download an uploaded file"""
    from .FileUploadModel import UploadedFile
    from fastapi.responses import FileResponse
    import os

    # Find file owned by current user
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
    ).first()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or not owned by current user"
        )

    # Check if physical file exists
    file_path = str(file_record.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical file not found on server"
        )

    # Return file for download
    return FileResponse(
        path=file_path,
        filename=str(file_record.original_filename),
        media_type=str(file_record.mimetype)
    )
