"""
LoginDTO Module - Authentication Login Data Transfer Objects

This module contains DTOs specifically for login functionality.
Other authentication DTOs will be organized in separate files:
- LogoutDTO.py: For logout functionality  
- ForgetDTO.py: For password reset functionality
- etc.

Created: August 2025
"""

from pydantic import BaseModel, Field

class AuthLoginDTO(BaseModel):
    """
    DTO for user login request
    
    Required fields for authentication:
    - username: User's unique username or email
    - password: User's password
    """
    username: str = Field(
        ..., 
        description="**REQUIRED** - Username or email for authentication",
        example="admin"
    )
    password: str = Field(
        ..., 
        description="**REQUIRED** - User password", 
        example="admin123"
    )

class AuthResponseDTO(BaseModel):
    """
    DTO for successful authentication response
    
    Contains JWT token and user information for authorized access
    """
    access_token: str = Field(
        ..., 
        description="JWT access token for API authentication"
    )
    token_type: str = Field(
        default="bearer", 
        description="Token type (always 'bearer')"
    )
    expires_in: int = Field(
        ..., 
        description="Token expiration time in seconds"
    )
    user_id: int = Field(
        ..., 
        description="Unique identifier for the authenticated user"
    )
    username: str = Field(
        ..., 
        description="Username of the authenticated user"
    )
    role: str = Field(
        ..., 
        description="User role for authorization purposes"
    )

class AuthTokenPayloadDTO(BaseModel):
    """
    DTO for JWT token payload structure
    
    Internal model for token validation and user session management
    """
    sub: str = Field(
        ..., 
        description="Subject (user ID) from the token"
    )
    username: str = Field(
        ..., 
        description="Username from the token"
    )
    role: str = Field(
        ..., 
        description="User role from the token"
    )
    exp: int = Field(
        ..., 
        description="Token expiration timestamp"
    )
    iat: int = Field(
        ..., 
        description="Token issued at timestamp"
    )
