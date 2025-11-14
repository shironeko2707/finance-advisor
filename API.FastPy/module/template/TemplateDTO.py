from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class TemplateCreateDTO(BaseModel):
    """
    DTO for creating a new template

    Required fields:
    - name: Template name (3-255 characters)
    - file_name: Original file name
    - file_path: Path where template file is stored
    - category: Template category for organization
    - created_by: User ID who created the template
    - modified_by: User ID who last modified the template (optional)

    Optional fields:
    - version: Template version (default: "1.0")
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="**REQUIRED** - Template name must be between 3-255 characters",
        example="Monthly Report Template"
    )
    file_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="**REQUIRED** - Original file name",
        example="monthly_report_template.xlsx"
    )
    file_path: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="**REQUIRED** - File path where template is stored",
        example="/storage/templates/monthly_report_template.xlsx"
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="**REQUIRED** - Template category for organization",
        example="Reports"
    )
    created_by: int = Field(
        ...,
        gt=0,
        description="**REQUIRED** - User ID who created the template",
        example=1
    )
    modified_by: Optional[int] = Field(
        None,
        gt=0,
        description="**OPTIONAL** - User ID who last modified the template",
        example=1
    )
    version: Optional[str] = Field(
        "1.0",
        max_length=50,
        description="**OPTIONAL** - Template version (default: '1.0')",
        example="1.0"
    )

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Template name cannot be empty or whitespace only')
        return v.strip()

    @validator('category')
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError('Category cannot be empty or whitespace only')
        return v.strip()

    @validator('file_name')
    def validate_file_name(cls, v):
        # Basic file name validation
        if not re.match(r'^[^<>:"/\\|?*]+\.[a-zA-Z0-9]+$', v):
            raise ValueError('Invalid file name format')
        return v

class TemplateUpdateDTO(BaseModel):
    """
    DTO for updating an existing template
    All fields are optional for partial updates
    """

    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Template name",
        example="Updated Monthly Report Template"
    )
    category: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Template category",
        example="Financial Reports"
    )
    version: Optional[str] = Field(
        None,
        max_length=50,
        description="Template version",
        example="2.0"
    )
    modified_by: Optional[int] = Field(
        None,
        gt=0,
        description="User ID who last modified the template",
        example=1
    )

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Template name cannot be empty or whitespace only')
        return v.strip() if v else v

    @validator('category')
    def validate_category(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Category cannot be empty or whitespace only')
        return v.strip() if v else v

class TemplateResponseDTO(BaseModel):
    """
    DTO for template response data
    """

    id: int
    name: str
    file_name: str
    file_path: str
    category: str
    version: str
    created_by: int
    creator_name: Optional[str] = None # Name of the user who created the template
    modified_by: Optional[int] = None
    modifier_name: Optional[str] = None # Name of the user who last modified the template
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class TemplateListResponseDTO(BaseModel):
    """
    DTO for template list response with pagination info
    """

    templates: list[TemplateResponseDTO]
    total: int
    page: int
    size: int
    total_pages: int

class TemplateUploadDTO(BaseModel):
    """
    DTO for template file upload
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Template name",
        example="New Template"
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Template category",
        example="Reports"
    )
    version: Optional[str] = Field(
        "1.0",
        max_length=50,
        description="Template version",
        example="1.0"
    )

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Template name cannot be empty or whitespace only')
        return v.strip()

    @validator('category')
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError('Category cannot be empty or whitespace only')
        return v.strip()
