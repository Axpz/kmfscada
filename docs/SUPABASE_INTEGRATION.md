# Supabase Integration Guide

This document explains how to use Supabase for user authentication in the SCADA system.

## Overview

The system uses Supabase for user authentication and management, while maintaining a local database for application-specific user data. This provides:

- Secure authentication via Supabase Auth
- User management through Supabase dashboard
- Local user data synchronization
- JWT token verification

## Configuration

### Environment Variables

Copy `env.example` to `.env` and configure the following variables:

```bash
# Supabase Configuration
SUPABASE_URL=http://localhost:8080
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters-long

# Supabase Auth Settings
SUPABASE_AUTH_ENABLED=true
SUPABASE_AUTO_CONFIRM=true
SUPABASE_ENABLE_SIGNUP=true
SUPABASE_ENABLE_ANONYMOUS=false
```

### Docker Compose Setup

The system uses `docker-compose.scada.yml` which includes:

- PostgreSQL database (Supabase-compatible)
- Supabase Auth service (GoTrue)
- Kong API Gateway
- FastAPI backend
- Frontend application

## API Endpoints

### Authentication Endpoints

- `GET /api/v1/auth/me` - Get current user info from Supabase
- `GET /api/v1/auth/me/local` - Get current user info from local database
- `POST /api/v1/auth/verify` - Verify JWT token
- `POST /api/v1/auth/signup` - Create new user in Supabase
- `PUT /api/v1/auth/profile` - Update user profile
- `DELETE /api/v1/auth/account` - Delete user account

### Usage Examples

#### 1. User Registration

```bash
curl -X POST "http://localhost:8080/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user123",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

#### 2. Get Current User

```bash
curl -X GET "http://localhost:8080/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Update Profile

```bash
curl -X PUT "http://localhost:8080/api/v1/auth/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "email": "john.smith@example.com"
  }'
```

## Database Schema

### User Table

The local user table includes:

- `id` - Primary key
- `supabase_id` - Supabase user ID (unique)
- `email` - User email
- `username` - Unique username
- `full_name` - User's full name
- `hashed_password` - Null for Supabase users
- `is_active` - Account status
- `is_superuser` - Admin privileges
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Authentication Flow

1. **User Registration**: User signs up through Supabase Auth
2. **Token Verification**: FastAPI verifies JWT tokens from Supabase
3. **Local Sync**: User data is automatically synced to local database
4. **API Access**: Protected endpoints use local user data

## Security Features

- JWT token verification using Supabase JWT secret
- Automatic user synchronization
- Role-based access control
- Secure password handling (managed by Supabase)

## Development

### Running the System

```bash
# Start all services
docker compose -f docker-compose.scada.yml up

# Run database migrations
alembic upgrade head

# Create superuser (if needed)
python scripts/create_superuser.py
```

### Testing Authentication

1. Start the system
2. Register a user via Supabase Auth
3. Get JWT token from Supabase
4. Use token to access protected endpoints

## Troubleshooting

### Common Issues

1. **JWT Verification Fails**
   - Check `SUPABASE_JWT_SECRET` matches Supabase configuration
   - Ensure token is not expired

2. **User Not Found**
   - Verify user exists in Supabase
   - Check local database synchronization

3. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check database credentials

### Logs

Check container logs for debugging:

```bash
docker compose -f docker-compose.scada.yml logs api
docker compose -f docker-compose.scada.yml logs auth
```

## Best Practices

1. **Environment Variables**: Never commit sensitive keys to version control
2. **Token Management**: Use short-lived tokens and refresh when needed
3. **Error Handling**: Implement proper error handling for auth failures
4. **Logging**: Log authentication events for security monitoring
5. **Testing**: Test authentication flows thoroughly

## Migration from Local Auth

If migrating from local authentication:

1. Run database migration to add `supabase_id` column
2. Update existing users with Supabase IDs
3. Test authentication flow
4. Remove old auth endpoints if no longer needed 