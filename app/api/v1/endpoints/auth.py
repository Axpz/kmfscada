from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.api import deps
from app.core.config import settings
from app.core.supabase import supabase_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.get("/me")
async def get_current_user_info(
    supabase_user: Dict[str, Any] = Depends(deps.get_supabase_user_only)
):
    """Get current user information from Supabase"""
    return {
        "id": supabase_user.get("id"),
        "email": supabase_user.get("email"),
        "role": supabase_user.get("app_metadata", {}).get("role", "user"),
        "created_at": supabase_user.get("created_at"),
        "confirmed_at": supabase_user.get("confirmed_at"),
        "user_metadata": supabase_user.get("user_metadata", {}),
        "app_metadata": supabase_user.get("app_metadata", {})
    }


@router.post("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify JWT token validity"""
    try:
        payload = supabase_auth.verify_jwt_token(credentials.credentials)
        if payload:
            return {
                "valid": True, 
                "user_id": payload.get("sub"),
                "aud": payload.get("aud"),
                "exp": payload.get("exp")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/signup")
async def signup_user(email: str, password: str, username: str = None, full_name: str = None):
    """Create a new user in Supabase"""
    try:
        # Prepare user metadata
        user_metadata = {}
        if username:
            user_metadata["username"] = username
        if full_name:
            user_metadata["full_name"] = full_name
        
        # Create user in Supabase
        supabase_user = await supabase_auth.create_user(
            email=email,
            password=password,
            user_metadata=user_metadata
        )
        
        if supabase_user:
            logger.info(f"User {email} registered successfully")
            return {
                "message": "User created successfully",
                "user_id": supabase_user.get("id"),
                "email": supabase_user.get("email")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/signin")
async def signin_user(email: str, password: str):
    """Sign in user with email and password"""
    try:
        result = await supabase_auth.sign_in_user(email, password)
        if result:
            return {
                "message": "Sign in successful",
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "user": {
                    "id": result.get("user", {}).get("id"),
                    "email": result.get("user", {}).get("email")
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except Exception as e:
        logger.error(f"Sign in failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        result = await supabase_auth.refresh_token(refresh_token)
        if result:
            return {
                "message": "Token refreshed successfully",
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/signout")
async def signout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Sign out user"""
    try:
        success = await supabase_auth.sign_out_user(credentials.credentials)
        if success:
            return {"message": "Sign out successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sign out failed"
            )
    except Exception as e:
        logger.error(f"Sign out failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sign out failed"
        )


@router.put("/profile")
async def update_user_profile(
    full_name: str = None,
    username: str = None,
    supabase_user: Dict[str, Any] = Depends(deps.get_supabase_user_only)
):
    """Update user profile in Supabase"""
    try:
        user_id = supabase_user.get("id")
        
        # Prepare update data
        update_data = {}
        if full_name or username:
            user_metadata = supabase_user.get("user_metadata", {})
            if full_name:
                user_metadata["full_name"] = full_name
            if username:
                user_metadata["username"] = username
            update_data["user_metadata"] = user_metadata
        
        if update_data:
            result = await supabase_auth.update_user(user_id, update_data)
            if result:
                return {
                    "message": "Profile updated successfully",
                    "user": {
                        "id": result.get("id"),
                        "email": result.get("email"),
                        "user_metadata": result.get("user_metadata", {})
                    }
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update profile"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No updates provided"
            )
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile update failed"
        )


@router.delete("/account")
async def delete_user_account(
    supabase_user: Dict[str, Any] = Depends(deps.get_supabase_user_only)
):
    """Delete user account from Supabase"""
    try:
        user_id = supabase_user.get("id")
        
        success = await supabase_auth.delete_user(user_id)
        if success:
            logger.info(f"User {user_id} account deleted successfully")
            return {"message": "Account deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete account"
            )
    except Exception as e:
        logger.error(f"Account deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion failed"
        )


@router.get("/users")
async def list_users(
    page: int = 1,
    per_page: int = 50,
    current_user = Depends(deps.get_current_active_superuser)
):
    """List users from Supabase (admin only)"""
    try:
        users = await supabase_auth.list_users(page=page, per_page=per_page)
        if users:
            return {
                "users": users,
                "page": page,
                "per_page": per_page
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to list users"
            )
    except Exception as e:
        logger.error(f"User listing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to list users"
        ) 