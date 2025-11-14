from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from config.database import get_db
from module.user_auth.LoginDTO import AuthLoginDTO, AuthResponseDTO
from module.user_auth.ForgetDTO import (
    ForgotPasswordRequestDTO, ForgotPasswordResponseDTO,
    ValidateOTPRequestDTO, ValidateOTPResponseDTO,
    ResetPasswordRequestDTO, ResetPasswordResponseDTO
)
from module.user_auth.provider.security import (
    verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_HOURS,
    generate_otp, create_reset_token, verify_reset_token, get_password_hash
)
from module.user_auth.provider.email import email_provider
from module.user_mgmt.UserModel import User
from module.user_auth.OTPModel import OTP

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Authentication failed"}}
)

@router.post(
    "/login",
    response_model=AuthResponseDTO,
    summary="User login",
    description="""
    Authenticate user with username/email and password.
    
    **Authentication Process:**
    - Validates username or email and password
    - Returns JWT access token with 8-hour expiration
    - Token includes user role for authorization
    
    **Token Details:**
    - **Expiration**: 8 hours from issue time
    - **Type**: Bearer token
    - **Usage**: Include in Authorization header as `Bearer <token>`
    
    **Example Request (Username):**
    ```json
    {
        "username": "admin",
        "password": "admin123"
    }
    ```
    
    **Example Request (Email):**
    ```json
    {
        "username": "admin@example.com",
        "password": "admin123"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 28800,
        "user_id": 1,
        "username": "admin",
        "role": "Admin"
    }
    ```
    """,
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJBZG1pbiIsImV4cCI6MTY5MjE4MDgwMCwiaWF0IjoxNjkyMTUyMDAwfQ.signature",
                        "token_type": "bearer",
                        "expires_in": 28800,
                        "user_id": 1,
                        "username": "admin",
                        "role": "Admin"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid username or password"}
                }
            }
        }
    }
)
def login(login_request: AuthLoginDTO, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token
    
    Args:
        login_request: Login credentials (username and password)
        db: Database session
    
    Returns:
        AuthResponseDTO: JWT token and user information
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by username or email
    user = db.query(User).filter(
        or_(User.username == login_request.username, User.email == login_request.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or email"
        )
    
    # Verify password
    if not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Check if user is active
    if user.status.value != "Active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active"
        )
    
    # Create access token
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return AuthResponseDTO(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,  # Convert hours to seconds
        user_id=user.id,
        username=user.username,
        role=user.role.value
    )

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponseDTO,
    summary="Request password reset",
    description="""
    Request password reset by sending OTP via email.
    
    **Process:**
    - Check if email exists in the system
    - Generate a random 4-digit OTP
    - Send OTP to user's email
    - OTP is valid for 30 minutes
    
    **Example Request:**
    ```json
    {
        "email": "user@example.com"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "OTP code has been sent to your email."
    }
    ```
    """,
    responses={
        200: {
            "description": "OTP sent successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "OTP code has been sent to your email."
                    }
                }
            }
        },
        404: {
            "description": "Email not found",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Email is invalid or does not exist."
                    }
                }
            }
        }
    }
)
def forgot_password(request: ForgotPasswordRequestDTO, db: Session = Depends(get_db)):
    """
    Request password reset by sending OTP to email

    Args:
        request: Email for password reset
        db: Database session

    Returns:
        ForgotPasswordResponseDTO: Status of OTP sending
    """
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return ForgotPasswordResponseDTO(
            success=False,
            message="Email is invalid or does not exist."
        )

    # Generate OTP
    otp_code = generate_otp()

    # Delete any existing OTPs for this email
    db.query(OTP).filter(OTP.email == request.email).delete()
    db.commit()

    # Create new OTP record
    otp_record = OTP(
        email=request.email,
        otp_code=otp_code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
    )
    db.add(otp_record)
    db.commit()

    # Send OTP via email
    if email_provider.send_otp_email(request.email, otp_code, user.first_name):
        return ForgotPasswordResponseDTO(
            success=True,
            message="OTP code has been sent to your email."
        )
    else:
        return ForgotPasswordResponseDTO(
            success=False,
            message="An error occurred while sending email. Please try again later."
        )

