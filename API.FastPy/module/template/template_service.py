from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from module.template.TemplateDTO import (
    TemplateCreateDTO, TemplateUpdateDTO, TemplateResponseDTO,
    TemplateListResponseDTO, TemplateUploadDTO
)
from module.template.template_repository import template_repository
import os
import uuid
import shutil
import math

class TemplateService:

    def __init__(self):
        self.template_repository = template_repository
        self.upload_dir = "storage/templates"
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)

    def create_template(self, db: Session, template: TemplateCreateDTO) -> TemplateResponseDTO:
        """
        Create a new template with business logic validation.

        - Validates template name uniqueness
        - Creates the template record
        """
        # Check if template name already exists
        if self.template_repository.check_name_exists(db, template.name):
            raise HTTPException(status_code=400, detail="Template name already exists")

        # Create the template
        db_template = self.template_repository.create_template(db, template)
        return TemplateResponseDTO.model_validate(db_template)

    def upload_template(self, db: Session, file: UploadFile, template_data: TemplateUploadDTO,
                       user_id: int) -> TemplateResponseDTO:
        """
        Upload a template file and create template record.

        - Validates file type
        - Saves file to storage
        - Creates template record
        """
        # Validate file type (allow common document types)
        allowed_extensions = {'.xlsx', '.xls', '.docx', '.doc', '.pdf', '.pptx', '.ppt'}
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Check if template name already exists
        if self.template_repository.check_name_exists(db, template_data.name):
            raise HTTPException(status_code=400, detail="Template name already exists")

        try:
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            file_name = f"{unique_id}_{file.filename}"
            file_path = os.path.join(self.upload_dir, file_name)

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Create template record
            template_create = TemplateCreateDTO(
                name=template_data.name,
                file_name=file.filename,
                file_path=file_path,
                category=template_data.category,
                version=template_data.version,
                created_by=user_id
            )

            db_template = self.template_repository.create_template(db, template_create)
            return TemplateResponseDTO.model_validate(db_template)

        except Exception as e:
            # Clean up file if template creation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error uploading template: {str(e)}")

    def get_template_by_id(self, db: Session, template_id: int) -> TemplateResponseDTO:
        """Get template by ID"""
        db_template = self.template_repository.get_template_by_id(db, template_id)
        if not db_template:
            raise HTTPException(status_code=404, detail="Template not found")
        return TemplateResponseDTO.model_validate(db_template)

    def get_templates(self, db: Session, page: int = 1, size: int = 10,
                     category: Optional[str] = None, search: Optional[str] = None) -> TemplateListResponseDTO:
        """Get templates with pagination and filtering"""
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 10

        skip = (page - 1) * size

        # Get templates and total count
        templates = self.template_repository.get_templates(db, skip, size, category, search)
        total = self.template_repository.get_templates_count(db, category, search)

        # Calculate total pages
        total_pages = math.ceil(total / size) if total > 0 else 0

        template_responses = []
        for template in templates:
            template_response = TemplateResponseDTO.model_validate(template)
            # Manually assign creator_name and modifier_name if they were added by the repository
            if hasattr(template, 'creator_name'):
                template_response.creator_name = template.creator_name
            if hasattr(template, 'modifier_name'):
                template_response.modifier_name = template.modifier_name
            template_responses.append(template_response)

        return TemplateListResponseDTO(
            templates=template_responses,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )

    def get_templates_by_category(self, db: Session, category: str) -> List[TemplateResponseDTO]:
        """Get all templates in a specific category"""
        templates = self.template_repository.get_templates_by_category(db, category)
        return [TemplateResponseDTO.model_validate(template) for template in templates]

    def get_templates_by_user(self, db: Session, user_id: int) -> List[TemplateResponseDTO]:
        """Get all templates created by a specific user"""
        templates = self.template_repository.get_templates_by_user(db, user_id)
        return [TemplateResponseDTO.model_validate(template) for template in templates]

    def get_categories(self, db: Session) -> List[str]:
        """Get all unique template categories"""
        return self.template_repository.get_categories(db)

    def update_template(self, db: Session, template_id: int, template_update: TemplateUpdateDTO) -> TemplateResponseDTO:
        """Update an existing template"""
        # Check if template exists
        existing_template = self.template_repository.get_template_by_id(db, template_id)
        if not existing_template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Check name uniqueness if name is being updated
        if template_update.name and template_update.name != existing_template.name:
            if self.template_repository.check_name_exists(db, template_update.name, exclude_id=template_id):
                raise HTTPException(status_code=400, detail="Template name already exists")

        # Update template
        updated_template = self.template_repository.update_template(db, template_id, template_update)
        return TemplateResponseDTO.model_validate(updated_template)

    def delete_template(self, db: Session, template_id: int) -> dict:
        """Delete a template and its associated file"""
        # Get template to access file path
        db_template = self.template_repository.get_template_by_id(db, template_id)
        if not db_template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Delete file if it exists
        if os.path.exists(db_template.file_path):
            try:
                os.remove(db_template.file_path)
            except Exception as e:
                # Log error but continue with database deletion
                print(f"Warning: Could not delete file {db_template.file_path}: {str(e)}")

        # Delete from database
        success = self.template_repository.delete_template(db, template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")

        return {"message": "Template deleted successfully"}

    def download_template(self, db: Session, template_id: int) -> FileResponse:
        """Download a template file"""
        # Get template by ID
        db_template = self.template_repository.get_template_by_id(db, template_id)
        if not db_template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Check if file exists
        if not os.path.exists(db_template.file_path):
            raise HTTPException(status_code=404, detail="Template file not found on server")

        # Return file response
        return FileResponse(
            path=db_template.file_path,
            filename=db_template.file_name,
            media_type='application/octet-stream'
        )

# Create a global instance to be imported by other modules
template_service = TemplateService()
