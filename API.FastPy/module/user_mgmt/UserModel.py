from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from config.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    USER = "User"

class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Will store hashed password
    first_name = Column(String(50), nullable=True)  # Made nullable to allow minimal user creation
    last_name = Column(String(50), nullable=True)   # Made nullable to allow minimal user creation
    email = Column(String(100), unique=True, index=True, nullable=False)
    job_title = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())