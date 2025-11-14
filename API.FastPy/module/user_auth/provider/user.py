from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db
from module.user_auth.provider.security import verify_token, MOCK_ADMIN_USER
from module.user_mgmt.UserModel import User, UserRole, UserStatus

# Security scheme
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        db: Database session
    
    Returns:
        User: Current authenticated user (real or mock)
    
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Verify token
    token_payload = verify_token(credentials.credentials)
    
    # Check if this is a mock user
    if token_payload.sub == MOCK_ADMIN_USER["sub"]:
        # Create a mock User object
        mock_user = User()
        mock_user.id = 999999999  # Special ID for mock user
        mock_user.username = MOCK_ADMIN_USER["username"]
        mock_user.email = "mock_admin@dev.local"
        mock_user.full_name = "Mock Admin"
        mock_user.role = UserRole.ADMIN
        mock_user.status = UserStatus.ACTIVE
        mock_user.password = ""  # Empty password for mock user
        return mock_user
    
    # Get real user from database
    user = db.query(User).filter(User.id == int(token_payload.sub)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is still active
    if user.status.value != "Active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current authenticated user with Admin role
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User: Current authenticated admin user
    
    Raises:
        HTTPException: 403 if user doesn't have Admin role
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    
    return current_user

def require_admin_role():
    """
    Dependency that requires Admin role for endpoint access
    
    Returns:
        Dependency function that validates admin access
    """
    return Depends(get_admin_user)
