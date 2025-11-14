from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# from dotenv import load_dotenv
# load_dotenv()  # Load environment variables from .env file

# Ensure storage directory exists
storage_dir = Path("storage")
storage_dir.mkdir(exist_ok=True)

def validate_database_config():
    """Validate database configuration based on environment"""
    is_production = os.getenv('IS_PRODUCTION', 'true').lower() == 'true'
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./storage/lengkeng.db')

    print(f"Using database URL: {database_url}")

    if is_production and database_url.startswith('sqlite'):
        raise ValueError(
            "SQLite database is not allowed in production environment. "
            "Please configure PostgreSQL by setting DATABASE_URL environment variable."
        )
    
    return database_url

# Database configuration
# Default to SQLite in storage directory for development/testing, use PostgreSQL in production
DATABASE_URL = validate_database_config()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()