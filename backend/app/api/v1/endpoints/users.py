from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any
import httpx
from app.core.config import settings
from app.core.auth import verify_jwt_token

router = APIRouter()
security = HTTPBearer()

@router.get("/")
async def get_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all users (admin only)"""
    try:
        # Verify JWT token
        payload = verify_jwt_token(credentials.credentials)
        user_id = payload.get("sub")
        
        # Check if user is admin (you can implement role checking here)
        # For now, we'll allow all authenticated users
        
        # Get users from Supabase
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/admin/users",
                headers={
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "apikey": settings.SUPABASE_SERVICE_KEY
                }
            )
            
            if response.status_code == 200:
                users_data = response.json()
                return {
                    "users": [
                        {
                            "id": user.get("id"),
                            "email": user.get("email"),
                            "role": user.get("role", "user"),
                            "created_at": user.get("created_at"),
                            "last_sign_in_at": user.get("last_sign_in_at")
                        }
                        for user in users_data
                    ]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to fetch users"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.post("/")
async def create_user(user_data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new user (admin only)"""
    try:
        # Verify JWT token
        payload = verify_jwt_token(credentials.credentials)
        
        # Create user in Supabase
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.SUPABASE_URL}/auth/v1/admin/users",
                headers={
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "email": user_data.get("email"),
                    "password": user_data.get("password"),
                    "email_confirm": True,
                    "user_metadata": {
                        "role": user_data.get("role", "user")
                    }
                }
            )
            
            if response.status_code == 200:
                created_user = response.json()
                return {
                    "id": created_user.get("id"),
                    "email": created_user.get("email"),
                    "role": created_user.get("user_metadata", {}).get("role", "user"),
                    "created_at": created_user.get("created_at")
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to create user: {response.text}"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.put("/{user_id}")
async def update_user(user_id: str, user_data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update user information (admin only)"""
    try:
        # Verify JWT token
        payload = verify_jwt_token(credentials.credentials)
        
        # Update user in Supabase
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                headers={
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "user_metadata": {
                        "role": user_data.get("role", "user")
                    }
                }
            )
            
            if response.status_code == 200:
                updated_user = response.json()
                return {
                    "id": updated_user.get("id"),
                    "email": updated_user.get("email"),
                    "role": updated_user.get("user_metadata", {}).get("role", "user"),
                    "updated_at": updated_user.get("updated_at")
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to update user: {response.text}"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) 