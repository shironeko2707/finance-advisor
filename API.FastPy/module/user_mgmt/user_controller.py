from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from module.user_mgmt.UserDTO import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from module.user_mgmt.user_service import user_service
from module.user_auth.provider.user import require_admin_role
from module.user_mgmt.UserModel import User, UserRole, UserStatus
import logging

router = APIRouter(
    prefix="/users", 
    tags=["User Management"],
    responses={404: {"description": "User not found"}}
)

@router.post(
    "", 
    response_model=UserResponseDTO,
    status_code=201,
    summary="Create a new user",
    description="""
    Create a new user in the system with flexible field requirements.
    
    **Required Fields:**
    - `username`: Unique username (6-50 characters, alphanumeric and underscores only)
    - `email`: Valid email address (must be unique in the system)
    
    **Optional Fields with Defaults:**
    - `password`: If not provided, a random 6-character password will be generated
    - `role`: Defaults to 'User' if not specified
    - `status`: Defaults to 'Active' if not specified
    - `first_name`, `last_name`, `job_title`: Additional user information
    
    **Default Values:**
    - Password: Auto-generated 6-character random string
    - Role: 'User'
    - Status: 'Active'
    
    **Examples:**
    1. Minimal creation: `{"username": "newuser123", "email": "user@example.com"}`
    2. With custom password: `{"username": "user456", "email": "user@example.com", "password": "mypass123"}`
    3. Complete user: Include all optional fields as needed
    """,
    response_description="The created user information (password excluded for security)",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "minimal_user": {
                            "summary": "User created with minimal required fields",
                            "description": "When only username and email are provided",
                            "value": {
                                "id": 1,
                                "username": "newuser123",
                                "first_name": None,
                                "last_name": None,
                                "email": "user@example.com",
                                "job_title": None,
                                "role": "User",
                                "status": "Active",
                                "created_at": "2025-08-14T10:30:00Z",
                                "updated_at": None
                            }
                        },
                        "complete_user": {
                            "summary": "User created with all fields",
                            "description": "When all optional fields are provided",
                            "value": {
                                "id": 2,
                                "username": "johndoe123",
                                "first_name": "John",
                                "last_name": "Doe",
                                "email": "john.doe@example.com",
                                "job_title": "Software Engineer",
                                "role": "Admin",
                                "status": "Active",
                                "created_at": "2025-08-14T10:30:00Z",
                                "updated_at": None
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Validation error or duplicate username/email",
            "content": {
                "application/json": {
                    "examples": {
                        "email_exists": {
                            "summary": "Email already exists",
                            "value": {"detail": "Email already registered"}
                        },
                        "username_exists": {
                            "summary": "Username already taken",
                            "value": {"detail": "Username already taken"}
                        },
                        "validation_error": {
                            "summary": "Validation error",
                            "value": {
                                "detail": [
                                    {
                                        "loc": ["body", "username"],
                                        "msg": "ensure this value has at least 6 characters",
                                        "type": "value_error.any_str.min_length"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
)
def create_user(user: UserCreateDTO, db: Session = Depends(get_db), _: User = require_admin_role()):
    """
    Create a new user with flexible field requirements.
    
    ## Required Fields:
    - **username**: Unique username (6-50 characters, alphanumeric and underscores only)
    - **email**: Valid email address (must be unique in the system)
    
    ## Optional Fields with Smart Defaults:
    - **password**: If not provided, a random 6-character password will be automatically generated
    - **role**: Defaults to 'User' if not specified (available: User, Admin, Moderator)
    - **status**: Defaults to 'Active' if not specified (available: Active, Inactive, Pending)
    - **first_name**: User's first name (optional)
    - **last_name**: User's last name (optional)
    - **job_title**: User's job title (optional)
    
    ## Usage Examples:
    
    **Minimal Creation (only required fields):**
    ```json
    {
        "username": "newuser123",
        "email": "newuser@example.com"
    }
    ```
    Result: User created with auto-generated password, role='User', status='Active'
    
    **With Custom Password:**
    ```json
    {
        "username": "customuser456",
        "email": "custom@example.com",
        "password": "mySecurePass123"
    }
    ```
    
    **Complete User Information:**
    ```json
    {
        "username": "johndoe123",
        "email": "john.doe@example.com",
        "password": "securepass123",
        "first_name": "John",
        "last_name": "Doe",
        "job_title": "Software Engineer",
        "role": "Admin",
        "status": "Active"
    }
    ```
    """
    return user_service.create_user(db=db, user=user)

@router.get(
    "", 
    response_model=List[UserResponseDTO],
    summary="Get all users with pagination and search",
    description="""
    Retrieve a list of users from the system with powerful filtering and pagination capabilities.
    
    **Features:**
    - **Pagination**: Control the number of results and offset for efficient data loading
    - **Search**: Find users by name or email using partial text matching
    - **Sorting**: Results are returned in chronological order (newest first)
    
    **Query Parameters:**
    - `skip`: Number of users to skip (default: 0, min: 0) - useful for pagination
    - `limit`: Maximum users to return (default: 100, min: 1, max: 1000)
    - `search_term`: Optional search term to filter by first name, last name, or email
    
    **Usage Examples:**
    - Get first 20 users: `GET /users/?limit=20`
    - Get next 20 users: `GET /users/?skip=20&limit=20`
    - Search for users: `GET /users/?search_term=john`
    - Combined: `GET /users/?search_term=engineer&skip=10&limit=5`
    
    **Search Behavior:**
    - Case-insensitive partial matching
    - Searches across first_name, last_name, and email fields
    - Returns users where any of these fields contain the search term
    """,
    response_description="Array of user objects matching the criteria. Empty array if no users found.",
    responses={
        200: {
            "description": "Successfully retrieved users",
            "content": {
                "application/json": {
                    "examples": {
                        "users_list": {
                            "summary": "List of users",
                            "description": "Example response with multiple users",
                            "value": [
                                {
                                    "id": 1,
                                    "username": "johndoe123",
                                    "first_name": "John",
                                    "last_name": "Doe",
                                    "email": "john.doe@example.com",
                                    "job_title": "Software Engineer",
                                    "role": "User",
                                    "status": "Active",
                                    "created_at": "2025-08-14T10:30:00Z",
                                    "updated_at": "2025-08-14T11:15:00Z"
                                },
                                {
                                    "id": 2,
                                    "username": "janesmith456",
                                    "first_name": "Jane",
                                    "last_name": "Smith",
                                    "email": "jane.smith@example.com",
                                    "job_title": "Product Manager",
                                    "role": "Admin",
                                    "status": "Active",
                                    "created_at": "2025-08-14T09:20:00Z",
                                    "updated_at": None
                                }
                            ]
                        },
                        "empty_result": {
                            "summary": "No users found",
                            "description": "When search criteria returns no results",
                            "value": []
                        }
                    }
                }
            }
        },
        422: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["query", "limit"],
                                "msg": "ensure this value is less than or equal to 1000",
                                "type": "value_error.number.not_le"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def read_users(
    skip: int = Query(0, ge=0, description="Number of users to skip for pagination (default: 0)"),
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of users to return (default: 1000, max: 1000)"),
    search_term: Optional[str] = Query(None, description="Search term for filtering users by first name, last name, email, or username (case-insensitive)"),
    status: Optional[UserStatus] = Query(None, description="Filter users by status (Active, Inactive)"),
    role: Optional[UserRole] = Query(None, description="Filter users by role (Admin, User)"),
    sort_by: str = Query("created_at", description="Field to sort by (id, username, email, first_name, last_name, created_at, updated_at)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: 'asc' for ascending or 'desc' for descending"),
    db: Session = Depends(get_db),
    _: User = require_admin_role()  # Admin access validation only
):
    """
    Retrieve a paginated list of users with comprehensive filtering and sorting capabilities.

    ## Query Parameters:
    
    ### Pagination:
    - **skip** (optional): Number of users to skip - useful for implementing pagination
      - Default: 0
      - Minimum: 0
      - Example: `skip=20` to get results starting from the 21st user
    
    - **limit** (optional): Maximum number of users to return in one request
      - Default: 100
      - Range: 1-1000
      - Example: `limit=50` to get at most 50 users
    
    ### Search & Filtering:
    - **search_term** (optional): Search term to filter users
      - Searches across: first_name, last_name, email, and username fields
      - Case-insensitive partial matching
      - Example: `search_term=john` finds users with "john" in their name, email, or username

    - **status** (optional): Filter by user status
      - Available values: "Active", "Inactive"
      - Example: `status=Active` to show only active users

    - **role** (optional): Filter by user role
      - Available values: "Admin", "User"
      - Example: `role=Admin` to show only administrators

    ### Sorting:
    - **sort_by** (optional): Field to sort results by
      - Available fields: "id", "username", "email", "first_name", "last_name", "created_at", "updated_at"
      - Default: "created_at"
      - Example: `sort_by=username` to sort alphabetically by username

    - **sort_order** (optional): Sort direction
      - Values: "asc" (ascending) or "desc" (descending)
      - Default: "desc" (newest first when sorting by created_at)
      - Example: `sort_order=asc` for oldest first or A-Z alphabetical

    ## Usage Patterns:
    
    **Basic Pagination:**
    ```
    GET /users/?limit=20               # First 20 users (newest first)
    GET /users/?skip=20&limit=20       # Next 20 users (21-40)
    GET /users/?skip=40&limit=20       # Next 20 users (41-60)
    ```
    
    **Search Examples:**
    ```
    GET /users/?search_term=engineer        # Users with "engineer" in name/email/username
    GET /users/?search_term=@company.com    # Users from company.com domain
    GET /users/?search_term=admin           # Users with "admin" in their details
    ```
    
    **Filtering Examples:**
    ```
    GET /users/?status=Active          # Only active users
    GET /users/?role=Admin             # Only administrators
    GET /users/?status=Active&role=User # Only active regular users
    ```

    **Sorting Examples:**
    ```
    GET /users/?sort_by=username&sort_order=asc    # Alphabetical by username A-Z
    GET /users/?sort_by=created_at&sort_order=desc # Newest users first (default)
    GET /users/?sort_by=email&sort_order=asc       # Alphabetical by email
    ```

    **Combined Usage:**
    ```
    GET /users/?search_term=manager&status=Active&sort_by=last_name&sort_order=asc&limit=10
    # Find active users with "manager" in their info, sorted by last name A-Z, limit 10
    ```
    
    ## Response Format:
    Returns an array of user objects, each containing complete user information excluding passwords.
    Empty array `[]` is returned when no users match the criteria.
    Results are sorted by the specified field and order (default: created_at desc - newest first).
    """
    return user_service.get_users(
        db=db,
        skip=skip,
        limit=limit,
        search_term=search_term,
        status=status,
        role=role,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get(
    "/{user_id}", 
    response_model=UserResponseDTO,
    summary="Get user by ID",
    description="""
    Retrieve a specific user's complete information using their unique identifier.
    
    **Purpose:**
    - Get detailed information about a single user
    - Useful for user profile pages, user management interfaces
    - Returns all user fields except password (for security)
    
    **Path Parameter:**
    - `user_id`: The unique integer identifier of the user (required)
    
    **Use Cases:**
    - Display user profile information
    - Edit user details (get current values first)
    - Verify user exists before performing operations
    - Show user details in admin panels
    """,
    response_description="Complete user information including all profile fields",
    responses={
        200: {
            "description": "User found and returned successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "johndoe123",
                        "first_name": "John",
                        "last_name": "Doe", 
                        "email": "john.doe@example.com",
                        "job_title": "Software Engineer",
                        "role": "User",
                        "status": "Active",
                        "created_at": "2025-08-14T10:30:00Z",
                        "updated_at": "2025-08-14T14:22:00Z"
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User not found"
                    }
                }
            }
        },
        422: {
            "description": "Invalid user ID format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "user_id"],
                                "msg": "value is not a valid integer",
                                "type": "type_error.integer"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def read_user(user_id: int, db: Session = Depends(get_db), _: User = require_admin_role()):
    """
    Retrieve a specific user by their unique identifier.
    
    ## Path Parameter:
    - **user_id**: The unique integer ID of the user to retrieve
      - Must be a positive integer
      - Example: `1`, `42`, `12345`
    
    ## Response:
    Returns complete user information including:
    - Basic info: username, first_name, last_name, email
    - Professional info: job_title
    - System info: role, status, created_at, updated_at
    - **Note**: Password is never included in responses for security
    
    ## Usage Examples:
    ```
    GET /users/1          # Get user with ID 1
    GET /users/12345      # Get user with ID 12345
    ```
    
    ## Common Use Cases:
    1. **User Profile Display**: Show user information on profile pages
    2. **Edit User Preparation**: Get current user data before showing edit form
    3. **User Verification**: Check if user exists and get their current status
    4. **Admin Operations**: View user details in management interfaces
    
    ## Error Handling:
    - Returns 404 if user doesn't exist
    - Returns 422 if user_id is not a valid integer
    """
    return user_service.get_user_by_id(db, user_id=user_id)

@router.put(
    "/{user_id}", 
    response_model=UserResponseDTO,
    summary="Update user information",
    description="""
    Update an existing user's information with flexible field modification.
    
    **Features:**
    - **Partial Updates**: Only provide fields you want to change
    - **Validation**: All fields are validated before updating
    - **Uniqueness Checks**: Username and email uniqueness is enforced
    - **Password Security**: Passwords are automatically hashed if provided
    
    **Updateable Fields:**
    - `username`: Must be unique and follow validation rules
    - `email`: Must be unique and valid email format
    - `password`: Will be securely hashed before storage
    - `first_name`, `last_name`: Personal information
    - `job_title`: Professional information
    - `role`: System role (User, Admin, Moderator)
    - `status`: Account status (Active, Inactive, Pending)
    
    **Validation Rules:**
    - Username: 6-50 characters, alphanumeric and underscores only
    - Email: Valid email format, must be unique
    - Password: 6-50 characters, must contain letters and numbers
    - Names: 1-50 characters if provided
    - Job title: Up to 100 characters if provided
    
    **Usage Patterns:**
    - Update single field: `{"first_name": "NewName"}`
    - Update multiple fields: `{"email": "new@email.com", "role": "Admin"}`
    - Change password: `{"password": "newSecurePass123"}`
    """,
    response_description="The updated user information with all current field values",
    responses={
        200: {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "profile_update": {
                            "summary": "Profile information updated",
                            "description": "User's name and job title were updated",
                            "value": {
                                "id": 1,
                                "username": "johndoe123",
                                "first_name": "Jonathan",
                                "last_name": "Doe-Smith",
                                "email": "john.doe@example.com",
                                "job_title": "Senior Software Engineer",
                                "role": "User",
                                "status": "Active",
                                "created_at": "2025-08-14T10:30:00Z",
                                "updated_at": "2025-08-14T15:45:00Z"
                            }
                        },
                        "role_update": {
                            "summary": "User role changed",
                            "description": "User was promoted to Admin role",
                            "value": {
                                "id": 2,
                                "username": "janesmith456",
                                "first_name": "Jane",
                                "last_name": "Smith",
                                "email": "jane.smith@example.com",
                                "job_title": "Product Manager",
                                "role": "Admin",
                                "status": "Active",
                                "created_at": "2025-08-14T09:20:00Z",
                                "updated_at": "2025-08-14T15:45:00Z"
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Validation error or duplicate data",
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_email": {
                            "summary": "Email already in use",
                            "value": {"detail": "Email already registered"}
                        },
                        "duplicate_username": {
                            "summary": "Username already taken",
                            "value": {"detail": "Username already taken"}
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def update_user(user_id: int, user_update: UserUpdateDTO, db: Session = Depends(get_db), _: User = require_admin_role()):
    """
    Update an existing user's information with flexible partial updates.
    
    ## Parameters:
    - **user_id** (path): The unique ID of the user to update
    - **user_update** (body): Object containing fields to update
    
    ## Updateable Fields:
    All fields are optional - only provide the ones you want to change:
    
    ### Personal Information:
    - **first_name**: User's first name (1-50 characters)
    - **last_name**: User's last name (1-50 characters) 
    - **job_title**: Professional title or position (up to 100 characters)
    
    ### Account Information:
    - **username**: Unique username (6-50 chars, alphanumeric + underscores)
    - **email**: Valid email address (must be unique across all users)
    - **password**: New password (6-50 chars, must contain letters and numbers)
    
    ### System Settings:
    - **role**: User role - "User", "Admin", or "Moderator"
    - **status**: Account status - "Active", "Inactive", or "Pending"
    
    ## Update Examples:
    
    **Update Name and Job Title:**
    ```json
    {
        "first_name": "Jonathan",
        "last_name": "Doe-Smith", 
        "job_title": "Senior Software Engineer"
    }
    ```
    
    **Change Email and Password:**
    ```json
    {
        "email": "new.email@company.com",
        "password": "newSecurePassword789"
    }
    ```
    
    **Promote to Admin:**
    ```json
    {
        "role": "Admin"
    }
    ```
    
    **Deactivate Account:**
    ```json
    {
        "status": "Inactive"
    }
    ```
    
    ## Validation & Business Rules:
    - Email and username must be unique across all users
    - Password changes are automatically hashed for security
    - Role changes affect user permissions immediately
    - Status changes affect user access to the system
    - All validation rules from user creation apply to updates
    
    ## Response:
    Returns the complete updated user object with all current field values and updated timestamp.
    """
    return user_service.update_user(db=db, user_id=user_id, user_update=user_update)

@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete user from system",
    description="""
    Permanently delete a user from the system.
    
    **⚠️ WARNING: This action is irreversible!**
    
    **What happens when you delete a user:**
    - User account is permanently removed from the database
    - All user data is deleted (profile, settings, etc.)
    - User will no longer be able to log in
    - Any references to this user in other systems may need cleanup
    
    **Before Deleting:**
    - Consider deactivating the user instead (`status: "Inactive"`) if you want to preserve data
    - Ensure you have proper authorization to delete this user
    - Back up any important user data if needed
    - Check if user has dependent data in other parts of the system
    
    **Alternative to Deletion:**
    Instead of permanent deletion, consider updating the user status:
    ```json
    PUT /users/{user_id}
    {
        "status": "Inactive"
    }
    ```
    
    **Use Cases:**
    - Remove test/demo accounts
    - Clean up inactive accounts (with proper data retention policies)
    - Handle GDPR "right to be forgotten" requests
    - Remove accounts that violated terms of service
    
    **Response:**
    - Success: HTTP 204 No Content (empty response body)
    - The absence of content indicates successful deletion
    """,
    responses={
        204: {
            "description": "User successfully deleted. No content returned.",
            "content": None
        },
        404: {
            "description": "User not found - cannot delete non-existent user",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User not found"
                    }
                }
            }
        },
        422: {
            "description": "Invalid user ID format", 
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "user_id"],
                                "msg": "value is not a valid integer",
                                "type": "type_error.integer"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = require_admin_role()):
    """
    Permanently delete a user from the system.
    
    ## ⚠️ IMPORTANT WARNINGS:
    
    **This operation is IRREVERSIBLE!** Once a user is deleted:
    - All user data is permanently lost
    - User cannot log in anymore
    - User ID cannot be reused
    - Any dependent data may become orphaned
    
    ## Parameters:
    - **user_id** (path): The unique integer ID of the user to delete
    
    ## Before You Delete:
    
    **Consider Alternatives:**
    1. **Deactivate Instead**: Set `status: "Inactive"` to preserve data
    2. **Archive Data**: Export important user information first
    3. **Check Dependencies**: Ensure no critical data depends on this user
    
    **Required Checks:**
    - Verify you have authorization to delete this user
    - Confirm this is not an accidental deletion
    - Check your organization's data retention policies
    
    ## Usage Examples:
    
    **Standard Deletion:**
    ```
    DELETE /users/123
    ```
    
    **Better Alternative (Deactivation):**
    ```
    PUT /users/123
    {
        "status": "Inactive"
    }
    ```
    
    ## When to Use This Endpoint:
    
    **Appropriate Cases:**
    - Removing test or demo accounts
    - Cleaning up spam accounts
    - Fulfilling "right to be forgotten" requests (GDPR)
    - Removing accounts that violated terms of service
    - System maintenance with proper data backups
    
    **Inappropriate Cases:**
    - Temporary user suspension (use status update instead)
    - Regular user management (use deactivation)
    - When user data might be needed later
    
    ## Response Behavior:
    - **Success (204)**: User deleted, no response body returned
    - **Not Found (404)**: User doesn't exist (already deleted or never existed)
    - **Error (422)**: Invalid user ID format
    
    The HTTP 204 status code specifically means "No Content" - the operation
    succeeded but there's no data to return since the user no longer exists.
    """
    return user_service.delete_user(db=db, user_id=user_id)

@router.patch(
    "/{user_id}/toggle-status",
    response_model=UserResponseDTO,
    summary="Toggle user status (activate/deactivate)",
    description="""
    Toggle a user's status between Active and Inactive. Only accessible by Admins.\n\n- If user is Active, will set to Inactive.\n- If user is Inactive, will set to Active.\n- Returns the updated user info.\n\n**Path Parameter:**\n- `user_id`: The unique integer identifier of the user (required)\n\n**Response:**\n- 200: Updated user info\n- 404: User not found\n- 422: Invalid user ID format\n    """,
    responses={
        200: {"description": "User status toggled successfully"},
        404: {"description": "User not found"},
        422: {"description": "Invalid user ID format"}
    }
)
def toggle_user_status(user_id: int, db: Session = Depends(get_db), _: User = require_admin_role()):
    """
    Toggle a user's status between Active and Inactive.
    """
    try:
        return user_service.toggle_user_status(db=db, user_id=user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error toggling user status: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
