import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from app.core.logging import get_logger
from app.websocket.manager import websocket_manager

router = APIRouter()
logger = get_logger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None, description="客户端ID"),
    channels: Optional[str] = Query(None, description="订阅频道，逗号分隔")
):
    """WebSocket连接端点"""
    logger.info(f"WebSocket connected: {client_id}")
    await websocket_manager.connect(websocket, client_id)
    
    # 处理频道订阅
    if channels:
        channel_list = [ch.strip() for ch in channels.split(",") if ch.strip()]
        await websocket_manager.subscribe_client(websocket, channel_list)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await websocket_manager.handle_client_message(websocket, message)
            except json.JSONDecodeError:
                await websocket_manager.send_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info(f"Client {client_id or 'anonymous'} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


@router.get("/ws/status")
async def get_websocket_status():
    """获取WebSocket连接状态"""
    return websocket_manager.get_status()