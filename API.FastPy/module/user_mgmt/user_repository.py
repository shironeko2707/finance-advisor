from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from module.user_mgmt.UserModel import User, UserRole, UserStatus
from typing import Optional, List, Dict, Any

class UserRepository:
    
    def create_user(self, db: Session, user_data: Dict[str, Any]) -> User:
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
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
    ) -> List[User]:
        """
        Get users with filtering and sorting.

        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            search_term: Search term for name, email, username
            status: Filter by user status (ACTIVE/INACTIVE)
            role: Filter by user role (ADMIN/USER)
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order - 'asc' or 'desc' (default: desc)

        Returns:
            List of User objects
        """
        query = db.query(User)
        
        # Apply search filter
        if search_term:
            search_filter = or_(
                User.first_name.ilike(f"%{search_term}%"),
                User.last_name.ilike(f"%{search_term}%"),
                User.email.ilike(f"%{search_term}%"),
                User.username.ilike(f"%{search_term}%"),
            )
            query = query.filter(search_filter)
        
        # Apply status filter
        if status:
            query = query.filter(User.status == status)

        # Apply role filter
        if role:
            query = query.filter(User.role == role)

        # Apply sorting
        sort_column = getattr(User, sort_by, User.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        return query.offset(skip).limit(limit).all()
    
    def update_user(self, db: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        for field, value in user_data.items():
            if hasattr(db_user, field) and value is not None:
                setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

# Create instance
user_repository = UserRepository()