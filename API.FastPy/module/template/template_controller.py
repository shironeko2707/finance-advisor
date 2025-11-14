from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from module.template.TemplateDTO import (
    TemplateCreateDTO, TemplateUpdateDTO, TemplateResponseDTO,
    TemplateListResponseDTO, TemplateUploadDTO
)
from module.template.template_service import template_service
from module.user_auth.provider.user import get_current_user
from module.user_mgmt.UserModel import User
import logging

router = APIRouter(
    prefix="/templates",
    tags=["Template Management"],
    responses={404: {"description": "Template not found"}}
)

@router.post(
    "/upload",
    response_model=TemplateResponseDTO,
    status_code=201,
    summary="Upload a new template file",
    description="""
    Upload a template file to the system.
    
    **Required Fields:**
    - `file`: Template file (Excel, Word, PDF, PowerPoint formats supported)
    - `name`: Template name (3-255 characters)
    - `category`: Template category for organization
    
    **Optional Fields:**
    - `version`: Template version (default: "1.0")
    
    **Supported File Types:**
    - Excel: .xlsx, .xls
    - Word: .docx, .doc
    - PDF: .pdf
    - PowerPoint: .pptx, .ppt
    
    **Example:**
    Upload a file with form data including name="Monthly Report" and category="Reports"
    """,
    response_description="The uploaded template information"
)
async def upload_template(
    file: UploadFile = File(..., description="Template file to upload"),
    name: str = Form(..., description="Template name"),
    category: str = Form(..., description="Template category"),
    version: str = Form("1.0", description="Template version"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new template file"""
    try:
        template_data = TemplateUploadDTO(
            name=name,
            category=category,
            version=version
        )
        return template_service.upload_template(db, file, template_data, current_user.id)
    except Exception as e:
        logging.error(f"Error uploading template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading template: {str(e)}")

@router.get(
    "",
    response_model=TemplateListResponseDTO,
    summary="Get templates with pagination and filtering",
    description="""
    Retrieve templates with optional filtering and pagination.
    
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `size`: Items per page (1-100, default: 10)
    - `category`: Filter by category
    - `search`: Search in template name and category
    
    **Example:**
    - Get all templates: `/templates`
    - Filter by category: `/templates?category=Reports`
    - Search templates: `/templates?search=monthly`
    - Pagination: `/templates?page=2&size=20`
    """,
    response_description="List of templates with pagination info"
)
def get_templates(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get templates with pagination and filtering"""
    return template_service.get_templates(db, page, size, category, search)

@router.get(
    "/{template_id}",
    response_model=TemplateResponseDTO,
    summary="Get template by ID",
    description="Retrieve detailed information about a specific template by its ID.",
    response_description="Template information"
)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get template by ID"""
    return template_service.get_template_by_id(db, template_id)

@router.get(
    "/{template_id}/download",
    response_class=FileResponse,
    summary="Download template file",
    description="""
    Download a template file by its ID.
    
    **Response:**
    - Returns the actual template file with original filename
    - Content-Type: application/octet-stream
    - Content-Disposition: attachment with original filename
    
    **Example:**
    GET `/templates/123/download` will download the template file with ID 123
    
    **Error Cases:**
    - 404: Template not found
    - 404: Template file not found on server
    """,
    response_description="Template file download"
)
def download_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download template file"""
    return template_service.download_template(db, template_id)

@router.put(
    "/{template_id}",
    response_model=TemplateResponseDTO,
    summary="Update template information",
    description="""
    Update template information (name, category, version).
    
    **Note:** This endpoint updates template metadata only, not the file itself.
    To update the file, delete the template and upload a new one.
    
    **Updateable Fields:**
    - `name`: Template name
    - `category`: Template category
    - `version`: Template version
    
    All fields are optional for partial updates.
    """,
    response_description="Updated template information"
)
def update_template(
    template_id: int,
    template_update: TemplateUpdateDTO,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update template information"""
    return template_service.update_template(db, template_id, template_update)

@router.delete(
    "/{template_id}",
    summary="Delete template",
    description="""
    Delete a template and its associated file from the system.
    
    **Warning:** This action is irreversible. The template file will be permanently deleted.
    """,
    response_description="Deletion confirmation message"
)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete template"""
    return template_service.delete_template(db, template_id)

@router.get(
    "/categories/list",
    response_model=List[str],
    summary="Get all template categories",
    description="Retrieve a list of all unique template categories in the system.",
    response_description="List of template categories"
)
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all template categories"""
    return template_service.get_categories(db)

@router.get(
    "/category/{category}",
    response_model=List[TemplateResponseDTO],
    summary="Get templates by category",
    description="Retrieve all templates in a specific category.",
    response_description="List of templates in the specified category"
)
def get_templates_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get templates by category"""
    return template_service.get_templates_by_category(db, category)

@router.get(
    "/user/my-templates",
    response_model=List[TemplateResponseDTO],
    summary="Get current user's templates",
    description="Retrieve all templates created by the current user.",
    response_description="List of templates created by the current user"
)
def get_my_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get templates created by current user"""
    return template_service.get_templates_by_user(db, current_user.id)
