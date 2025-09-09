import asyncio
import random
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.sensor import SensorData
from app.mqtt.publisher import publish_sensor_data
from app.mqtt.sensor_configs import SENSOR_CONFIGS, generate_sensor_data_for_db, generate_multiple_sensor_data_records

logger = get_logger(__name__)

class SensorDataProducer:
    def __init__(self):
        self.running = False
    
    def generate_sensor_reading(self, sensor_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """生成单个传感器读数"""
        # 使用新的数据库兼容的数据生成函数
        line_id = f"line_{random.randint(1, 3):03d}"
        component_id = random.choice(["extruder", "cooler", "winder", "cutter"])
        
        sensor_data = generate_sensor_data_for_db(line_id, component_id)
        logger.info(f'Generated sensor data for {line_id}/{component_id}')
        return sensor_data
    
    def save_to_database(self, reading_data: Dict[str, Any]) -> bool:
        """保存到数据库"""
        try:
            db: Session = SessionLocal()
            
            # 创建SensorData对象，使用新的数据结构
            sensor_data = SensorData(**reading_data)
            
            db.add(sensor_data)
            db.commit()
            db.refresh(sensor_data)
            
            logger.info(f"Saved sensor data to database: {reading_data['line_id']}/{reading_data['component_id']} at {reading_data['timestamp']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save sensor data to database: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def publish_to_mqtt(self, sensor_data: Dict[str, Any]) -> bool:
        """发布到MQTT"""
        try:
            # 准备MQTT消息数据
            # mqtt_data = {
            #     "sensor_id": reading_data["sensor_id"],
            #     "timestamp": reading_data["timestamp"].isoformat(),
            #     "value": reading_data["value"],
            #     "unit": reading_data["unit"],
            #     "location": reading_data["location"],
            #     "meta": reading_data["meta"]
            # }
            mqtt_data = sensor_data
            logger.info(f"Publishing sensor data to MQTT: {mqtt_data}")
            # 发布到MQTT
            success = publish_sensor_data(mqtt_data)
            
            if not success:
                logger.error(f"Failed to publish sensor data to MQTT: {sensor_data['sensor_id']}")
            
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
    
    def generate_batch_sensor_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """生成批量传感器数据"""
        try:
            # 使用新的批量生成函数
            records = generate_multiple_sensor_data_records(count=count)
            
            # 批量保存到数据库
            saved_count = 0
            for record in records:
                if self.save_to_database(record):
                    saved_count += 1
                # 发布到MQTT
                self.publish_to_mqtt(record)
            
            logger.info(f"Generated and saved {saved_count}/{count} sensor data records")
            return records
            
        except Exception as e:
            logger.error(f"Failed to generate batch sensor data: {e}")
            return []
    
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