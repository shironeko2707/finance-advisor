import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base, get_db
from main import app

# Import models to ensure they are registered with Base

# Create a temporary database file for testing
temp_db_file = None
test_engine = None
TestingSessionLocal = None

def get_test_engine():
    global test_engine, temp_db_file
    if test_engine is None:
        # Create a temporary database file
        temp_db_fd, temp_db_file = tempfile.mkstemp(suffix='.db')
        os.close(temp_db_fd)  # Close the file descriptor, but keep the file
        
        SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{temp_db_file}"
        test_engine = create_engine(
            SQLALCHEMY_TEST_DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=test_engine)
    return test_engine

def get_test_session_maker():
    global TestingSessionLocal
    if TestingSessionLocal is None:
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_test_engine())
    return TestingSessionLocal

def override_get_db():
    """Override database session for testing"""
    SessionLocal = get_test_session_maker()
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_client():
    """Create a test client with a temporary database"""
    # Ensure database is set up
    engine = get_test_engine()
    
    # Clear any existing data by dropping and recreating tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_db():
    """Create a test database session"""
    engine = get_test_engine()
    SessionLocal = get_test_session_maker()
    
    # Clear any existing data
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Clean up temporary database file at the end of the session
def pytest_sessionfinish(session, exitstatus):
    """Clean up temporary database file"""
    global temp_db_file
    if temp_db_file and os.path.exists(temp_db_file):
        try:
            os.unlink(temp_db_file)
        except OSError:
            pass
