"""
Template module for managing template files and metadata.

This module provides functionality for:
- Uploading template files
- Managing template information (name, category, version)
- Retrieving templates with filtering and pagination
- Updating template metadata
- Deleting templates and their files
"""

from .TemplateModel import Template
from .TemplateDTO import (
    TemplateCreateDTO,
    TemplateUpdateDTO,
    TemplateResponseDTO,
    TemplateListResponseDTO,
    TemplateUploadDTO
)
from .template_repository import template_repository
from .template_service import template_service
from .template_controller import router

__all__ = [
    'Template',
    'TemplateCreateDTO',
    'TemplateUpdateDTO',
    'TemplateResponseDTO',
    'TemplateListResponseDTO',
    'TemplateUploadDTO',
    'template_repository',
    'template_service',
    'router'
]
