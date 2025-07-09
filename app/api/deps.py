from typing import Generator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.supabase import supabase_auth
import logging

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


def get_db() -> Generator:
    """Dependency to get database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user_from_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current user from Supabase JWT token."""
    token = credentials.credentials
    
    # Verify JWT token
    payload = supabase_auth.verify_jwt_token(token)
    if not payload:
        logger.warning("Invalid JWT token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("No user ID found in JWT token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from Supabase
    user_data = await supabase_auth.get_user_by_id(user_id)
    if not user_data:
        logger.warning(f"User {user_id} not found in Supabase")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_data


async def get_current_active_user(
    supabase_user: Dict[str, Any] = Depends(get_current_user_from_supabase)
) -> Dict[str, Any]:
    """Get current active user from Supabase."""
    # Check if user is confirmed (active)
    if not supabase_user.get("confirmed_at"):
        logger.warning(f"Inactive user {supabase_user.get('id')} attempted access")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return supabase_user


async def get_current_active_superuser(
    supabase_user: Dict[str, Any] = Depends(get_current_user_from_supabase)
) -> Dict[str, Any]:
    """Get current active superuser from Supabase."""
    # Check if user has admin role in app_metadata
    app_metadata = supabase_user.get("app_metadata", {})
    if not app_metadata.get("role") == "admin":
        logger.warning(f"Non-admin user {supabase_user.get('id')} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges"
        )
    return supabase_user


async def get_supabase_user_only(
    supabase_user: Dict[str, Any] = Depends(get_current_user_from_supabase)
) -> Dict[str, Any]:
    """Get Supabase user data only."""
    return supabase_user


async def get_optional_supabase_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get Supabase user data if token is provided (optional authentication)."""
    if not credentials:
        return None
    
    try:
        return await get_current_user_from_supabase(credentials)
    except HTTPException:
        return None 