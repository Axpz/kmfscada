from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.api import deps
from app.core.supabase import supabase_auth
from app.schemas.user import (
    UserSigninValidator, 
    UserUpdateValidator, 
    RefreshTokenValidator,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/me")
async def get_current_user_info(
    supabase_user: Dict[str, Any] = Depends(deps.get_supabase_user_only)
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
async def signin_user(user_data: UserSigninValidator) -> Dict[str, Any]:
    """Sign in user with email and password"""
    return await supabase_auth.sign_in_user(user_data.email, user_data.password)


@router.post("/refresh")
async def refresh_token(token_data: RefreshTokenValidator) -> Dict[str, Any]:
    """Refresh access token using refresh token"""
    return await supabase_auth.refresh_token(token_data.refresh_token)


@router.post("/signout")
async def signout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Sign out user"""
    return await supabase_auth.sign_out_user(credentials.credentials)


@router.put("/update")
async def update_user_profile(
    profile_data: UserUpdateValidator,
    supabase_user: Dict[str, Any] = Depends(deps.get_supabase_user_only)
) -> Dict[str, Any]:
    """Update user profile in Supabase"""
    try:
        user_id = supabase_user.get("id")
        
        # Check if any updates are provided
        if not any([profile_data.full_name, profile_data.username, profile_data.password]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update"
            )
        
        # Prepare update data
        update_data = {}
        if profile_data.full_name or profile_data.username:
            user_metadata = supabase_user.get("user_metadata", {}).copy()
            if profile_data.full_name:
                user_metadata["full_name"] = profile_data.full_name
            if profile_data.username:
                user_metadata["username"] = profile_data.username
            update_data["user_metadata"] = user_metadata

        if profile_data.password:
            update_data["password"] = profile_data.password
            
        result = await supabase_auth.update_user(user_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
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
