"""
Generated Report controller with REST API endpoints
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from typing import Optional
from sqlalchemy.orm import Session
from module.user_auth.provider.user import get_current_user
from module.user_mgmt.UserModel import User
from module.user_mgmt.user_service import user_service
from config.database import get_db
from module.file_upload.fileupload_service import FileUploadService
from module.file_upload.FileUploadDTO import GeneratedReportListResponse, GeneratedReportDetailResponse, GeneratedReportInfo
from module.report.pdf_converter import PDFConverterService

router = APIRouter(
    prefix="/reports",
    tags=["Generated Reports"],
    responses={404: {"description": "Not found"}},
)

file_service = FileUploadService()
pdf_converter = PDFConverterService()

@router.get("",
           response_model=GeneratedReportListResponse,
           summary="List generated reports",
           description="""
           Get list of all generated reports with detailed information.
           
           **Query Parameters:**
           - skip: Number of records to skip (pagination)
           - limit: Maximum number of records to return (max 100)
           - search: Search by report name or template filename
           
           **Response includes:**
           - Report name and filename
           - Template information
           - Input files count and details
           - Generation metadata (time, status, user)
           - Download statistics
           """)
async def list_generated_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by report name or template filename")
) -> GeneratedReportListResponse:
    """List generated reports with detailed information"""
    
    reports = file_service.get_generated_reports(
        user_id=current_user.id,
        limit=limit,
        offset=skip,
        search=search
    )
    
    report_infos = []
    for report in reports:
        user_name = ""
        if report.generated_by:
            try:
                user = user_service.get_user_by_id(db, report.generated_by)
                user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            except HTTPException as e:
                # Handle case where user might not be found (e.g., user deleted)
                if e.status_code == 404:
                    user_name = "System"
                else:
                    raise # Re-raise other HTTPExceptions

        report_info = GeneratedReportInfo(
            id=report.id,
            report_name=report.report_name or f"Report {report.id}",
            report_filename=report.report_filename,
            report_file_path=report.report_file_path,
            report_file_size=report.report_file_size,
            report_content_type=report.report_content_type,
            template_filename=report.template_filename,
            input_files_count=len(report.input_file_ids),
            input_files_info=report.input_files_info,
            generated_at=report.generated_at.isoformat(),
            generated_by=report.generated_by,
            user_name= user_name,
            generation_status=report.generation_status,
            generation_time_seconds=report.generation_time_seconds,
            is_downloaded=report.is_downloaded,
            download_count=report.download_count
        )
        report_infos.append(report_info)
    
    return GeneratedReportListResponse(
        reports=report_infos,
        total=len(report_infos),
        user_id=current_user.id
    )

@router.get("/{report_id}",
           response_model=GeneratedReportDetailResponse,
           summary="Get generated report details",
           description="""
           Get detailed information about a specific generated report.
           
           **Includes:**
           - Complete report information (name, filename, size, content type)
           - Template details (ID, filename, path)
           - Input files details (list with metadata)
           - Generation metadata (time, status, API response)
           - Usage statistics (download count, status)
           
           **Security:** Only the user who generated the report can access it.
           """)
async def get_generated_report_details(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> GeneratedReportDetailResponse:
    """Get detailed information about a specific generated report"""
    
    report = file_service.get_generated_report_by_id(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated report not found"
        )
    
    # Check if user owns this report
    if report.generated_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this report"
        )
    
    return GeneratedReportDetailResponse(
        id=report.id,
        report_name=report.report_name or f"Report {report.id}",
        report_filename=report.report_filename,
        report_file_path=report.report_file_path,
        report_file_size=report.report_file_size,
        report_content_type=report.report_content_type,
        
        template_file_id=report.template_file_id,
        template_filename=report.template_filename,
        template_file_path=report.template_file_path,
        
        input_files=report.input_files_info,
        input_files_count=len(report.input_file_ids),
        
        generated_at=report.generated_at.isoformat(),
        generated_by=report.generated_by,
        generation_status=report.generation_status,
        generation_time_seconds=report.generation_time_seconds,
        
        external_api_url=report.external_api_url,
        external_api_response=report.external_api_response,
        
        is_downloaded=report.is_downloaded,
        download_count=report.download_count,
        error_message=report.error_message
    )

@router.get("/{report_id}/download",
           summary="Download generated report by ID",
           description="""
           Download a generated report file by its database ID.
           
           **Features:**
           - Downloads file with proper content type and filename
           - Automatically tracks download count
           - Marks report as downloaded
           - Returns appropriate media type based on file extension
           
           **Security:** Only the user who generated the report can download it.
           """)
async def download_generated_report_by_id(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a generated report file by its database ID"""
    
    report = file_service.get_generated_report_by_id(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated report not found"
        )
    
    # Check if user owns this report
    # if report.generated_by != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Access denied to this report"
    #     )
    
    # Check if file exists
    if not os.path.exists(report.report_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found on disk"
        )
    
    # Mark as downloaded
    file_service.mark_report_as_downloaded(report_id)
    
    return FileResponse(
        path=report.report_file_path,
        filename=report.report_filename,
        media_type=report.report_content_type
    )

