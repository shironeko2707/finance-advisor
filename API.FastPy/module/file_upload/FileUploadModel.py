"""
File upload database model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from config.database import Base
from datetime import datetime
from pydantic import BaseModel

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # excel, pdf
    file_size = Column(Integer, nullable=False)
    mimetype = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, nullable=True)  # User ID who uploaded
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="success")  # success, error, processing
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename={self.original_filename}, type={self.file_type})>"
    
class ResponseListFile(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: str
    file_size: str
    mimetype: str
    uploaded_by: str
    uploaded_at: str
    status: str
    error_message: str
    uploader: str

