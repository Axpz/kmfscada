from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/scada"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-token-with-at-least-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY: int = 3600
    
    # Supabase
    SUPABASE_URL: str = "http://localhost:8080"
    SUPABASE_SERVICE_KEY: str = "your-service-role-key"
    SUPABASE_ANON_KEY: str = "your-anon-key"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SCADA System"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 