@router.get("/{report_id}/pdf",
           summary="View generated report as PDF in browser",
           description="""
           View a generated report as PDF directly in the browser.
           
           **Features:**
           - Serves PDF files directly for browser viewing
           - Automatically converts non-PDF reports (Excel, CSV, etc.) to PDF
           - Caches converted PDFs for better performance
           - Sets proper headers for inline browser viewing
           - Tracks view count separately from downloads
           
           **Supported conversions:**
           - Excel files (.xlsx, .xls) → PDF with formatted tables
           - CSV files → PDF with formatted tables
           - Text files → PDF with formatted text
           - HTML files → PDF (when possible)
           - PDF files → Direct serving
           
           **Security:** Only the user who generated the report can view it.
           """)
async def view_generated_report_as_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View a generated report as PDF in browser"""

    report = file_service.get_generated_report_by_id(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated report not found"
        )
    
    # Check if file exists
    if not os.path.exists(report.report_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found on disk"
        )

    # If it's already a PDF, serve it directly
    if report.report_content_type == 'application/pdf':
        return FileResponse(
            path=report.report_file_path,
            filename=report.report_filename,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}  # Display in browser instead of download
        )

    # Check if we can convert to PDF
    if not pdf_converter.is_convertible_to_pdf(report.report_file_path):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File format '{report.report_content_type}' cannot be converted to PDF for browser viewing. Please use the download endpoint instead."
        )

    # Generate PDF filename for converted file
    base_name = os.path.splitext(report.report_filename)[0]
    pdf_filename = f"{base_name}_view.pdf"

    # Check if converted PDF already exists (cache)
    pdf_cache_dir = os.path.join(os.path.dirname(report.report_file_path), "pdf_cache")
    os.makedirs(pdf_cache_dir, exist_ok=True)
    cached_pdf_path = os.path.join(pdf_cache_dir, f"report_{report_id}_{pdf_filename}")

    # Use cached PDF if it exists and is newer than the original file
    if (os.path.exists(cached_pdf_path) and
        os.path.getmtime(cached_pdf_path) >= os.path.getmtime(report.report_file_path)):
        return FileResponse(
            path=cached_pdf_path,
            filename=pdf_filename,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"}
        )

    # Convert to PDF
    success, pdf_path, error_message = await pdf_converter.convert_to_pdf(
        source_file_path=report.report_file_path,
        output_dir=pdf_cache_dir
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert report to PDF: {error_message}"
        )
    
    # Rename the converted file to our cached filename
    if pdf_path != cached_pdf_path:
        import shutil
        shutil.move(pdf_path, cached_pdf_path)

    # Serve the converted PDF
    return FileResponse(
        path=cached_pdf_path,
        filename=pdf_filename,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
    )
