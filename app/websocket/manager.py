import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from fastapi import WebSocket
from app.core.logging import get_logger
from multiprocessing import Queue
from app.core.config import settings
from app.websocket.types import WebSocketMessage

logger = get_logger(__name__)

class WebSocketManager:
    # 定义支持的业务消息类型
    MESSAGE_TYPES = {
        "production_data": "生产线数据更新",
        "system_status": "系统状态更新", 
        "msg": "业务消息",
        "heartbeat": "心跳消息"
    }
    
    def __init__(self):
        # 存储活跃的WebSocket连接
        self.active_connections: List[WebSocket] = []
        # 存储连接的订阅信息
        self.connection_subscriptions: Dict[WebSocket, List[str]] = {}
        # Initialize broadcast queue as instance variable
        self.broadcast_queue: Queue = Queue(maxsize=settings.MQTT_QUEUE_SIZE)

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_subscriptions[websocket] = []
        
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
        
        # 发送欢迎消息
        await self.send_message(
            "connection",
            data={
                "message": "Connected to SCADA WebSocket",
                "client_id": client_id or "anonymous"
            }, 
            websocket=websocket)
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.connection_subscriptions:
            del self.connection_subscriptions[websocket]
        
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_message(self, message_type: str, data: Any, websocket: WebSocket = None):
        """发送标准WebSocket消息"""
        ws_message = WebSocketMessage(
            type=message_type,
            timestamp=datetime.now(),
            data=data
        )
        
        if websocket:
            try:
                await websocket.send_text(ws_message.model_dump_json())
            except Exception as e:
                logger.error(f"Failed to send message to client: {e}")
                self.disconnect(websocket)
        else:
            await self.broadcast(ws_message)
    
    async def broadcast(self, ws_message: WebSocketMessage, channel: str = "all"):
        """广播WebSocket消息给所有连接的客户端"""
        if not self.active_connections:
            return

        message_str = ws_message.model_dump_json()
        disconnected_clients = []

        logger.info(f"Broadcasting message: {ws_message.type}")
        
        for connection in self.active_connections:
            try:
                if channel == 'all':
                    await connection.send_text(message_str)
                    continue

                # 检查客户端是否订阅了该频道
                subscriptions = self.connection_subscriptions.get(connection, [])
                if channel in subscriptions or not subscriptions:
                    await connection.send_text(message_str)

            except Exception as e:
                logger.error(f"Failed to send broadcast message: {e}")
                disconnected_clients.append(connection)
        
        # 清理断开的连接
        for client in disconnected_clients:
            self.disconnect(client)
        
        if disconnected_clients:
            logger.info(f"Cleaned up {len(disconnected_clients)} disconnected clients")
    
    async def subscribe_client(self, websocket: WebSocket, channels: List[str]):
        """为客户端订阅特定频道"""
        # 确保WebSocket在连接列表中
        if websocket in self.active_connections:
            self.connection_subscriptions[websocket] = channels
            logger.info(f"Client subscribed to channels: {channels}")
            
            # 发送订阅确认
            await self.send_message(
                "subscription",
                {"message": f"Subscribed to channels: {channels}"},
                websocket
            )
        else:
            logger.warning(f"WebSocket not found in active connections for subscription")
    
    async def handle_client_message(self, websocket: WebSocket, message: dict):
        """处理客户端发送的消息"""
        message_type = message.get("type")
        
        if message_type == "subscribe":
            # 处理订阅请求
            channels = message.get("channels", [])
            await self.subscribe_client(websocket, channels)
            
        elif message_type == "ping":
            # 处理心跳
            await self.send_message("heartbeat", {
                "pong": True,
                "client_timestamp": message.get("timestamp"),
                "server_timestamp": datetime.now().isoformat()
            }, websocket)
            
        elif message_type == "system_status":
            # 获取系统状态
            await self.send_message("system_status", {
                "status_response": self.get_status(),
                "request_type": "get_status"
            }, websocket)
            
        elif message_type == "production_data":
            await self.send_message("production_data", message, websocket)

        else:
            await self.send_message("msg", {
                "error": f"Unknown message type: {message_type}",
                "message_type": "error"
            }, websocket)

    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)
    
    def get_status(self) -> Dict[str, Any]:
        """获取WebSocket管理器状态"""
        return {
            "active_connections": len(self.active_connections),
            "total_subscriptions": sum(len(subs) for subs in self.connection_subscriptions.values()),
            "connection_subscriptions": [f"{k}: {v}" for k, v in self.connection_subscriptions.items()] 
        }
    
    def initialize_queue(self):
        """Initialize the broadcast queue"""
        if self.broadcast_queue is None:
            self.broadcast_queue = Queue(maxsize=settings.MQTT_QUEUE_SIZE)
            logger.info("WebSocket broadcast queue initialized")
    
    def cleanup_queue(self):
        """Clean up the broadcast queue to prevent semaphore leaks"""
        try:
            if self.broadcast_queue is not None:
                # Clear any remaining items in the queue
                try:
                    while not self.broadcast_queue.empty():
                        self.broadcast_queue.get_nowait()
                except:
                    pass
                
                # Close and join the queue
                self.broadcast_queue.close()
                self.broadcast_queue.join_thread()
                logger.info("WebSocket broadcast queue cleaned up")
                self.broadcast_queue = None
                
        except Exception as e:
            logger.error(f"Error cleaning up WebSocket queue: {e}")

# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()