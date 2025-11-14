"""
Test configuration module
Handles different database configurations for testing
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base

class TestConfig:
    """Test configuration settings"""
    
    # Use in-memory SQLite for fastest tests
    TEST_DATABASE_URL = "sqlite:///:memory:"
    
    # Alternative: Use temporary file database
    # TEST_DATABASE_URL = "sqlite:///./test_temp.db"
    
    # For integration tests, you might want to use a separate test database
    # TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    
    @classmethod
    def get_test_engine(cls):
        """Get database engine for testing"""
        return create_engine(
            cls.TEST_DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in cls.TEST_DATABASE_URL else {}
        )
    
    @classmethod
    def get_test_session_local(cls):
        """Get session local for testing"""
        engine = cls.get_test_engine()
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    @classmethod
    def create_test_tables(cls, engine):
        """Create all tables for testing"""
        Base.metadata.create_all(bind=engine)
    
    @classmethod
    def drop_test_tables(cls, engine):
        """Drop all tables after testing"""
        Base.metadata.drop_all(bind=engine)
