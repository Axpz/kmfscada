from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, sensor_data, websocket, alarm_rules, alarm_records, production_lines, export_record, audit_log
from app.api.v1.endpoints import mqtt

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users management"])
api_router.include_router(production_lines.router, prefix="/production-lines", tags=["production lines"])
api_router.include_router(sensor_data.router, prefix="/sensor-data", tags=["sensor data"])
api_router.include_router(alarm_rules.router, prefix="/alarm-rules", tags=["alarm rules"])
api_router.include_router(alarm_records.router, prefix="/alarm-records", tags=["alarm records"])
api_router.include_router(export_record.router, prefix="/export-records", tags=["export records"])
api_router.include_router(audit_log.router, prefix="/audit-logs", tags=["audit logs"])
api_router.include_router(mqtt.router, prefix="/mqtt", tags=["mqtt"])
api_router.include_router(websocket.router, prefix="", tags=["websocket"]) 