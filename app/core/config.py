from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/scada"
    
    # Supabase Configuration
    SUPABASE_URL: str = "http://localhost:8080"
    SUPABASE_SERVICE_KEY: str = "your-service-role-key"
    SUPABASE_ANON_KEY: str = "your-anon-key"
    SUPABASE_JWT_SECRET: str = "your-super-secret-jwt-token-with-at-least-32-characters-long"
    
    # Supabase Auth Settings
    SUPABASE_AUTH_ENABLED: bool = True
    SUPABASE_AUTO_CONFIRM: bool = True
    SUPABASE_ENABLE_SIGNUP: bool = True
    SUPABASE_ENABLE_ANONYMOUS: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SCADA System"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-for-fastapi"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings() 