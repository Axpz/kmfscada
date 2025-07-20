import asyncio
from app.core.logging import get_logger
from app.mqtt.simulate_producer import sensor_producer
from app.mqtt.processor import mqtt_processor

logger = get_logger(__name__)

class BackgroundTaskManager:
    def __init__(self):
        self.tasks = []
        self.running = False
    
    async def sensor_data_generator_task(self):
        """this is a test 传感器数据生成后台任务 - 每60秒执行一次"""
        logger.info("Starting test sensor data generator task (60s interval)")
        
        while sensor_producer.running:
            try:
                # 异步生成所有传感器数据（包含WebSocket广播）
                await sensor_producer.generate_all_sensors_async()
                
                # 等待60秒
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in sensor data generator task: {e}")
                await asyncio.sleep(60)  # 出错后也等待60秒再重试
    
    async def start_background_tasks(self):
        """启动所有后台任务"""
        if self.running:
            logger.warning("Background tasks already running")
            return
        
        self.running = True
        
        # 启动MQTT多进程处理系统
        try:
            mqtt_processor.start()
            logger.info("MQTT multiprocess system started")
        except Exception as e:
            logger.error(f"Failed to start MQTT processor: {e}")
        
        # 启动传感器数据生成器
        sensor_producer.start()
        
        # 创建并启动传感器数据生成任务
        task = asyncio.create_task(self.sensor_data_generator_task())
        self.tasks.append(task)
        
        logger.info("Background tasks started")
    
    async def stop_background_tasks(self):
        """停止所有后台任务"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止传感器数据生成器
        sensor_producer.stop()
        
        # 取消所有异步任务
        for task in self.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.tasks.clear()
        
        # 停止MQTT多进程处理系统
        try:
            mqtt_processor.stop()
            logger.info("MQTT multiprocess system stopped")
        except Exception as e:
            logger.error(f"Error stopping MQTT processor: {e}")
        
        logger.info("Background tasks stopped")
    
    def get_status(self):
        """获取系统状态"""
        return {
            "background_tasks_running": self.running,
            "sensor_producer_running": sensor_producer.running,
            "active_tasks": len([t for t in self.tasks if not t.done()]),
            "mqtt_processor": mqtt_processor.get_status()
        }

# 全局任务管理器
task_manager = BackgroundTaskManager()