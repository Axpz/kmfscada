#!/usr/bin/env python3
"""
Test script to verify JWT token validation
"""
import asyncio
import httpx
from app.core.supabase import supabase_auth
from app.core.config import settings

async def test_jwt_verification():
    """Test JWT token verification"""
    print("Testing JWT token verification...")
    print(f"SUPABASE_JWT_SECRET: {settings.SUPABASE_JWT_SECRET[:20]}...")
    
    # Test with a sample token (this will fail, but shows the process)
    sample_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    try:
        result = supabase_auth.verify_jwt_token(sample_token)
        print(f"JWT verification result: {result}")
    except Exception as e:
        print(f"JWT verification error: {e}")

async def test_supabase_connection():
    """Test Supabase connection"""
    print("\nTesting Supabase connection...")
    print(f"SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"SUPABASE_SERVICE_KEY: {settings.SUPABASE_SERVICE_KEY[:20]}...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/health",
                headers={
                    "apikey": settings.SUPABASE_ANON_KEY
                }
            )
            print(f"Supabase health check status: {response.status_code}")
            if response.status_code == 200:
                print("Supabase is running and accessible")
            else:
                print(f"Supabase health check failed: {response.text}")
    except Exception as e:
        print(f"Supabase connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_jwt_verification())
    asyncio.run(test_supabase_connection()) 