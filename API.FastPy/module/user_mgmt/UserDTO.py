from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re
from module.user_mgmt.UserModel import UserRole, UserStatus

class UserCreateDTO(BaseModel):
    """
    DTO for creating a new user
    
    Required fields:
    - username: Unique username (6-50 characters, alphanumeric and underscores only)
    - email: Valid email address (must be unique in the system)
    
    Optional fields:
    - password: User password (default: randomly generated 6-character string if not provided)
    - role: User role (default: 'User')
    - status: User status (default: 'Active')
    - first_name, last_name, job_title: Additional user information
    """
    
    # Required fields
    username: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="**REQUIRED** - Username must be between 6-50 characters, containing only letters, numbers, and underscores",
        example="johndoe123"
    )
    email: EmailStr = Field(
        ..., 
        description="**REQUIRED** - Valid email address format required. Must be unique in the system.",
        example="john.doe@example.com"
    )
    
    # Optional fields with defaults
    password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=50,
        description="**OPTIONAL** - Password (6-50 characters). If not provided, a random 6-character password will be generated automatically.",
        example="securepassword123"
    )
    first_name: Optional[str] = Field(
        None, 
        max_length=50,
        description="**OPTIONAL** - User's first name",
        example="John"
    )
    last_name: Optional[str] = Field(
        None, 
        max_length=50,
        description="**OPTIONAL** - User's last name",
        example="Doe"
    )
    job_title: Optional[str] = Field(
        None, 
        max_length=100,
        description="**OPTIONAL** - User's job title",
        example="Software Engineer"
    )
    role: Optional[UserRole] = Field(
        UserRole.USER, 
        description="**OPTIONAL** - User's role in the system (default: 'User')",
        example="User"
    )
    status: Optional[UserStatus] = Field(
        UserStatus.ACTIVE, 
        description="**OPTIONAL** - User's current status (default: 'Active')",
        example="Active"
    )

    @validator('email')
    def validate_email_format(cls, v):
        # Additional email validation if needed
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(v)):
            raise ValueError('Invalid email format')
        return v

    @validator('username')
    def validate_username(cls, v):
        # Username should contain only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 6:
                raise ValueError('Password must be at least 6 characters long')
            if len(v) > 50:
                raise ValueError('Password must not exceed 50 characters')
            # Optional: Add more password strength requirements
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('Password must contain at least one letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
        return v

class UserUpdateDTO(BaseModel):
    """
    DTO for updating an existing user
    
    All fields are optional - only provide the fields you want to change.
    Any field not provided will remain unchanged in the database.
    
    Field validation and uniqueness constraints:
    - username: Must be unique across all users
    - email: Must be unique and valid format
    - password: Will be securely hashed before storage
    """
    
    username: Optional[str] = Field(
        None,
        min_length=6,
        max_length=50,
        description="**OPTIONAL** - New username (6-50 characters, alphanumeric and underscores only). Must be unique across all users.",
        example="johndoe123"
    )
    first_name: Optional[str] = Field(
        None, 
        max_length=50,
        description="**OPTIONAL** - User's first name (1-50 characters)",
        example="Jonathan"
    )
    last_name: Optional[str] = Field(
        None, 
        max_length=50,
        description="**OPTIONAL** - User's last name (1-50 characters)",
        example="Doe-Smith"
    )
    email: Optional[EmailStr] = Field(
        None, 
        description="**OPTIONAL** - Valid email address. Must be unique across all users.",
        example="jonathan.doe@newcompany.com"
    )
    job_title: Optional[str] = Field(
        None, 
        max_length=100,
        description="**OPTIONAL** - User's job title or position (up to 100 characters)",
        example="Senior Software Engineer"
    )
    role: Optional[UserRole] = Field(
        None, 
        description="**OPTIONAL** - User's system role. Available options: User, Admin, Moderator",
        example="Admin"
    )
    status: Optional[UserStatus] = Field(
        None, 
        description="**OPTIONAL** - User's account status. Available options: Active, Inactive, Pending",
        example="Active"
    )
    password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=50,
        description="**OPTIONAL** - New password (6-50 characters, must contain at least one letter and one number). Will be securely hashed before storage.",
        example="newSecurePassword789"
    )

    @validator('email')
    def validate_email_format(cls, v):
        if v is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(v)):
                raise ValueError('Invalid email format')
        return v

    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 6:
                raise ValueError('Password must be at least 6 characters long')
            if len(v) > 50:
                raise ValueError('Password must not exceed 50 characters')
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('Password must contain at least one letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
        return v

class UserResponseDTO(BaseModel):
    """DTO for user response containing all user information (excluding password for security)"""
    
    id: int = Field(
        ..., 
        description="Unique identifier for the user",
        example=1
    )
    username: str = Field(
        ...,
        description="Username of the user",
        example="johndoe123"
    )
    first_name: Optional[str] = Field(
        None, 
        description="User's first name",
        example="John"
    )
    last_name: Optional[str] = Field(
        None, 
        description="User's last name",
        example="Doe"
    )
    email: EmailStr = Field(
        ..., 
        description="User's email address",
        example="john.doe@example.com"
    )
    job_title: Optional[str] = Field(
        None, 
        description="User's job title",
        example="Software Engineer"
    )
    role: UserRole = Field(
        ..., 
        description="User's role in the system",
        example="User"
    )
    status: UserStatus = Field(
        ..., 
        description="User's current status",
        example="Active"
    )
    created_at: datetime = Field(
        ..., 
        description="Timestamp when the user was created",
        example="2023-01-15T10:30:00Z"
    )
    updated_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when the user was last updated",
        example="2023-01-20T14:45:00Z"
    )

    class Config:
        from_attributes = True

# Backward compatibility aliases (to avoid breaking existing imports)
UserBase = UserResponseDTO  # Changed from UserBaseDTO to avoid conflicts
UserCreate = UserCreateDTO
UserUpdate = UserUpdateDTO
UserResponse = UserResponseDTO
