from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.api import deps
from app.core.supabase import supabase_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_users(
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
):
    """Get all users (admin only)"""
    try:
        logger.info(f"Getting users: {current_user}")
        users = await supabase_auth.list_users()
        logger.info(f"Users: {users}")
        if users:
            return {
                "users": [
                    {
                        "id": user.get("id"),
                        "email": user.get("email"),
                        "role": user.get("user_metadata", {}).get("role", "user"),
                        "created_at": user.get("created_at"),
                        "last_sign_in_at": user.get("last_sign_in_at"),
                        "confirmed_at": user.get("confirmed_at")
                    }
                    for user in users.get("users", [])
                ]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users"
            )
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.post("/")
async def create_user(
    email: str,
    password: str,
    role: str = "user",
    username: str = None,
    full_name: str = None,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
):
    """Create a new user (admin only)"""
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
            # Set role in app_metadata
            await supabase_auth.update_user(
                supabase_user.get("id"),
                {"user_metadata": {"role": role}}
            )
            
            return {
                "id": supabase_user.get("id"),
                "email": supabase_user.get("email"),
                "role": role,
                "created_at": supabase_user.get("created_at")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    role: str = None,
    username: str = None,
    full_name: str = None,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
):
    """Update user information (admin only)"""
    try:
        # Get current user data
        user_data = await supabase_auth.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = {}
        
        if role:
            update_data["user_metadata"] = {"role": role}
        
        if username or full_name:
            user_metadata = user_data.get("user_metadata", {})
            if username:
                user_metadata["username"] = username
            if full_name:
                user_metadata["full_name"] = full_name
            update_data["user_metadata"] = user_metadata
        
        if update_data:
            result = await supabase_auth.update_user(user_id, update_data)
            if result:
                return {
                    "id": result.get("id"),
                    "email": result.get("email"),
                    "role": result.get("user_metadata", {}).get("role", "user"),
                    "user_metadata": result.get("user_metadata", {}),
                    "updated_at": result.get("updated_at")
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update user"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No updates provided"
            )
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
):
    """Delete user (admin only)"""
    try:
        success = await supabase_auth.delete_user(user_id)
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete user"
            )
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user"
        ) 