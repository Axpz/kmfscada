import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Empty
from app.websocket.manager import websocket_manager
from app.core.logging import get_logger

logger = get_logger(__name__)

executor = ThreadPoolExecutor(max_workers=1)

def blocking_get_message():
    """同步阻塞方法：用于线程池中"""
    try:
        return websocket_manager.broadcast_queue.get(timeout=5)
    except Empty:
        return None
    except Exception as e:
        logger.error(f"线程池读取队列失败: {e}")
        return None

async def websocket_broadcast_loop():
    """异步主循环：非阻塞地读取消息并广播"""
    while True:
        # 交给线程池去执行 blocking 的 get
        msg = await asyncio.get_event_loop().run_in_executor(executor, blocking_get_message)
        logger.info(f"Broadcasting ++++++++ message: {msg}")

        if msg is None:
            logger.info("Queue is empty")
            continue

        try:
            await websocket_manager.broadcast(message=msg, channel="all")
        except Exception as e:
            logger.error(f"WebSocket 广播失败: {e}")

