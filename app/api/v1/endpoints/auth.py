from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api import deps
from app.core.supabase import supabase_auth
from app.schemas.user import (
    UserSigninValidator, 
    UserUpdateValidator, 
    RefreshTokenValidator,
)
from app.services.audit_log_service import AuditLogService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/me")
async def get_current_user_info(
    supabase_user: Dict[str, Any] = Depends(deps.get_current_user_from_supabase)
) -> Dict[str, Any]:
    """Get current user information from Supabase"""
    return supabase_user


@router.post("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Verify JWT token validity"""
    return supabase_auth.verify_jwt_token(credentials.credentials)


@router.post("/signin")
async def signin_user(
    user_data: UserSigninValidator,
    db: Session = Depends(deps.get_db),
) -> Dict[str, Any]:
    """Sign in user with email and password"""
    logger.info(f"Signing in user: {user_data}")
    resp = await supabase_auth.sign_in_user(user_data.email, user_data.password)
    logger.info(f"Sign in response: {resp}")
    AuditLogService(db).create_log_entry(
        email=user_data.email,
        action="signin_user",
        detail=f"用户{user_data.email}登录"
    )
    return resp.json()


@router.post("/refresh")
async def refresh_token(token_data: RefreshTokenValidator) -> Dict[str, Any]:
    """Refresh access token using refresh token"""
    return await supabase_auth.refresh_token(token_data.refresh_token)


@router.post("/signout")
async def signout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(deps.get_db),
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Sign out user"""
    AuditLogService(db).create_log_entry(
        email=current_user.get("email"),
        action="signout_user",
        detail=f"用户{current_user.get("email")}登出"
    )
    return await supabase_auth.sign_out_user(credentials.credentials)


@router.put("/update")
async def update_user_profile(
    profile_data: UserUpdateValidator,
    db: Session = Depends(deps.get_db),
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Update user profile in Supabase"""
    try:
        user_id = current_user.get("id")

        logger.info(f"Updating user profile: {profile_data}")
        logger.info(f"Supabase user: {current_user}")
        
        # Check if any updates are provided
        if not any([profile_data.full_name, profile_data.username, profile_data.password, profile_data.new_password]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="至少需要提供一个字段用于更新"
            )
        
        if profile_data.new_password:
            if profile_data.password == profile_data.new_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="新密码不能与旧密码相同"
                )
            try:
                res = await supabase_auth.sign_in_user(current_user.get("email"), profile_data.password)
                if not res.json().get("access_token"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="密码验证失败"
                    )
            except Exception as e:
                logger.info(f"Sign in Exception: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="密码验证失败"
                )
        
        # Prepare update data
        update_data = {}
        if profile_data.full_name or profile_data.username:
            user_metadata = current_user.get("user_metadata", {}).copy()
            if profile_data.full_name:
                user_metadata["full_name"] = profile_data.full_name
            if profile_data.username:
                user_metadata["username"] = profile_data.username
            update_data["user_metadata"] = user_metadata

        if profile_data.new_password:
            update_data["password"] = profile_data.new_password
            
        result = await supabase_auth.update_user(user_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
        
        AuditLogService(db).create_log_entry(
            email=current_user.get("email"),
            action="update_user_profile",
            detail=f"用户{current_user.get("email")}更新资料"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile update failed"
        )
