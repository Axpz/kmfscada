from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.core.supabase import supabase_auth
from app.schemas.user import (
    UserCreateValidator, 
    SuperUserUpdateValidator, 
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateValidator,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
) -> Dict[str, Any]:
    """Create a new user (admin only)"""
    try:
        logger.info(f"Admin {current_user.get('id')} creating user: {user_data.email}")
        
        # Prepare user metadata
        user_metadata = {}
        if user_data.username:
            user_metadata["username"] = user_data.username
        if user_data.full_name:
            user_metadata["full_name"] = user_data.full_name
        
        # Create user in Supabase
        supabase_user = await supabase_auth.create_user(
            email=user_data.email,
            password=user_data.password,
            user_metadata=user_metadata
        )
        
        return supabase_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    update_data: SuperUserUpdateValidator,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
) -> Dict[str, Any]:
    """Update user information (admin only)"""
    try:
        logger.info(f"Admin {current_user.get('id')} updating user: {user_id}")
        
        # Get current user data
        user_data = await supabase_auth.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        user_metadata = user_data.get("user_metadata", {}).copy()
        if update_data.role:
            user_metadata["role"] = update_data.role.value
        if update_data.username:
            user_metadata["username"] = update_data.username
        if update_data.full_name:
            user_metadata["full_name"] = update_data.full_name

        supabase_update_data = {"user_metadata": user_metadata}
        if update_data.password:
            supabase_update_data["password"] = update_data.password
        
        return await supabase_auth.update_user(user_id, supabase_update_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
) -> Dict[str, Any]:
    """Delete user (admin only)"""
    try:
        logger.info(f"Admin {current_user.get('id')} deleting user: {user_id}")
        
        # Check if user exists first
        user_data = await supabase_auth.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deleting themselves
        if user_id == current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        success = await supabase_auth.delete_user(user_id)
        if success:
            logger.info(f"User {user_id} deleted successfully by admin {current_user.get('id')}")
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete user"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user"
        ) 