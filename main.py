import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import init_logging, get_logger
from app.middleware import LoggingMiddleware
from app.api.v1.api import api_router
from app.mqtt.background_tasks import task_manager
from app.websocket.broadcaster import websocket_broadcast_loop

# Import all models to register them with Base and get init_database function
from app.db.base import *

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger = get_logger(__name__)
    logger.info("Starting SCADA API application")
    
    # 初始化日志系统
    init_logging()
    logger.info("Logging system initialized")
    
    # 初始化数据库
    Base.metadata.create_all(bind=engine)
    if not db_init():
        logger.error("Database initialization failed")
        raise RuntimeError("Database initialization failed")
    
    # 启动后台任务（包含MQTT多进程系统和传感器数据生成）
    await task_manager.start_background_tasks()
    logger.info("Background tasks started")
    
    # 启动WebSocket广播监听器
    asyncio.create_task(websocket_broadcast_loop())
    logger.info("WebSocket broadcast listener started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SCADA API application")
    await task_manager.stop_background_tasks()

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


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "SCADA System API with FastAPI",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
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