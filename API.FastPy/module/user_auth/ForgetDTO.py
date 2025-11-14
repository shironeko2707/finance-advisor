"""
ForgetDTO Module - Password Reset Data Transfer Objects

This module contains DTOs specifically for password reset functionality.
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class ForgotPasswordRequestDTO(BaseModel):
    """DTO for password reset request"""
    email: EmailStr = Field(..., description="User email to receive OTP")

class ForgotPasswordResponseDTO(BaseModel):
    """DTO for password reset response"""
    success: bool = Field(..., description="OTP sending status")
    message: str = Field(..., description="Result message")

class ValidateOTPRequestDTO(BaseModel):
    """DTO for OTP validation"""
    email: EmailStr = Field(..., description="User email")
    otp_code: str = Field(..., min_length=4, max_length=4, description="4-digit OTP code")

class ValidateOTPResponseDTO(BaseModel):
    """DTO for OTP validation response"""
    success: bool = Field(..., description="OTP validation status")
    message: str = Field(..., description="Result message")
    reset_token: Optional[str] = Field(default=None, description="Password reset token (if successful)")

class ResetPasswordRequestDTO(BaseModel):
    """DTO for setting new password"""
    password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    repassword: str = Field(..., description="Confirm new password")
    reset_token: str = Field(..., description="Password reset verification token")

class ResetPasswordResponseDTO(BaseModel):
    """DTO for password reset response"""
    success: bool = Field(..., description="Password reset status")
    message: str = Field(..., description="Result message")
