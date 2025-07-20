import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.sensor import SensorReading
from app.mqtt.publisher import publish_sensor_data
from app.mqtt.sensor_configs import SENSOR_CONFIGS, generate_sensor_value, get_sensor_status

logger = get_logger(__name__)

class SensorDataProducer:
    def __init__(self):
        self.running = False
    
    def generate_sensor_reading(self, sensor_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """生成单个传感器读数"""
        # 生成数值
        value = generate_sensor_value(sensor_id, config)
        
        # 获取状态
        status = get_sensor_status(value, config)
        
        # 创建传感器读数数据
        reading_data = {
            "sensor_id": sensor_id,
            "timestamp": datetime.now(timezone.utc),
            "value": value,
            "unit": config["unit"],
            "location": config["location"],
            "meta": {
                "sensor_type": config["type"],
                "status": status,
                "min_threshold": config["range"][0],
                "max_threshold": config["range"][1],
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        return reading_data
    
    def save_to_database(self, reading_data: Dict[str, Any]) -> bool:
        """保存到数据库"""
        try:
            db: Session = SessionLocal()
            
            # 创建SensorReading对象
            sensor_reading = SensorReading(
                sensor_id=reading_data["sensor_id"],
                timestamp=reading_data["timestamp"],
                value=reading_data["value"],
                unit=reading_data["unit"],
                location=reading_data["location"],
                meta=reading_data["meta"]
            )
            
            db.add(sensor_reading)
            db.commit()
            db.refresh(sensor_reading)
            
            logger.debug(f"Saved sensor reading to database: {reading_data['sensor_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save sensor reading to database: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def publish_to_mqtt(self, reading_data: Dict[str, Any]) -> bool:
        """发布到MQTT"""
        try:
            # 准备MQTT消息数据
            mqtt_data = {
                "sensor_id": reading_data["sensor_id"],
                "timestamp": reading_data["timestamp"].isoformat(),
                "value": reading_data["value"],
                "unit": reading_data["unit"],
                "location": reading_data["location"],
                "meta": reading_data["meta"]
            }
            
            # 发布到MQTT
            success = publish_sensor_data(mqtt_data)
            
            if not success:
                logger.error(f"Failed to publish sensor data to MQTT: {reading_data['sensor_id']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to publish sensor data to MQTT: {e}")
            return False
    
    async def broadcast_to_websocket(self, reading_data: Dict[str, Any]):
        """广播数据到WebSocket客户端"""
        try:
            from app.websocket.broadcaster import broadcast_sensor_data
            await broadcast_sensor_data(reading_data)
            logger.debug(f"Broadcasted sensor data to WebSocket: {reading_data['sensor_id']}")
        except Exception as e:
            logger.error(f"Failed to broadcast to WebSocket: {e}")
    
    async def generate_all_sensors_async(self) -> List[Dict[str, Any]]:
        """异步生成所有传感器的数据"""
        readings = []
        
        for sensor_id, config in SENSOR_CONFIGS.items():
            try:
                reading_data = self.generate_sensor_reading(sensor_id, config)
                readings.append(reading_data)
                
                # 保存到数据库
                # self.save_to_database(reading_data)
                
                # 发布到MQTT
                self.publish_to_mqtt(reading_data)
                
                # 广播到WebSocket
                # await self.broadcast_to_websocket(reading_data)
                
            except Exception as e:
                logger.error(f"Failed to generate data for sensor {sensor_id}: {e}")
        
        logger.info(f"Generated {len(readings)} sensor readings")
        return readings
    
    def generate_all_sensors(self) -> List[Dict[str, Any]]:
        """生成所有传感器的数据（同步版本，用于兼容）"""
        readings = []
        
        for sensor_id, config in SENSOR_CONFIGS.items():
            try:
                reading_data = self.generate_sensor_reading(sensor_id, config)
                readings.append(reading_data)
                
                # 保存到数据库
                self.save_to_database(reading_data)
                
                # 发布到MQTT
                self.publish_to_mqtt(reading_data)
                
                # 尝试异步广播到WebSocket（如果在事件循环中）
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.broadcast_to_websocket(reading_data))
                except RuntimeError:
                    # 没有事件循环，跳过WebSocket广播
                    pass
                
            except Exception as e:
                logger.error(f"Failed to generate data for sensor {sensor_id}: {e}")
        
        logger.info(f"Generated {len(readings)} sensor readings")
        return readings
    
    def start(self):
        """启动数据生产"""
        self.running = True
        logger.info("Sensor data producer started")
    
    def stop(self):
        """停止数据生产"""
        self.running = False
        logger.info("Sensor data producer stopped")

# 全局生产者实例
sensor_producer = SensorDataProducer()