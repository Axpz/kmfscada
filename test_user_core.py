"""
核心用户功能单元测试
Core User Functionality Unit Tests

专注于测试用户相关的核心逻辑，不依赖外部服务
Focus on testing core user-related logic without external service dependencies
"""

import pytest
from datetime import datetime
from typing import Optional
from pydantic import ValidationError

from app.schemas.user import (
    UserRole,
    UserCreateValidator,
    UserUpdateValidator,
    SuperUserUpdateValidator,
    UserSignupValidator,
    UserSigninValidator,
    RefreshTokenValidator,
    UserResponse,
    UserListResponse,
    AuthTokens,
    AuthResponse,
    MessageResponse,
    TokenVerificationResponse,
    UserValidatorMixin
)


class TestUserRole:
    """测试用户角色枚举 / Test user role enumeration"""
    
    def test_user_role_values(self):
        """测试用户角色值 / Test user role values"""
        assert UserRole.USER == "user"
        assert UserRole.ADMIN == "admin"
        assert UserRole.SUPER_ADMIN == "super_admin"
    
    def test_user_role_enum_membership(self):
        """测试角色枚举成员 / Test role enum membership"""
        roles = [role.value for role in UserRole]
        assert "user" in roles
        assert "admin" in roles
        assert "super_admin" in roles
        assert len(roles) == 3


class TestUserValidatorMixin:
    """测试用户验证混合类 / Test user validator mixin"""
    
    def test_validate_username_valid(self):
        """测试有效用户名验证 / Test valid username validation"""
        valid_usernames = [
            "testuser",
            "test_user",
            "user123",
            "Test_User_123"
        ]
        
        for username in valid_usernames:
            result = UserValidatorMixin.validate_username(username)
            assert result == username
    
    def test_validate_username_invalid_length(self):
        """测试无效长度用户名 / Test invalid length usernames"""
        # 太短 / Too short
        with pytest.raises(ValueError, match="Username must be between 3 and 20 characters"):
            UserValidatorMixin.validate_username("ab")
        
        # 太长 / Too long
        with pytest.raises(ValueError, match="Username must be between 3 and 20 characters"):
            UserValidatorMixin.validate_username("a" * 21)
    
    def test_validate_username_invalid_characters(self):
        """测试无效字符用户名 / Test invalid character usernames"""
        invalid_usernames = [
            "test@user",
            "test-user",
            "test user",
            "test.user",
            "test#user"
        ]
        
        for username in invalid_usernames:
            with pytest.raises(ValueError, match="Username can only contain letters, numbers, and underscores"):
                UserValidatorMixin.validate_username(username)
    
    def test_validate_username_none_and_empty(self):
        """测试None和空用户名 / Test None and empty usernames"""
        assert UserValidatorMixin.validate_username(None) is None
        assert UserValidatorMixin.validate_username("") is None
        assert UserValidatorMixin.validate_username("   ") is None
    
    def test_validate_password_valid(self):
        """测试有效密码验证 / Test valid password validation"""
        # 注意：当前实现中密码验证被注释掉了，所以任何密码都会通过
        # Note: Password validation is currently commented out, so any password passes
        passwords = [
            "password123",
            "123",
            "abc",
            "Password123!",
            ""
        ]
        
        for password in passwords:
            result = UserValidatorMixin.validate_password(password, required=False)
            assert result == password
    
    def test_validate_role_valid(self):
        """测试有效角色验证 / Test valid role validation"""
        valid_roles = ["user", "admin", "super_admin"]
        
        for role in valid_roles:
            result = UserValidatorMixin.validate_role(role)
            assert result == role
    
    def test_validate_role_invalid(self):
        """测试无效角色验证 / Test invalid role validation"""
        with pytest.raises(ValueError, match="Role must be one of"):
            UserValidatorMixin.validate_role("invalid_role")
    
    def test_validate_role_none(self):
        """测试None角色 / Test None role"""
        assert UserValidatorMixin.validate_role(None) is None
    
    def test_validate_full_name_valid(self):
        """测试有效全名验证 / Test valid full name validation"""
        valid_names = [
            "John Doe",
            "Mary Jane Smith",
            "Jean-Pierre O'Connor",
            "Dr. Smith Jr."
        ]
        
        for name in valid_names:
            result = UserValidatorMixin.validate_full_name(name)
            assert result == name
    
    def test_validate_full_name_invalid(self):
        """测试无效全名验证 / Test invalid full name validation"""
        # 太长 / Too long
        with pytest.raises(ValueError, match="Full name must be less than 100 characters"):
            UserValidatorMixin.validate_full_name("a" * 101)
        
        # 无效字符 / Invalid characters
        with pytest.raises(ValueError, match="Full name can only contain"):
            UserValidatorMixin.validate_full_name("John@Doe")
    
    def test_validate_full_name_none_and_empty(self):
        """测试None和空全名 / Test None and empty full names"""
        assert UserValidatorMixin.validate_full_name(None) is None
        assert UserValidatorMixin.validate_full_name("") is None
        assert UserValidatorMixin.validate_full_name("   ") is None


