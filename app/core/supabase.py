from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from app.core.config import settings
import httpx
from jose import jwt, JWTError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SupabaseAuthService:
    """Optimized Supabase authentication service for SCADA system."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SERVICE_ROLE_KEY
        )
        self.jwt_secret = settings.JWT_SECRET
        self.jwt_audience = settings.JWT_AUDIENCE
        self.auth_url = f"{settings.SUPABASE_URL}/auth/v1"
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token from Supabase."""
        try:
            # For Supabase JWT tokens, we need to handle audience claims properly
            # The audience is typically the project reference ID
            decode_options = {
                "verify_aud": False  # Disable audience verification for now
            }
            
            # If we have a specific audience configured, use it
            if self.jwt_audience:
                payload = jwt.decode(
                    token, 
                    self.jwt_secret, 
                    algorithms=["HS256"],
                    audience=self.jwt_audience,
                    options=decode_options
                )
            else:
                payload = jwt.decode(
                    token, 
                    self.jwt_secret, 
                    algorithms=["HS256"],
                    options=decode_options
                )
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            # Log additional debugging information
            try:
                unverified_payload = jwt.decode(
                    token, 
                    options={"verify_signature": False}
                )
                logger.debug(f"Token payload (unverified): {unverified_payload}")
                logger.debug(f"Token audience: {unverified_payload.get('aud')}")
                logger.debug(f"Token issuer: {unverified_payload.get('iss')}")
            except Exception as debug_e:
                logger.debug(f"Could not decode token for debugging: {debug_e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from Supabase by user ID."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.auth_url}/admin/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {settings.SERVICE_ROLE_KEY}",
                        "apikey": settings.SERVICE_ROLE_KEY
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get user {user_id}: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user information from Supabase by email."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.auth_url}/admin/users",
                    headers={
                        "Authorization": f"Bearer {settings.SERVICE_ROLE_KEY}",
                        "apikey": settings.SERVICE_ROLE_KEY
                    },
                    params={"filter": f"email.eq.{email}"}
                )
                
                if response.status_code == 200:
                    users = response.json()
                    return users[0] if users else None
                else:
                    logger.error(f"Failed to get user by email {email}: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def create_user(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Create a new user in Supabase."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.auth_url}/admin/users",
                    headers={
                        "Authorization": f"Bearer {settings.SERVICE_ROLE_KEY}",
                        "apikey": settings.SERVICE_ROLE_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "email": email,
                        "password": password,
                        "email_confirm": True,
                        "user_metadata": user_metadata or {}
                    }
                )
                
                return response.json()
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user information in Supabase."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.put(
                    f"{self.auth_url}/admin/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {settings.SERVICE_ROLE_KEY}",
                        "apikey": settings.SERVICE_ROLE_KEY,
                        "Content-Type": "application/json"
                    },
                    json=updates
                )
                return resp.json()
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user from Supabase."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                return await client.delete(
                    f"{self.auth_url}/admin/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {settings.SERVICE_ROLE_KEY}",
                        "apikey": settings.SERVICE_ROLE_KEY
                    }
                )
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    async def list_users(self, page: int = 1, per_page: int = 50) -> Optional[List[Dict[str, Any]]]:
        """List users from Supabase."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.auth_url}/admin/users",
                    headers={
                        "Authorization": f"Bearer {settings.SERVICE_ROLE_KEY}",
                        "apikey": settings.SERVICE_ROLE_KEY
                    },
                    params={"page": page, "per_page": per_page}
                )
                return resp.json()
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """Extract user ID from JWT token."""
        payload = self.verify_jwt_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    async def sign_in_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Sign in user with email and password."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                return await client.post(
                    f"{self.auth_url}/token?grant_type=password",
                    headers={
                        "apikey": settings.ANON_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "email": email,
                        "password": password
                    }
                )
        except Exception as e:
            logger.error(f"Error signing in user {email}: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.auth_url}/token?grant_type=refresh_token",
                    headers={
                        "apikey": settings.ANON_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "refresh_token": refresh_token
                    }
                )
                return resp.json()
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    
    async def get_session(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get current session information."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                return await client.get(
                    f"{self.auth_url}/user",
                    headers={
                        "apikey": settings.ANON_KEY,
                        "Authorization": f"Bearer {access_token}"
                    }
                )
        except Exception as e:
            logger.debug(f"Error getting session: {e}")
            return None

    async def sign_out_user(self, access_token: str) -> Dict[str, Any]:
        """Sign out user: if session exists, call Supabase logout; if not, fallback to local logout."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                    f"{self.auth_url}/logout",
                    headers={
                        "apikey": settings.ANON_KEY,
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                )

            return response.json()



# Global instance
supabase_auth = SupabaseAuthService() 