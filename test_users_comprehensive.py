"""
Comprehensive tests for user management functionality
Tests both authentication endpoints and user management endpoints
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime
from typing import Dict, Any

from main import app
from app.schemas.user import UserRole


class TestUserSchemas:
    """Test user schema validation"""
    
    def test_user_create_validator_valid_data(self):
        """Test UserCreateValidator with valid data"""
        from app.schemas.user import UserCreateValidator
        
        user_data = UserCreateValidator(
            username="testuser",
            password="password123",
            email="test@example.com",
            full_name="Test User",
            role=UserRole.USER
        )
        
        assert user_data.username == "testuser"
        assert user_data.password == "password123"
        assert user_data.email == "test@example.com"
        assert user_data.full_name == "Test User"
        assert user_data.role == UserRole.USER
    
    def test_user_create_validator_invalid_username(self):
        """Test UserCreateValidator with invalid username"""
        from app.schemas.user import UserCreateValidator
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateValidator(
                username="ab",  # Too short
                password="password123",
                email="test@example.com"
            )
        
        assert "Username must be between 3 and 20 characters" in str(exc_info.value)
    
    def test_user_create_validator_invalid_username_special_chars(self):
        """Test UserCreateValidator with special characters in username"""
        from app.schemas.user import UserCreateValidator
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreateValidator(
                username="test@user",  # Contains special character
                password="password123",
                email="test@example.com"
            )
        
        assert "Username can only contain letters, numbers, and underscores" in str(exc_info.value)
    
    def test_user_update_validator_valid_data(self):
        """Test UserUpdateValidator with valid data"""
        from app.schemas.user import UserUpdateValidator
        
        update_data = UserUpdateValidator(
            username="newusername",
            full_name="New Full Name"
        )
        
        assert update_data.username == "newusername"
        assert update_data.full_name == "New Full Name"
        assert update_data.password is None
    
    def test_super_user_update_validator_with_role(self):
        """Test SuperUserUpdateValidator with role update"""
        from app.schemas.user import SuperUserUpdateValidator
        
        update_data = SuperUserUpdateValidator(
            username="adminuser",
            role=UserRole.ADMIN
        )
        
        assert update_data.username == "adminuser"
        assert update_data.role == UserRole.ADMIN
    
    def test_user_signup_validator_valid_data(self):
        """Test UserSignupValidator with valid data"""
        from app.schemas.user import UserSignupValidator
        
        signup_data = UserSignupValidator(
            email="signup@example.com",
            password="password123",
            username="signupuser",
            full_name="Signup User"
        )
        
        assert signup_data.email == "signup@example.com"
        assert signup_data.password == "password123"
        assert signup_data.username == "signupuser"
        assert signup_data.full_name == "Signup User"
    
    def test_user_signin_validator_valid_data(self):
        """Test UserSigninValidator with valid data"""
        from app.schemas.user import UserSigninValidator
        
        signin_data = UserSigninValidator(
            email="signin@example.com",
            password="password123"
        )
        
        assert signin_data.email == "signin@example.com"
        assert signin_data.password == "password123"


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        self.mock_user_data = {
            "id": "test-user-id",
            "email": "test@example.com",
            "user_metadata": {
                "username": "testuser",
                "full_name": "Test User",
                "role": "user"
            },
            "app_metadata": {
                "role": "user"
            },
            "created_at": "2024-01-01T00:00:00Z",
            "last_sign_in_at": "2024-01-01T12:00:00Z",
            "confirmed_at": "2024-01-01T00:30:00Z"
        }
    
    @patch('app.core.supabase.supabase_auth.create_user')
    def test_signup_success(self, mock_create_user):
        """Test successful user signup"""
        mock_create_user.return_value = self.mock_user_data
        
        signup_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "username": "newuser",
            "full_name": "New User"
        }
        
        response = self.client.post("/api/v1/auth/signup", json=signup_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "User created successfully. Please check your email to confirm your account."
        assert data["user"]["email"] == self.mock_user_data["email"]
        assert data["user"]["username"] == "testuser"
        
        mock_create_user.assert_called_once()
    
    @patch('app.core.supabase.supabase_auth.create_user')
    def test_signup_failure(self, mock_create_user):
        """Test failed user signup"""
        mock_create_user.return_value = None
        
        signup_data = {
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        response = self.client.post("/api/v1/auth/signup", json=signup_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Failed to create user"
    
    @patch('app.core.supabase.supabase_auth.sign_in_user')
    def test_signin_success(self, mock_sign_in):
        """Test successful user signin"""
        mock_sign_in.return_value = {
            "user": self.mock_user_data,
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600
        }
        
        signin_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = self.client.post("/api/v1/auth/signin", json=signin_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Sign in successful"
        assert data["tokens"]["access_token"] == "test-access-token"
        assert data["tokens"]["refresh_token"] == "test-refresh-token"
        assert data["user"]["email"] == "test@example.com"
    
    @patch('app.core.supabase.supabase_auth.sign_in_user')
    def test_signin_failure(self, mock_sign_in):
        """Test failed user signin"""
        mock_sign_in.return_value = None
        
        signin_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/api/v1/auth/signin", json=signin_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid email or password"
    
    @patch('app.core.supabase.supabase_auth.refresh_token')
    def test_refresh_token_success(self, mock_refresh):
        """Test successful token refresh"""
        mock_refresh.return_value = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 3600
        }
        
        refresh_data = {
            "refresh_token": "valid-refresh-token"
        }
        
        response = self.client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Token refreshed successfully"
        assert data["tokens"]["access_token"] == "new-access-token"
    
    @patch('app.core.supabase.supabase_auth.refresh_token')
    def test_refresh_token_failure(self, mock_refresh):
        """Test failed token refresh"""
        mock_refresh.return_value = None
        
        refresh_data = {
            "refresh_token": "invalid-refresh-token"
        }
        
        response = self.client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid or expired refresh token"
    
    @patch('app.api.deps.get_current_user_from_supabase')
    def test_get_current_user_info_success(self, mock_get_user):
        """Test successful get current user info"""
        mock_get_user.return_value = self.mock_user_data
        
        headers = {"Authorization": "Bearer valid-token"}
        response = self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["role"] == "user"
    
    def test_get_current_user_info_no_token(self):
        """Test get current user info without token"""
        response = self.client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('app.core.supabase.supabase_auth.verify_jwt_token')
    def test_verify_token_valid(self, mock_verify):
        """Test token verification with valid token"""
        mock_verify.return_value = {
            "sub": "test-user-id",
            "exp": 1640995200  # Example timestamp
        }
        
        headers = {"Authorization": "Bearer valid-token"}
        response = self.client.post("/api/v1/auth/verify", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True
        assert data["user_id"] == "test-user-id"
    
    @patch('app.core.supabase.supabase_auth.verify_jwt_token')
    def test_verify_token_invalid(self, mock_verify):
        """Test token verification with invalid token"""
        mock_verify.return_value = None
        
        headers = {"Authorization": "Bearer invalid-token"}
        response = self.client.post("/api/v1/auth/verify", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
    
    @patch('app.api.deps.get_current_user_from_supabase')
    @patch('app.core.supabase.supabase_auth.update_user')
    def test_update_profile_success(self, mock_update, mock_get_user):
        """Test successful profile update"""
        mock_get_user.return_value = self.mock_user_data
        
        updated_user_data = self.mock_user_data.copy()
        updated_user_data["user_metadata"]["full_name"] = "Updated Name"
        mock_update.return_value = updated_user_data
        
        update_data = {
            "full_name": "Updated Name"
        }
        
        headers = {"Authorization": "Bearer valid-token"}
        response = self.client.put("/api/v1/auth/profile", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Profile updated successfully"
        assert data["user"]["full_name"] == "Updated Name"
    
    @patch('app.api.deps.get_current_user_from_supabase')
    def test_update_profile_no_data(self, mock_get_user):
        """Test profile update with no data provided"""
        mock_get_user.return_value = self.mock_user_data
        
        update_data = {}
        
        headers = {"Authorization": "Bearer valid-token"}
        response = self.client.put("/api/v1/auth/profile", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "At least one field must be provided for update" in data["detail"]
    
    @patch('app.api.deps.get_current_user_from_supabase')
    @patch('app.core.supabase.supabase_auth.sign_out_user')
    def test_signout_success(self, mock_signout, mock_get_user):
        """Test successful user signout"""
        mock_signout.return_value = True
        
        headers = {"Authorization": "Bearer valid-token"}
        response = self.client.post("/api/v1/auth/signout", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Sign out successful"
    
    @patch('app.api.deps.get_current_user_from_supabase')
    @patch('app.core.supabase.supabase_auth.delete_user')
    def test_delete_account_success(self, mock_delete, mock_get_user):
        """Test successful account deletion"""
        mock_get_user.return_value = self.mock_user_data
        mock_delete.return_value = True
        
        headers = {"Authorization": "Bearer valid-token"}
        response = self.client.delete("/api/v1/auth/account", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Account deleted successfully"


class TestUserManagementEndpoints:
    """Test user management endpoints (admin only)"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        self.admin_user_data = {
            "id": "admin-user-id",
            "email": "admin@example.com",
            "user_metadata": {
                "username": "admin",
                "full_name": "Admin User",
                "role": "super_admin"
            },
            "app_metadata": {
                "role": "super_admin"
            },
            "created_at": "2024-01-01T00:00:00Z",
            "confirmed_at": "2024-01-01T00:30:00Z"
        }
        
        self.regular_user_data = {
            "id": "regular-user-id",
            "email": "user@example.com",
            "user_metadata": {
                "username": "regularuser",
                "full_name": "Regular User",
                "role": "user"
            },
            "app_metadata": {
                "role": "user"
            },
            "created_at": "2024-01-01T00:00:00Z",
            "confirmed_at": "2024-01-01T00:30:00Z"
        }
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.list_users')
    def test_get_users_success(self, mock_list_users, mock_get_admin):
        """Test successful get users list"""
        mock_get_admin.return_value = self.admin_user_data
        mock_list_users.return_value = {
            "users": [self.admin_user_data, self.regular_user_data]
        }
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.get("/api/v1/users/", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["users"]) == 2
        assert data["users"][0]["email"] == "admin@example.com"
        assert data["users"][1]["email"] == "user@example.com"
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.list_users')
    def test_get_users_with_pagination(self, mock_list_users, mock_get_admin):
        """Test get users with pagination"""
        mock_get_admin.return_value = self.admin_user_data
        mock_list_users.return_value = {
            "users": [self.admin_user_data, self.regular_user_data]
        }
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.get("/api/v1/users/?skip=0&limit=1", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["users"]) == 1  # Limited to 1
    
    def test_get_users_unauthorized(self):
        """Test get users without admin token"""
        response = self.client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.create_user')
    @patch('app.core.supabase.supabase_auth.update_user')
    def test_create_user_success(self, mock_update_user, mock_create_user, mock_get_admin):
        """Test successful user creation"""
        mock_get_admin.return_value = self.admin_user_data
        mock_create_user.return_value = self.regular_user_data
        mock_update_user.return_value = self.regular_user_data
        
        user_data = {
            "username": "newuser",
            "password": "password123",
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "user"
        }
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.post("/api/v1/users/", json=user_data, headers=headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["username"] == "regularuser"
        
        mock_create_user.assert_called_once()
        mock_update_user.assert_called_once()
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.create_user')
    def test_create_user_failure(self, mock_create_user, mock_get_admin):
        """Test failed user creation"""
        mock_get_admin.return_value = self.admin_user_data
        mock_create_user.return_value = None
        
        user_data = {
            "username": "newuser",
            "password": "password123",
            "email": "newuser@example.com",
            "role": "user"
        }
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.post("/api/v1/users/", json=user_data, headers=headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Failed to create user"
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.get_user_by_id')
    @patch('app.core.supabase.supabase_auth.update_user')
    def test_update_user_success(self, mock_update_user, mock_get_user, mock_get_admin):
        """Test successful user update"""
        mock_get_admin.return_value = self.admin_user_data
        mock_get_user.return_value = self.regular_user_data
        
        updated_user_data = self.regular_user_data.copy()
        updated_user_data["user_metadata"]["full_name"] = "Updated Name"
        mock_update_user.return_value = updated_user_data
        
        update_data = {
            "full_name": "Updated Name"
        }
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.put("/api/v1/users/regular-user-id", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.get_user_by_id')
    def test_update_user_not_found(self, mock_get_user, mock_get_admin):
        """Test update user that doesn't exist"""
        mock_get_admin.return_value = self.admin_user_data
        mock_get_user.return_value = None
        
        update_data = {
            "full_name": "Updated Name"
        }
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.put("/api/v1/users/nonexistent-id", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.get_user_by_id')
    def test_update_user_no_data(self, mock_get_user, mock_get_admin):
        """Test update user with no data provided"""
        mock_get_admin.return_value = self.admin_user_data
        mock_get_user.return_value = self.regular_user_data
        
        update_data = {}
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.put("/api/v1/users/regular-user-id", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "At least one field must be provided for update" in data["detail"]
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.get_user_by_id')
    @patch('app.core.supabase.supabase_auth.delete_user')
    def test_delete_user_success(self, mock_delete_user, mock_get_user, mock_get_admin):
        """Test successful user deletion"""
        mock_get_admin.return_value = self.admin_user_data
        mock_get_user.return_value = self.regular_user_data
        mock_delete_user.return_value = True
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.delete("/api/v1/users/regular-user-id", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User deleted successfully"
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.get_user_by_id')
    def test_delete_user_not_found(self, mock_get_user, mock_get_admin):
        """Test delete user that doesn't exist"""
        mock_get_admin.return_value = self.admin_user_data
        mock_get_user.return_value = None
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.delete("/api/v1/users/nonexistent-id", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"
    
    @patch('app.api.deps.get_current_active_superuser')
    @patch('app.core.supabase.supabase_auth.get_user_by_id')
    def test_delete_user_self_deletion(self, mock_get_user, mock_get_admin):
        """Test admin trying to delete their own account"""
        mock_get_admin.return_value = self.admin_user_data
        mock_get_user.return_value = self.admin_user_data
        
        headers = {"Authorization": "Bearer admin-token"}
        response = self.client.delete("/api/v1/users/admin-user-id", headers=headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Cannot delete your own account"


class TestSupabaseAuthService:
    """Test Supabase authentication service"""
    
    def setup_method(self):
        """Setup test environment"""
        from app.core.supabase import SupabaseAuthService
        self.auth_service = SupabaseAuthService()
    
    @patch('app.core.supabase.jwt.decode')
    def test_verify_jwt_token_valid(self, mock_jwt_decode):
        """Test JWT token verification with valid token"""
        mock_jwt_decode.return_value = {
            "sub": "test-user-id",
            "exp": 1640995200,
            "aud": "test-audience"
        }
        
        result = self.auth_service.verify_jwt_token("valid-token")
        
        assert result is not None
        assert result["sub"] == "test-user-id"
        assert result["exp"] == 1640995200
    
    @patch('app.core.supabase.jwt.decode')
    def test_verify_jwt_token_invalid(self, mock_jwt_decode):
        """Test JWT token verification with invalid token"""
        from jose import JWTError
        mock_jwt_decode.side_effect = JWTError("Invalid token")
        
        result = self.auth_service.verify_jwt_token("invalid-token")
        
        assert result is None
    
    def test_get_user_id_from_token_valid(self):
        """Test extracting user ID from valid token"""
        with patch.object(self.auth_service, 'verify_jwt_token') as mock_verify:
            mock_verify.return_value = {"sub": "test-user-id"}
            
            user_id = self.auth_service.get_user_id_from_token("valid-token")
            
            assert user_id == "test-user-id"
    
    def test_get_user_id_from_token_invalid(self):
        """Test extracting user ID from invalid token"""
        with patch.object(self.auth_service, 'verify_jwt_token') as mock_verify:
            mock_verify.return_value = None
            
            user_id = self.auth_service.get_user_id_from_token("invalid-token")
            
            assert user_id is None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])