class TestUserCreateValidator:
    """测试用户创建验证器 / Test user create validator"""
    
    def test_valid_user_creation(self):
        """测试有效用户创建 / Test valid user creation"""
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
    
    def test_minimal_user_creation(self):
        """测试最小用户创建 / Test minimal user creation"""
        user_data = UserCreateValidator(
            password="password123",
            email="test@example.com"
        )
        
        assert user_data.username is None
        assert user_data.password == "password123"
        assert user_data.email == "test@example.com"
        assert user_data.full_name is None
        assert user_data.role is None
    
    def test_invalid_email(self):
        """测试无效邮箱 / Test invalid email"""
        with pytest.raises(ValidationError):
            UserCreateValidator(
                password="password123",
                email="invalid-email"
            )
    
    def test_missing_required_fields(self):
        """测试缺少必需字段 / Test missing required fields"""
        # 缺少密码 / Missing password
        with pytest.raises(ValidationError):
            UserCreateValidator(
                email="test@example.com"
            )
        
        # 缺少邮箱 / Missing email
        with pytest.raises(ValidationError):
            UserCreateValidator(
                password="password123"
            )


class TestUserUpdateValidator:
    """测试用户更新验证器 / Test user update validator"""
    
    def test_valid_user_update(self):
        """测试有效用户更新 / Test valid user update"""
        update_data = UserUpdateValidator(
            username="newusername",
            password="newpassword123",
            full_name="New Full Name"
        )
        
        assert update_data.username == "newusername"
        assert update_data.password == "newpassword123"
        assert update_data.full_name == "New Full Name"
    
    def test_partial_user_update(self):
        """测试部分用户更新 / Test partial user update"""
        update_data = UserUpdateValidator(
            username="newusername"
        )
        
        assert update_data.username == "newusername"
        assert update_data.password is None
        assert update_data.full_name is None
    
    def test_empty_user_update(self):
        """测试空用户更新 / Test empty user update"""
        update_data = UserUpdateValidator()
        
        assert update_data.username is None
        assert update_data.password is None
        assert update_data.full_name is None


class TestSuperUserUpdateValidator:
    """测试超级用户更新验证器 / Test super user update validator"""
    
    def test_super_user_update_with_role(self):
        """测试包含角色的超级用户更新 / Test super user update with role"""
        update_data = SuperUserUpdateValidator(
            username="adminuser",
            role=UserRole.ADMIN
        )
        
        assert update_data.username == "adminuser"
        assert update_data.role == UserRole.ADMIN
    
    def test_super_user_update_role_only(self):
        """测试仅角色的超级用户更新 / Test super user update role only"""
        update_data = SuperUserUpdateValidator(
            role=UserRole.SUPER_ADMIN
        )
        
        assert update_data.role == UserRole.SUPER_ADMIN
        assert update_data.username is None


class TestUserSignupValidator:
    """测试用户注册验证器 / Test user signup validator"""
    
    def test_valid_signup(self):
        """测试有效注册 / Test valid signup"""
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
    
    def test_minimal_signup(self):
        """测试最小注册 / Test minimal signup"""
        signup_data = UserSignupValidator(
            email="signup@example.com",
            password="password123"
        )
        
        assert signup_data.email == "signup@example.com"
        assert signup_data.password == "password123"
        assert signup_data.username is None
        assert signup_data.full_name is None


