from .client import mqtt_client
from app.core.logging import get_logger

logger = get_logger(__name__)

def subscribe_topic(topic: str, qos: int = 1) -> bool:
    """订阅MQTT主题的便捷函数"""
    return mqtt_client.subscribe(topic, qos)

def subscribe_all_sensors():
    """订阅所有传感器数据"""
    return subscribe_topic("kmf/scada/sensors/data")

def subscribe_all_production():
    """订阅所有生产线状态"""
    return subscribe_topic("kmf/scada/production/+/status")

def subscribe_all_commands():
    """订阅所有设备控制命令"""
    return subscribe_topic("kmf/scada/commands/+")

def init_subscriptions():
    """初始化默认订阅"""
    logger.info("Initializing MQTT subscriptions")
    
    # 订阅传感器数据
    subscribe_all_sensors()
    
    # 订阅生产线状态
    subscribe_all_production()
    
    # 订阅控制命令
    subscribe_all_commands()
    
    logger.info("MQTT subscriptions initialized")