"""
Auto Report System

A system for generating automated reports from PDF documents using Azure AI
with RabbitMQ integration for microservice communication.
"""

from .main import main, index_document, load_template
from .helpers import write_fill_in_values_to_worksheet
from .messaging import ReportService, ReportRequest, ReportResponse, RabbitMQConfig
from .client import ReportClient

__version__ = "0.1.0"
__all__ = [
    "main",
    "index_document", 
    "load_template",
    "write_fill_in_values_to_worksheet",
    "ReportService",
    "ReportClient",
    "ReportRequest",
    "ReportResponse",
    "RabbitMQConfig"
]