class TestUserSigninValidator:
    """测试用户登录验证器 / Test user signin validator"""
    
    def test_valid_signin(self):
        """测试有效登录 / Test valid signin"""
        signin_data = UserSigninValidator(
            email="signin@example.com",
            password="password123"
        )
        
        assert signin_data.email == "signin@example.com"
        assert signin_data.password == "password123"
    
    def test_signin_missing_fields(self):
        """测试登录缺少字段 / Test signin missing fields"""
        with pytest.raises(ValidationError):
            UserSigninValidator(
                email="signin@example.com"
            )
        
        with pytest.raises(ValidationError):
            UserSigninValidator(
                password="password123"
            )


class TestRefreshTokenValidator:
    """测试刷新令牌验证器 / Test refresh token validator"""
    
    def test_valid_refresh_token(self):
        """测试有效刷新令牌 / Test valid refresh token"""
        token_data = RefreshTokenValidator(
            refresh_token="valid-refresh-token"
        )
        
        assert token_data.refresh_token == "valid-refresh-token"
    
    def test_missing_refresh_token(self):
        """测试缺少刷新令牌 / Test missing refresh token"""
        with pytest.raises(ValidationError):
            RefreshTokenValidator()


class TestResponseModels:
    """测试响应模型 / Test response models"""
    
    def test_user_response(self):
        """测试用户响应模型 / Test user response model"""
        user_response = UserResponse(
            id="test-id",
            email="test@example.com",
            role=UserRole.USER,
            username="testuser",
            full_name="Test User",
            created_at=datetime.now(),
            last_sign_in_at=datetime.now(),
            confirmed_at=datetime.now()
        )
        
        assert user_response.id == "test-id"
        assert user_response.email == "test@example.com"
        assert user_response.role == UserRole.USER
        assert user_response.username == "testuser"
        assert user_response.full_name == "Test User"
    
    def test_user_list_response(self):
        """测试用户列表响应模型 / Test user list response model"""
        users = [
            UserResponse(
                id="user1",
                email="user1@example.com",
                role=UserRole.USER
            ),
            UserResponse(
                id="user2",
                email="user2@example.com",
                role=UserRole.ADMIN
            )
        ]
        
        user_list_response = UserListResponse(
            users=users,
            total=2
        )
        
        assert len(user_list_response.users) == 2
        assert user_list_response.total == 2
    
    def test_auth_tokens(self):
        """测试认证令牌模型 / Test auth tokens model"""
        tokens = AuthTokens(
            access_token="access-token",
            refresh_token="refresh-token",
            expires_in=3600
        )
        
        assert tokens.access_token == "access-token"
        assert tokens.refresh_token == "refresh-token"
        assert tokens.token_type == "bearer"
        assert tokens.expires_in == 3600
    
    def test_auth_response(self):
        """测试认证响应模型 / Test auth response model"""
        user = UserResponse(
            id="test-id",
            email="test@example.com",
            role=UserRole.USER
        )
        
        tokens = AuthTokens(
            access_token="access-token",
            refresh_token="refresh-token",
            expires_in=3600
        )
        
        auth_response = AuthResponse(
            message="Success",
            tokens=tokens,
            user=user
        )
        
        assert auth_response.message == "Success"
        assert auth_response.tokens.access_token == "access-token"
        assert auth_response.user.email == "test@example.com"
    
    def test_message_response(self):
        """测试消息响应模型 / Test message response model"""
        message_response = MessageResponse(
            message="Operation successful"
        )
        
        assert message_response.message == "Operation successful"
        assert message_response.success is True
        
        # 测试失败响应 / Test failure response
        failure_response = MessageResponse(
            message="Operation failed",
            success=False
        )
        
        assert failure_response.message == "Operation failed"
        assert failure_response.success is False
    
    def test_token_verification_response(self):
        """测试令牌验证响应模型 / Test token verification response model"""
        verification_response = TokenVerificationResponse(
            valid=True,
            user_id="test-user-id",
            email="test@example.com",
            expires_at=datetime.now()
        )
        
        assert verification_response.valid is True
        assert verification_response.user_id == "test-user-id"
        assert verification_response.email == "test@example.com"
        
        # 测试无效令牌响应 / Test invalid token response
        invalid_response = TokenVerificationResponse(
            valid=False
        )
        
        assert invalid_response.valid is False
        assert invalid_response.user_id is None
        assert invalid_response.email is None


if __name__ == "__main__":
    # 运行测试 / Run tests
    pytest.main([__file__, "-v"])