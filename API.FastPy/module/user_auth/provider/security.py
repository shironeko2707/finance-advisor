import os
import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from module.user_auth.LoginDTO import AuthTokenPayloadDTO

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

# Mock token configuration for development
MOCK_TOKEN_ADMIN = os.getenv("MOCK_TOKEN_ADMIN", "")
MOCK_ADMIN_USER = {
    "sub": "khengleong_mock_admin",
    "username": "khengleong_mock_admin",
    "role": "Admin",
    "exp": 9999999999,  # Never expires (year 2286)
    "iat": 1692949200,
    "mock": True
}

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate hash from password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> AuthTokenPayloadDTO:
    """Verify and decode JWT token"""
    # Check for mock token first
    if MOCK_TOKEN_ADMIN is not "" and token == MOCK_TOKEN_ADMIN:
        return AuthTokenPayloadDTO(
            sub=MOCK_ADMIN_USER["sub"],
            username=MOCK_ADMIN_USER["username"],
            role=MOCK_ADMIN_USER["role"],
            exp=MOCK_ADMIN_USER["exp"],
            iat=MOCK_ADMIN_USER["iat"]
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token data
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")
        
        if user_id is None or username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required claims",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return AuthTokenPayloadDTO(
            sub=user_id,
            username=username,
            role=role,
            exp=exp,
            iat=payload.get("iat", 0)
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def generate_otp() -> str:
    """Generate a 4-digit OTP code"""
    return str(random.randint(1000, 9999))

def create_reset_token(email: str) -> str:
    """Create a JWT token for password reset"""
    data = {
        "sub": email,
        "type": "password_reset",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)  # 30 minutes expiry
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "password_reset":
            return None

        return email
    except JWTError:
        return None
