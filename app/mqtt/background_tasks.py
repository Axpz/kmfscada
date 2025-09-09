import asyncio
from app.core.logging import get_logger
from app.mqtt.manager import mqtt_manager

logger = get_logger(__name__)

class BackgroundTaskManager:
    def __init__(self):
        self.tasks = []
        self.running = False
    
    async def start_background_tasks(self):
        """启动所有后台任务"""
        if self.running:
            logger.warning("Background tasks already running")
            return 
        
        # 启动MQTT多进程处理系统
        try:
            mqtt_manager.start_system()
            logger.info("MQTT multiprocess system started")
        except Exception as e:
            logger.error(f"Failed to start MQTT manager: {e}")
        
        self.running = True
        logger.info("Background tasks started")
    
    async def stop_background_tasks(self):
        """停止所有后台任务"""
        if not self.running:
            return
        
        
        # 停止MQTT多进程处理系统
        try:
            mqtt_manager.stop_system()
            logger.info("MQTT multiprocess system stopped")
        except Exception as e:
            logger.error(f"Error stopping MQTT manager: {e}")
        
        self.running = False
        logger.info("Background tasks stopped")

# 全局任务管理器
task_manager = BackgroundTaskManager()