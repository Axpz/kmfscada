from fastapi import APIRouter
from app.api.v1.endpoints import users, production, auth, sensor, mqtt_status, websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users management"])
api_router.include_router(production.router, prefix="/production", tags=["production"])
api_router.include_router(sensor.router, prefix="/sensor", tags=["sensor"])
api_router.include_router(mqtt_status.router, prefix="/system", tags=["system status"])
api_router.include_router(websocket.router, prefix="", tags=["websocket"]) 