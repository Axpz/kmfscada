from fastapi import APIRouter
from app.mqtt.background_tasks import task_manager

router = APIRouter()

@router.get("/status")
async def get_mqtt_status():
    """获取MQTT系统状态"""
    return task_manager.get_status()

@router.get("/health")
async def mqtt_health_check():
    """MQTT系统健康检查"""
    status = task_manager.get_status()
    
    is_healthy = (
        status["background_tasks_running"] and
        status["mqtt_manager"]["running"] and
        status["mqtt_manager"]["mqtt_connected"] and
        status["mqtt_manager"]["alive_workers"] > 0
    )
    
    return {
        "healthy": is_healthy,
        "status": status
    }