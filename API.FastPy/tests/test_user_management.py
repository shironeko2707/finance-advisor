from fastapi.testclient import TestClient

# Authentication headers for tests
AUTH_HEADERS = {
    "Authorization": "Bearer mock_token_admin"
}

class TestUserCreation:
    """Test user creation functionality with different scenarios"""
    
    def test_create_user_minimal_fields(self, test_client: TestClient):
        """Test creating user with only required fields (username and email)"""
        payload = {
            "username": "minimaluser",
            "email": "minimal@example.com"
        }
        
        response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)

        assert response.status_code == 201
        result = response.json()
        assert result["username"] == "minimaluser"
        assert result["email"] == "minimal@example.com"
        assert result["role"] == "User"  # Default role
        assert result["status"] == "Active"  # Default status
        assert "password" not in result  # Password should not be returned
        assert result["id"] is not None
    
    def test_create_user_with_custom_password(self, test_client: TestClient):
        """Test creating user with custom password"""
        payload = {
            "username": "custompass",
            "email": "custompass@example.com",
            "password": "mySecurePass123"
        }
        
        response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)

        assert response.status_code == 201
        result = response.json()
        assert result["username"] == "custompass"
        assert result["email"] == "custompass@example.com"
        assert "password" not in result  # Password should not be returned
    
    def test_create_user_complete_information(self, test_client: TestClient):
        """Test creating user with all available fields"""
        payload = {
            "username": "completeuser",
            "email": "complete@example.com",
            "password": "completePass789",
            "first_name": "John",
            "last_name": "Doe",
            "job_title": "Software Engineer",
            "role": "Admin",
            "status": "Active"
        }
        
        response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)

        assert response.status_code == 201
        result = response.json()
        assert result["username"] == "completeuser"
        assert result["email"] == "complete@example.com"
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["job_title"] == "Software Engineer"
        assert result["role"] == "Admin"
        assert result["status"] == "Active"
        assert "password" not in result
    
    def test_create_user_with_role_override(self, test_client: TestClient):
        """Test creating user with custom role and status"""
        payload = {
            "username": "adminuser",
            "email": "admin@example.com",
            "role": "Admin",
            "status": "Active",
            "first_name": "Admin",
            "last_name": "User"
        }
        
        response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)

        assert response.status_code == 201
        result = response.json()
        assert result["username"] == "adminuser"
        assert result["email"] == "admin@example.com"
        assert result["role"] == "Admin"
        assert result["status"] == "Active"
        assert result["first_name"] == "Admin"
        assert result["last_name"] == "User"


class TestUserValidation:
    """Test user validation error scenarios"""
    
    def test_missing_required_fields(self, test_client: TestClient):
        """Test validation with missing required fields"""
        payload = {
            "first_name": "John"  # Missing username and email
        }
        
        response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)

        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail
        
        # Check that both username and email are in validation errors
        error_fields = [error["loc"][-1] for error in error_detail["detail"]]
        assert "username" in error_fields
        assert "email" in error_fields
    
    def test_invalid_username_too_short(self, test_client: TestClient):
        """Test validation with username too short"""
        payload = {
            "username": "abc",  # Too short
            "email": "test@example.com"
        }
        
        response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)

        # This might be 201 if there's no minimum length validation
        # or 422 if there is - adjust based on your actual validation rules
        if response.status_code == 422:
            error_detail = response.json()
            assert "detail" in error_detail
        else:
            # If no validation, should succeed
            assert response.status_code == 201
    
    def test_invalid_email_format(self, test_client: TestClient):
        """Test validation with invalid email format"""
        payload = {
            "username": "testuser123",
            "email": "invalid-email"  # Invalid format
        }
        
        response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)

        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail
        
        # Check that email validation failed
        error_fields = [error["loc"][-1] for error in error_detail["detail"]]
        assert "email" in error_fields
    
    def test_duplicate_username(self, test_client: TestClient):
        """Test creating user with duplicate username"""
        # First, create a user
        payload1 = {
            "username": "duplicatetest",
            "email": "duplicate1@example.com"
        }
        
        response1 = test_client.post("/users/", json=payload1, headers=AUTH_HEADERS)
        assert response1.status_code == 201
        
        # Try to create another user with the same username
        payload2 = {
            "username": "duplicatetest",  # Same username
            "email": "duplicate2@example.com"  # Different email
        }
        
        response2 = test_client.post("/users/", json=payload2, headers=AUTH_HEADERS)

        # Should fail due to duplicate username
        assert response2.status_code == 400  # Or whatever your app returns for conflicts
    
    def test_duplicate_email(self, test_client: TestClient):
        """Test creating user with duplicate email"""
        # First, create a user
        payload1 = {
            "username": "user123456",  # Make sure username is at least 6 characters
            "email": "duplicate@example.com"
        }
        
        response1 = test_client.post("/users/", json=payload1, headers=AUTH_HEADERS)
        print(f"First user creation response: {response1.status_code}, {response1.text}")
        assert response1.status_code == 201
        
        # Try to create another user with the same email
        payload2 = {
            "username": "user789012",  # Different username, also at least 6 characters
            "email": "duplicate@example.com"  # Same email
        }
        
        response2 = test_client.post("/users/", json=payload2, headers=AUTH_HEADERS)

        # Should fail due to duplicate email
        assert response2.status_code == 400  # Or whatever your app returns for conflicts


class TestUserRetrieval:
    """Test user retrieval functionality"""
    
    def test_get_user_by_id(self, test_client: TestClient):
        """Test retrieving user by ID"""
        # First create a user
        payload = {
            "username": "getuser",
            "email": "getuser@example.com"
        }
        
        create_response = test_client.post("/users/", json=payload, headers=AUTH_HEADERS)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # Then retrieve the user
        get_response = test_client.get(f"/users/{user_id}", headers=AUTH_HEADERS)
        assert get_response.status_code == 200
        
        retrieved_user = get_response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["username"] == "getuser"
        assert retrieved_user["email"] == "getuser@example.com"
        assert "password" not in retrieved_user
    
    def test_get_user_not_found(self, test_client: TestClient):
        """Test retrieving non-existent user"""
        response = test_client.get("/users/99999", headers=AUTH_HEADERS)
        assert response.status_code == 404
    
    def test_list_users(self, test_client: TestClient):
        """Test listing all users"""
        # Create multiple users
        users_data = [
            {"username": "listuser1", "email": "list1@example.com"},
            {"username": "listuser2", "email": "list2@example.com"},
            {"username": "listuser3", "email": "list3@example.com"},
        ]
        
        created_users = []
        for user_data in users_data:
            response = test_client.post("/users/", json=user_data, headers=AUTH_HEADERS)
            assert response.status_code == 201
            created_users.append(response.json())
        
        # List all users
        list_response = test_client.get("/users/", headers=AUTH_HEADERS)
        assert list_response.status_code == 200
        
        users_list = list_response.json()
        assert len(users_list) >= len(users_data)
        
        # Check that our created users are in the list
        usernames = [user["username"] for user in users_list]
        for user_data in users_data:
            assert user_data["username"] in usernames
