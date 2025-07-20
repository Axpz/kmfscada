import paho.mqtt.client as mqtt
from app.core.config import settings
from app.core.logging import get_logger
import json
from typing import Optional
from multiprocessing import Queue
import time

logger = get_logger(__name__)

class MQTTClient:
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.task_queue: Optional[Queue] = None

    def set_task_queue(self, task_queue: Queue):
        """设置任务队列"""
        self.task_queue = task_queue

    def init(self):
        self.connect()
        
    def connect(self):
        """连接到MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)
            
            # 设置回调函数
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # 设置用户名密码（如果有）
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
            
            # 连接到broker
            self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            self.client.loop_start()
            
            logger.info(f"Connecting to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
    
    def disconnect(self):
        """断开MQTT连接"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
    
    def publish(self, topic: str, payload: dict, qos: int = 1):
        """发布消息"""
        if not self.connected:
            logger.warning("MQTT not connected, cannot publish message")
            return False
            
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}: {message}")
                return True
            else:
                logger.error(f"Failed to publish to {topic}, error code: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False
    
    def subscribe(self, topic: str, qos: int = 1):
        """订阅主题"""
        while not self.connected:
            logger.warning("MQTT not connected, cannot subscribe")
            time.sleep(1)
            
        try:
            result = self.client.subscribe(topic, qos=qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Subscribed to topic: {topic}")
                return True
            else:
                logger.error(f"Failed to subscribe to {topic}, error code: {result[0]}")
                return False
        except Exception as e:
            logger.error(f"Error subscribing to topic: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.connected = True
            print("✅ 已连接 MQTT Broker")
            logger.info("Connected to MQTT broker successfully")
            
            # 自动订阅传感器数据主题
            client.subscribe("kmf/scada/sensors/+/data")
            client.subscribe("kmf/scada/sensors/data")  # 兼容不同格式
            logger.info("Auto-subscribed to sensor data topics")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.connected = False
        logger.warning("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """消息接收回调 - 将消息放入队列"""
        try:
            payload = msg.payload.decode()
            topic = msg.topic
            
            print(f"📥 收到 MQTT 消息: {payload}")
            logger.info(f"Received message from {topic}")
            
            # 将消息放入队列供Worker进程处理
            if self.task_queue:
                try:
                    self.task_queue.put_nowait(payload)
                    logger.debug("Message added to task queue")
                except Exception as e:
                    print("⚠️ 队列满了，消息被丢弃！")
                    logger.warning(f"Task queue full, message dropped: {e}")
            else:
                logger.warning("Task queue not set, message ignored")
            
        except Exception as e:
            logger.error(f"Error processing received message: {e}")

# 全局MQTT客户端实例
mqtt_client = MQTTClient()