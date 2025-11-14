from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException
from module.user_mgmt.UserDTO import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from module.user_mgmt.user_repository import user_repository
from module.user_mgmt.UserModel import UserRole, UserStatus
from module.user_mgmt.utils import get_password_hash, generate_random_password

class UserService:
    
    def __init__(self):
        self.user_repository = user_repository
    
    def create_user(self, db: Session, user: UserCreateDTO) -> UserResponseDTO:
        """
        Create a new user with business logic validation and smart defaults.
        
        - Validates email and username uniqueness
        - Generates random 6-character password if not provided
        - Applies default role (User) and status (Active) if not specified
        - Hashes the password before storage
        """
        # Check if user with email already exists
        existing_user = self.user_repository.get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if username already exists
        existing_username = self.user_repository.get_user_by_username(db, username=user.username)
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Prepare user data with defaults
        user_data = user.model_dump()
        
        # Generate random password if not provided
        if not user.password:
            generated_password = generate_random_password(6)
            user_data['password'] = get_password_hash(generated_password)
            # Note: In a real system, you might want to return the generated password 
            # or send it via email to the user
        else:
            # Hash the provided password
            user_data['password'] = get_password_hash(user.password)
        
        # Ensure defaults are set (though they should be set by Pydantic already)
        if user_data.get('role') is None:
            user_data['role'] = 'User'
        if user_data.get('status') is None:
            user_data['status'] = 'Active'
        
        new_user = self.user_repository.create_user(db=db, user_data=user_data)
        return UserResponseDTO.model_validate(new_user)
    
    def get_user_by_id(self, db: Session, user_id: int) -> UserResponseDTO:
        """Get a specific user by ID"""
        user = self.user_repository.get_user_by_id(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponseDTO.model_validate(user)
    
    def get_users(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search_term: Optional[str] = None,
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[UserResponseDTO]:
        """
        Get list of users with filtering and sorting capabilities.

        Args:
            db: Database session
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            search_term: Search term for filtering users
            status: Filter by user status (ACTIVE/INACTIVE)
            role: Filter by user role (ADMIN/USER)
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order - 'asc' or 'desc' (default: desc)

        Returns:
            List of UserResponseDTO objects
        """
        users = self.user_repository.get_users(
            db=db,
            skip=skip,
            limit=limit,
            search_term=search_term,
            status=status,
            role=role,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return [UserResponseDTO.model_validate(user) for user in users]
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdateDTO) -> UserResponseDTO:
        """Update a user with business logic validation"""
        # Check if user exists
        existing_user = self.user_repository.get_user_by_id(db, user_id=user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if email is being updated and if it's already taken by another user
        if user_update.email:
            email_user = self.user_repository.get_user_by_email(db, email=user_update.email)
            if email_user and email_user.id != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if username is being updated and if it's already taken by another user
        if user_update.username:
            username_user = self.user_repository.get_user_by_username(db, username=user_update.username)
            if username_user and username_user.id != user_id:
                raise HTTPException(status_code=400, detail="Username already taken")
        
        # Hash password if it's being updated
        user_data = user_update.model_dump(exclude_unset=True)
        if 'password' in user_data and user_data['password']:
            user_data['password'] = get_password_hash(user_data['password'])
        
        updated_user = self.user_repository.update_user(db=db, user_id=user_id, user_data=user_data)
        return UserResponseDTO.model_validate(updated_user)
    
    def delete_user(self, db: Session, user_id: int) -> dict:
        """Delete a user"""
        success = self.user_repository.delete_user(db=db, user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}

    def toggle_user_status(self, db: Session, user_id: int) -> UserResponseDTO:
        """
        Toggle a user's status between ACTIVE and INACTIVE.
        Args:
            db (Session): SQLAlchemy session
            user_id (int): ID of the user to toggle
        Returns:
            UserResponseDTO: The updated user object
        Raises:
            HTTPException: If user not found or DB error
        """
        import logging
        logger = logging.getLogger(__name__)
        user = self.user_repository.get_user_by_id(db, user_id=user_id)
        if not user:
            logger.warning(f"User with id {user_id} not found for status toggle.")
            raise HTTPException(status_code=404, detail="User not found")
        try:
            if user.status == UserStatus.ACTIVE:
                user.status = UserStatus.INACTIVE
            else:
                user.status = UserStatus.ACTIVE
            db.commit()
            db.refresh(user)
            logger.info(f"Toggled status for user {user_id} to {user.status}.")
            return UserResponseDTO.model_validate(user)
        except Exception as e:
            db.rollback()
            logger.error(f"Error toggling status for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Create instance
user_service = UserService()