@router.post(
    "/validate-otp",
    response_model=ValidateOTPResponseDTO,
    summary="Validate OTP code",
    description="""
    Validate OTP code to receive password reset token.
    
    **Process:**
    - Check if OTP code is correct and not expired
    - Check if OTP has not been used
    - Return token for password reset (valid for 30 minutes)
    
    **Example Request:**
    ```json
    {
        "email": "user@example.com",
        "otp_code": "1234"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "OTP is valid.",
        "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """,
    responses={
        200: {
            "description": "OTP validation result",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "OTP is valid.",
                        "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        400: {
            "description": "Invalid OTP",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "OTP code is incorrect or has expired.",
                        "reset_token": None
                    }
                }
            }
        }
    }
)
def validate_otp(request: ValidateOTPRequestDTO, db: Session = Depends(get_db)):
    """
    Validate OTP code and return reset token

    Args:
        request: Email and OTP code
        db: Database session

    Returns:
        ValidateOTPResponseDTO: Validation result and reset token
    """
    # Find OTP record
    otp_record = db.query(OTP).filter(
        OTP.email == request.email,
        OTP.otp_code == request.otp_code,
        OTP.is_used == False
    ).first()

    if not otp_record:
        return ValidateOTPResponseDTO(
            success=False,
            message="OTP code is incorrect or has expired.",
            reset_token=None
        )

    # Check if OTP is expired
    if otp_record.is_expired():
        return ValidateOTPResponseDTO(
            success=False,
            message="OTP code is incorrect or has expired.",
            reset_token=None
        )

    # Mark OTP as used
    otp_record.is_used = True
    db.commit()

    # Generate reset token
    reset_token = create_reset_token(request.email)

    return ValidateOTPResponseDTO(
        success=True,
        message="OTP is valid.",
        reset_token=reset_token
    )

@router.post(
    "/reset-password",
    response_model=ResetPasswordResponseDTO,
    summary="Reset password",
    description="""
    Reset password with new password using verification token.
    
    **Process:**
    - Verify password reset token
    - Check password and confirmation password match
    - Update new password in database
    
    **Password Requirements:**
    - Minimum 8 characters
    - Must include uppercase, lowercase and numbers
    
    **Example Request:**
    ```json
    {
        "password": "NewPassword123",
        "repassword": "NewPassword123",
        "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Your password has been changed successfully. Please login again."
    }
    ```
    """,
    responses={
        200: {
            "description": "Password reset result",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Your password has been changed successfully. Please login again."
                    }
                }
            }
        },
        400: {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Password must be at least 8 characters long and include uppercase, lowercase and numbers."
                    }
                }
            }
        }
    }
)
def reset_password(request: ResetPasswordRequestDTO, db: Session = Depends(get_db)):
    """
    Reset password with new password

    Args:
        request: New password, confirmation and reset token
        db: Database session

    Returns:
        ResetPasswordResponseDTO: Password reset result
    """
    # Verify reset token
    email = verify_reset_token(request.reset_token)
    if not email:
        return ResetPasswordResponseDTO(
            success=False,
            message="Token is invalid or has expired."
        )

    # Check password confirmation
    if request.password != request.repassword:
        return ResetPasswordResponseDTO(
            success=False,
            message="Password confirmation does not match."
        )

    # Validate password strength
    if len(request.password) < 8:
        return ResetPasswordResponseDTO(
            success=False,
            message="Password must be at least 8 characters long."
        )

    # Check password contains uppercase, lowercase and numbers
    if not any(c.isupper() for c in request.password):
        return ResetPasswordResponseDTO(
            success=False,
            message="Password must be at least 8 characters long and include uppercase, lowercase and numbers."
        )

    if not any(c.islower() for c in request.password):
        return ResetPasswordResponseDTO(
            success=False,
            message="Password must be at least 8 characters long and include uppercase, lowercase and numbers."
        )

    if not any(c.isdigit() for c in request.password):
        return ResetPasswordResponseDTO(
            success=False,
            message="Password must be at least 8 characters long and include uppercase, lowercase and numbers."
        )

    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return ResetPasswordResponseDTO(
            success=False,
            message="User does not exist."
        )

    # Update password
    user.password = get_password_hash(request.password)
    db.commit()

    # Clean up used OTPs for this email
    db.query(OTP).filter(OTP.email == email).delete()
    db.commit()

    return ResetPasswordResponseDTO(
        success=True,
        message="Your password has been changed successfully. Please login again."
    )
