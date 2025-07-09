# Quick Start Guide - Supabase Auth Integration

This guide will help you quickly set up and run the SCADA system with optimized Supabase authentication.

## 🚀 Quick Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Make (optional, but recommended)

### 1. Environment Setup

```bash
# Navigate to the project directory
cd kmfscada

# Copy environment file
cp env.example .env

# Edit environment variables (optional)
# nano .env
```

### 2. Start Supabase Services

```bash
# Start all services (database, auth, API gateway, frontend)
make supabase-up

# Or manually:
docker-compose -f docker-compose.scada.yml up -d
```

### 3. Run Database Migrations

```bash
# Apply database migrations
make db-upgrade

# Or manually:
alembic upgrade head
```

### 4. Verify Services

Check if all services are running:

```bash
# View logs
make supabase-logs

# Check specific service logs
docker-compose -f docker-compose.scada.yml logs api
docker-compose -f docker-compose.scada.yml logs auth
```

### 5. Test Authentication

```bash
# Run comprehensive authentication tests
make test-supabase
```

## 🔗 Service URLs

Once started, you can access:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **FastAPI Backend**: http://localhost:8000
- **Supabase Auth**: http://localhost:9999
- **Health Check**: http://localhost:8080/health

## 📋 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/auth/me` | Get current user info from Supabase |
| `GET` | `/api/v1/auth/me/local` | Get current user info from local database |
| `POST` | `/api/v1/auth/signup` | Register new user |
| `POST` | `/api/v1/auth/signin` | Sign in user |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `POST` | `/api/v1/auth/signout` | Sign out user |
| `POST` | `/api/v1/auth/verify` | Verify JWT token |
| `PUT` | `/api/v1/auth/profile` | Update user profile |
| `DELETE` | `/api/v1/auth/account` | Delete user account |
| `GET` | `/api/v1/auth/users` | List users (admin only) |

### Example Usage

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

#### 2. User Sign In

```bash
curl -X POST "http://localhost:8080/api/v1/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

#### 3. Get Current User

```bash
curl -X GET "http://localhost:8080/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 4. Update Profile

```bash
curl -X PUT "http://localhost:8080/api/v1/auth/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "email": "john.smith@example.com"
  }'
```

## 🏗️ Architecture

### Service Components

1. **PostgreSQL Database** - Supabase-compatible database
2. **Supabase Auth (GoTrue)** - Authentication service
3. **Kong API Gateway** - Route management and security
4. **FastAPI Backend** - Business logic and API endpoints
5. **Frontend** - User interface (optional)

### Authentication Flow

```
User → Frontend → Kong → FastAPI → Supabase Auth → Database
```

## 🔧 Development

### Running in Development Mode

```bash
# Start only the backend in development mode
make dev

# Or manually:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Operations

```bash
# Create new migration
make db-migrate message="Add new table"

# Apply migrations
make db-upgrade

# Rollback migration
make db-downgrade
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Test Supabase integration
make test-supabase
```

## 🔒 Security Features

### JWT Token Management

- **Access Token**: Short-lived (1 hour by default)
- **Refresh Token**: Long-lived with rotation
- **Token Verification**: Server-side validation
- **Secure Storage**: Client-side secure storage

### Rate Limiting

- **Email Sent**: 30 requests per hour
- **SMS Sent**: 5 requests per hour
- **API Calls**: Configurable per endpoint

### Security Best Practices

1. **Environment Variables**: Never commit sensitive keys
2. **Token Rotation**: Automatic refresh token rotation
3. **CORS Configuration**: Proper cross-origin settings
4. **Input Validation**: Server-side validation
5. **Error Handling**: Secure error messages

## 🐛 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check if ports are in use
   docker ps
   
   # Restart services
   make supabase-down
   make supabase-up
   ```

2. **Database connection issues**
   ```bash
   # Check database logs
   docker-compose -f docker-compose.scada.yml logs db
   
   # Reset database
   make supabase-down
   docker volume rm scada-minimal_scada_db_data
   make supabase-up
   ```

3. **Authentication issues**
   ```bash
   # Check auth service logs
   docker-compose -f docker-compose.scada.yml logs auth
   
   # Verify environment variables
   cat .env
   ```

4. **JWT token issues**
   ```bash
   # Check JWT secret configuration
   echo $JWT_SECRET
   
   # Verify token format
   curl -X POST "http://localhost:8080/api/v1/auth/verify" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Useful Commands

```bash
# View all logs
make supabase-logs

# Stop all services
make supabase-down

# Restart services
make supabase-down && make supabase-up

# Clean up everything
make supabase-down
docker system prune -f

# Check service health
curl http://localhost:8080/health
```

## 📊 Monitoring

### Health Checks

- **Database**: `pg_isready`
- **Auth Service**: HTTP health endpoint
- **API Gateway**: Kong health check
- **Backend**: FastAPI health endpoint

### Logging

- **Application Logs**: Structured logging with levels
- **Access Logs**: Request/response logging
- **Error Logs**: Detailed error tracking
- **Security Logs**: Authentication events

## 🚀 Production Deployment

### Environment Configuration

```bash
# Production environment variables
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Security settings
JWT_SECRET=your-production-jwt-secret
SUPABASE_JWT_SECRET=your-production-supabase-jwt-secret

# Database settings
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Security Checklist

- [ ] Strong JWT secrets
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation
- [ ] Error handling
- [ ] Logging configured
- [ ] Monitoring setup

## 📚 Documentation

- [Supabase Integration Guide](docs/SUPABASE_INTEGRATION.md)
- [API Documentation](http://localhost:8000/docs)
- [Environment Configuration](env.example)
- [Database Schema](alembic/versions/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 