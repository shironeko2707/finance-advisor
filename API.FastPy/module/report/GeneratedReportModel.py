"""
Generated Report database model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Report file information
    report_name = Column(String(255), nullable=True)  # Display name for the report
    report_filename = Column(String(255), nullable=False)
    report_file_path = Column(String(500), nullable=False)
    report_file_size = Column(Integer, nullable=False)
    report_content_type = Column(String(100), nullable=False)
    
    # Template information
    template_file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)
    template_filename = Column(String(255), nullable=False)
    template_file_path = Column(String(500), nullable=False)
    
    # Input files information (JSON array of file IDs and paths)
    input_file_ids = Column(JSON, nullable=False)  # Array of file IDs
    input_files_info = Column(JSON, nullable=False)  # Array of file info objects
    
    # Generation metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, nullable=True)  # User ID who triggered generation
    generation_status = Column(String(50), default="success")  # success, error, processing
    generation_time_seconds = Column(Integer, nullable=True)  # Time taken to generate
    
    # External API response
    external_api_url = Column(String(500), nullable=True)
    external_api_response = Column(JSON, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Processing flags
    is_downloaded = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    
    # Relationships
    template_file = relationship("UploadedFile", foreign_keys=[template_file_id])
    
    def __repr__(self):
        return f"<GeneratedReport(id={self.id}, filename={self.report_filename}, status={self.generation_status})>"

class ReportInputFile(Base):
    __tablename__ = "report_input_files"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("generated_reports.id"), nullable=False)
    input_file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)
    
    # Relationships
    report = relationship("GeneratedReport", backref="input_file_relations")
    input_file = relationship("UploadedFile")
    
    def __repr__(self):
        return f"<ReportInputFile(report_id={self.report_id}, file_id={self.input_file_id})>"
