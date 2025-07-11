#!/usr/bin/env python3
"""
Test script to verify the complete authentication flow
"""
import asyncio
import httpx
from app.core.supabase import supabase_auth
from app.core.config import settings

async def test_auth_flow():
    """Test the complete authentication flow"""
    print("Testing complete authentication flow...")
    
    # Test 1: Create a test user
    print("\n1. Creating test user...")
    test_email = "test@example.com"
    test_password = "testpassword123"
    
    try:
        user = await supabase_auth.create_user(
            email=test_email,
            password=test_password,
            user_metadata={"username": "testuser", "full_name": "Test User"}
        )
        if user:
            print(f"✓ User created: {user.get('id')}")
        else:
            print("✗ Failed to create user")
            return
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return
    
    # Test 2: Sign in user
    print("\n2. Signing in user...")
    try:
        signin_result = await supabase_auth.sign_in_user(test_email, test_password)
        if signin_result:
            access_token = signin_result.get("access_token")
            print(f"✓ User signed in successfully")
            print(f"  Access token: {access_token[:50]}...")
        else:
            print("✗ Failed to sign in user")
            return
    except Exception as e:
        print(f"✗ Error signing in user: {e}")
        return
    
    # Test 3: Verify JWT token
    print("\n3. Verifying JWT token...")
    try:
        payload = supabase_auth.verify_jwt_token(access_token)
        if payload:
            user_id = payload.get("sub")
            print(f"✓ JWT token verified successfully")
            print(f"  User ID: {user_id}")
            print(f"  Token payload: {payload}")
        else:
            print("✗ Failed to verify JWT token")
            return
    except Exception as e:
        print(f"✗ Error verifying JWT token: {e}")
        return
    
    # Test 4: Get user by ID
    print("\n4. Getting user by ID...")
    try:
        user_data = await supabase_auth.get_user_by_id(user_id)
        if user_data:
            print(f"✓ User data retrieved successfully")
            print(f"  Email: {user_data.get('email')}")
            print(f"  Created at: {user_data.get('created_at')}")
        else:
            print("✗ Failed to get user data")
    except Exception as e:
        print(f"✗ Error getting user data: {e}")
    
    # Test 5: Clean up - delete test user
    print("\n5. Cleaning up test user...")
    try:
        success = await supabase_auth.delete_user(user_id)
        if success:
            print("✓ Test user deleted successfully")
        else:
            print("✗ Failed to delete test user")
    except Exception as e:
        print(f"✗ Error deleting test user: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow()) 