"""
Template database model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from config.database import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False, default="1.0")
    created_by = Column(Integer, nullable=False)  # User ID who created the template
    modified_by = Column(Integer, nullable=True) # User ID who last modified the template
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, category={self.category}, version={self.version})>"
