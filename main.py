from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import init_logging, get_logger
from app.middleware import LoggingMiddleware
from app.api.v1.api import api_router

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger = get_logger("startup")
    logger.info("Starting SCADA API application")
    
    # 初始化日志系统
    init_logging()
    logger.info("Logging system initialized")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SCADA API application")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SCADA System API with FastAPI",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scada-api"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG
    ) 