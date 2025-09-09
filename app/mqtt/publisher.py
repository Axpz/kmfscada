from .client import mqtt_client
from app.core.logging import get_logger
from typing import Dict, Any

logger = get_logger(__name__)

def publish_message(topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
    """发布MQTT消息的便捷函数"""
    return mqtt_client.publish(topic, payload, qos)

def publish_sensor_data(data: Dict[str, Any]) -> bool:
    """发布传感器数据"""
    topic = f"kmf/scada/sensors/data"
    return publish_message(topic, data)
