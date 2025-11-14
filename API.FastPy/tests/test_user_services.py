from sqlalchemy.orm import Session
from module.user_mgmt.UserDTO import UserCreateDTO
from module.user_mgmt.user_service import UserService
from module.user_mgmt.user_repository import UserRepository


class TestUserService:
    """Test the UserService business logic"""
    
    def test_create_user_service(self, test_db: Session):
        """Test user creation through service layer"""
        user_service = UserService()
        
        user_data = UserCreateDTO(
            username="servicetest",
            email="servicetest@example.com",
            first_name="Service",
            last_name="Test"
        )
        
        created_user = user_service.create_user(test_db, user_data)
        
        assert created_user.username == "servicetest"
        assert created_user.email == "servicetest@example.com"
        assert created_user.first_name == "Service"
        assert created_user.last_name == "Test"
        assert created_user.id is not None
    
    def test_get_user_service(self, test_db: Session):
        """Test user retrieval through service layer"""
        user_service = UserService()
        
        # Create a user first
        user_data = UserCreateDTO(
            username="getservicetest",
            email="getservicetest@example.com"
        )
        created_user = user_service.create_user(test_db, user_data)
        
        # Retrieve the user
        retrieved_user = user_service.get_user_by_id(test_db, created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "getservicetest"
        assert retrieved_user.email == "getservicetest@example.com"
    
    # def test_get_user_by_username_service(self, test_db: Session):
    #     """Test user retrieval by username through service layer"""
    #     user_service = UserService()
    #
    #     # Create a user first
    #     user_data = UserCreateDTO(
    #         username="usernametest",
    #         email="usernametest@example.com"
    #     )
    #     created_user = user_service.create_user(test_db, user_data)
    #
    #     # Retrieve the user by username
    #     retrieved_user = user_service.get_user_by_username(test_db, "usernametest")
    #
    #     assert retrieved_user is not None
    #     assert retrieved_user.id == created_user.id
    #     assert retrieved_user.username == "usernametest"
    
    def test_list_users_service(self, test_db: Session):
        """Test listing users through service layer"""
        user_service = UserService()
        
        # Create multiple users
        users_data = [
            UserCreateDTO(username="listuser1", email="listuser1@example.com"),
            UserCreateDTO(username="listuser2", email="listuser2@example.com"),
            UserCreateDTO(username="listuser3", email="listuser3@example.com"),
        ]
        
        created_users = []
        for user_data in users_data:
            created_user = user_service.create_user(test_db, user_data)
            created_users.append(created_user)
        
        # List users
        users_list = user_service.get_users(test_db)
        
        assert len(users_list) >= len(users_data)
        
        # Check that our created users are in the list
        usernames = [user.username for user in users_list]
        for user_data in users_data:
            assert user_data.username in usernames


class TestUserRepository:
    """Test the UserRepository data access layer"""
    
    def test_create_user_repository(self, test_db: Session):
        """Test user creation through repository layer"""
        user_repo = UserRepository()
        
        user_data = {
            "username": "repotest",
            "email": "repotest@example.com",
            "password": "hashedpassword",
            "first_name": "Repo",
            "last_name": "Test",
            "role": "USER",
            "status": "ACTIVE"
        }
        
        created_user = user_repo.create_user(test_db, user_data)
        
        assert created_user.username == "repotest"
        assert created_user.email == "repotest@example.com"
        assert created_user.first_name == "Repo"
        assert created_user.last_name == "Test"
        assert created_user.id is not None
    
    def test_get_user_repository(self, test_db: Session):
        """Test user retrieval through repository layer"""
        user_repo = UserRepository()
        
        # Create a user first
        user_data = {
            "username": "getrepotest",
            "email": "getrepotest@example.com",
            "password": "hashedpassword",
            "first_name": "Get",
            "last_name": "Test",
            "role": "USER",
            "status": "ACTIVE"
        }
        created_user = user_repo.create_user(test_db, user_data)
        
        # Retrieve the user
        retrieved_user = user_repo.get_user_by_id(test_db, created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "getrepotest"
    
    def test_get_user_by_username_repository(self, test_db: Session):
        """Test user retrieval by username through repository layer"""
        user_repo = UserRepository()
        
        # Create a user first
        user_data = {
            "username": "usernamerepotest",
            "email": "usernamerepotest@example.com",
            "password": "hashedpassword",
            "role": "USER",
            "status": "ACTIVE"
        }
        created_user = user_repo.create_user(test_db, user_data)
        
        # Retrieve the user by username
        retrieved_user = user_repo.get_user_by_username(test_db, "usernamerepotest")
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "usernamerepotest"
    
    def test_get_user_by_email_repository(self, test_db: Session):
        """Test user retrieval by email through repository layer"""
        user_repo = UserRepository()
        
        # Create a user first
        user_data = {
            "username": "emailrepotest",
            "email": "emailrepotest@example.com",
            "password": "hashedpassword",
            "role": "USER",
            "status": "ACTIVE"
        }
        created_user = user_repo.create_user(test_db, user_data)
        
        # Retrieve the user by email
        retrieved_user = user_repo.get_user_by_email(test_db, "emailrepotest@example.com")
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "emailrepotest@example.com"
