from typing import Generator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.supabase import supabase_auth
from app.core.logging import get_logger

logger = get_logger(__name__)

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

    logger.info("Processing JWT credentials", extra={
        "extra_fields": {
            "credentials_type": type(credentials).__name__,
            "has_credentials": bool(credentials)
        }
    })
    
    # Verify JWT token
    payload = supabase_auth.verify_jwt_token(token)
    if not payload:
        logger.warning("Invalid JWT token provided", extra={
        "extra_fields": {
            "auth_error": "invalid_token",
            "token_length": len(token) if token else 0
        }
    })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"JWT token verified successfully {payload}")

    user_id = payload.get("sub")
    if not user_id:
        logger.warning("No user ID found in JWT token", extra={
            "extra_fields": {
                "auth_error": "no_user_id",
                "payload_keys": list(payload.keys()) if payload else []
            }
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from Supabase
    user_data = await supabase_auth.get_user_by_id(user_id)
    if not user_data:
        logger.warning("User not found in Supabase", extra={
            "extra_fields": {
                "auth_error": "user_not_found",
                "user_id": user_id
            }
        })
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
        logger.warning("Inactive user attempted access", extra={
            "extra_fields": {
                "auth_error": "inactive_user",
                "user_id": supabase_user.get('id')
            }
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return supabase_user


async def get_current_active_superuser(
    supabase_user: Dict[str, Any] = Depends(get_current_user_from_supabase)
) -> Dict[str, Any]:
    """Get current active superuser from Supabase."""
    # Check if user has admin role in user_metadata
    logger.info(f"Current supabase user: {supabase_user}")
    user_metadata = supabase_user.get("user_metadata", {})
    if not user_metadata.get("role") == "super_admin":
        logger.warning("Non-admin user attempted admin access", extra={
            "extra_fields": {
                "auth_error": "insufficient_privileges",
                "user_id": supabase_user.get('id'),
                "user_role": user_metadata.get("role")
            }
        })
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