from datetime import datetime
from enum import Enum
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserValidatorMixin:
    """Common validation logic mixin class"""
    
    @staticmethod
    def validate_username(v: Optional[str]) -> Optional[str]:
        """Username validation"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not 3 <= len(v) <= 20:
                raise ValueError("Username must be between 3 and 20 characters")
        return v
    
    @staticmethod
    def validate_password(v: Optional[str], required: bool = True) -> Optional[str]:
        """Password validation"""
        # if v is not None:
        #     if len(v) < 8:
        #         raise ValueError("Password must be at least 8 characters long")
        #     if not re.search(r"[A-Za-z]", v):
        #         raise ValueError("Password must contain at least one letter")
        #     if not re.search(r"\d", v):
        #         raise ValueError("Password must contain at least one number")
        #     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
        #         raise ValueError("Password must contain at least one special character")
        # elif required:
        #     raise ValueError("Password is required")
        return v
    
    @staticmethod
    def validate_role(v: Optional[str]) -> Optional[str]:
        """Role validation"""
        if v is not None and v not in [role.value for role in UserRole]:
            valid_roles = ", ".join([role.value for role in UserRole])
            raise ValueError(f"Role must be one of: {valid_roles}")
        return v
    
    @staticmethod
    def validate_full_name(v: Optional[str]) -> Optional[str]:
        """Full name validation"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) < 3 or len(v) > 100:
                raise ValueError("Full name must be between 3 and 100 characters")
        return v


class UserCreateValidator(BaseModel, UserValidatorMixin):
    """User creation validation model"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    username: Optional[str] = None
    password: str
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[UserRole] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_username(v)

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        return cls.validate_password(v, required=True)
    
    @field_validator("full_name")
    @classmethod
    def full_name_valid(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_full_name(v)
    
    @field_validator("role")
    @classmethod
    def role_valid(cls, v: Optional[UserRole]) -> Optional[UserRole]:
        return cls.validate_role(v)


class UserUpdateValidator(BaseModel, UserValidatorMixin):
    """User update validation model"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    username: Optional[str] = None
    password: Optional[str] = None
    new_password: Optional[str] = None
    full_name: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_username(v)

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_password(v, required=False)

    @field_validator("full_name")
    @classmethod
    def full_name_valid(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_full_name(v)


class SuperUserUpdateValidator(UserUpdateValidator):
    """Super user update validation model"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    role: Optional[UserRole] = None

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: Optional[UserRole]) -> Optional[UserRole]:
        return cls.validate_role(v)


class UserSignupValidator(BaseModel, UserValidatorMixin):
    """User signup validation model"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_username(v)

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        return cls.validate_password(v, required=True)

    @field_validator("full_name")
    @classmethod
    def full_name_valid(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_full_name(v)


class UserSigninValidator(BaseModel, UserValidatorMixin):
    """User signin validation model"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        return cls.validate_password(v, required=True)


class RefreshTokenValidator(BaseModel):
    """Refresh token validation model"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    refresh_token: str


