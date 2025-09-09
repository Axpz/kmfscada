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
        if websocket_manager.broadcast_queue is None:
            return None
        return websocket_manager.broadcast_queue.get(timeout=5)
    except Empty:
        return None
    except Exception as e:
        logger.error(f"线程池读取队列失败: {e}")
        return None

async def websocket_broadcast_loop():
    """异步主循环：非阻塞地读取消息并广播"""
    try:
        while True:
            # 交给线程池去执行 blocking 的 get
            msg = await asyncio.get_event_loop().run_in_executor(executor, blocking_get_message)
            if msg is None:
                logger.info(f"Queue is empty: {msg}")
                await asyncio.sleep(2)
                continue

            logger.info(f"--------------------------------: {msg}")

            try:
                await websocket_manager.send_message('production_data', msg)
            except Exception as e:
                logger.error(f"WebSocket 广播失败: {e}")
    except asyncio.CancelledError:
        logger.info("WebSocket broadcast loop cancelled")
        raise
    except Exception as e:
        logger.error(f"WebSocket broadcast loop error: {e}")
    finally:
        # Clean up executor when loop ends
        executor.shutdown(wait=True)
        logger.info("ThreadPoolExecutor shutdown completed")

async def broadcast_sensor_data(data):
    """Broadcast sensor data to WebSocket clients"""
    try:
        await websocket_manager.broadcast(message=data, channel="sensors")
    except Exception as e:
        logger.error(f"Failed to broadcast sensor data: {e}")

