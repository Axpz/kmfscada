import os
import time
from multiprocessing import Process, Queue
from typing import List
from app.core.config import settings
from app.core.logging import get_logger
from app.mqtt.worker import worker_process
from app.mqtt.client import mqtt_client

from app.websocket.manager import WebSocketManager

logger = get_logger("mqtt.processor")

class MQTTProcessor:
    def __init__(self):
        self.workers: List[Process] = []
        self.task_queue: Queue = None
        self.websocket_queue: Queue = None
        self.running = False
    
    def start_workers(self):
        """启动Worker进程"""
        print(f"🚀 启动 {settings.MQTT_WORKER_PROCESSES} 个Worker进程")
        logger.info(f"Starting {settings.MQTT_WORKER_PROCESSES} worker processes")
        
        # Initialize task queue if not already done
        if self.task_queue is None:
            self.task_queue = Queue(maxsize=settings.MQTT_QUEUE_SIZE)
        
        # Use websocket manager's queue
        from app.websocket.manager import websocket_manager
        self.websocket_queue = websocket_manager.broadcast_queue
        
        self.workers = []
        for i in range(settings.MQTT_WORKER_PROCESSES):
            worker = Process(target=worker_process, args=(self.task_queue, self.websocket_queue))
            worker.start()
            self.workers.append(worker)
            logger.info(f"Started worker process {i} with pid {worker.pid}")
        
        return self.workers
    
    def stop_workers(self):
        """停止Worker进程"""
        print("🔚 停止Worker进程...")
        logger.info("Stopping worker processes")
        
        # 发送退出信号给所有Worker
        if self.task_queue is not None:
            for _ in self.workers:
                try:
                    self.task_queue.put(None, timeout=1)  # 发送退出信号
                except Exception as e:
                    logger.warning(f"Failed to send stop signal: {e}")
        
        # 等待所有Worker进程结束
        for worker in self.workers:
            try:
                worker.join(timeout=3)  # 减少等待时间到3秒
                if worker.is_alive():
                    logger.warning(f"Worker {worker.pid} still alive, sending SIGTERM")
                    worker.terminate()
                    worker.join(timeout=2)  # 再等待2秒
                    
                    if worker.is_alive():
                        logger.warning(f"Force killing worker {worker.pid}")
                        try:
                            import signal
                            os.kill(worker.pid, signal.SIGKILL)
                        except:
                            pass
                        worker.join()
                        
                logger.info(f"Worker process {worker.pid} stopped")
            except Exception as e:
                logger.error(f"Error stopping worker {worker.pid}: {e}")
        
        self.workers.clear()
        
        # Properly close and clean up queues
        self._cleanup_queues()
        
        print("✅ 所有Worker进程已停止")
    
    def _cleanup_queues(self):
        """Clean up multiprocessing queues to prevent semaphore leaks"""
        try:
            if self.task_queue is not None:
                # Clear any remaining items in the queue
                try:
                    while not self.task_queue.empty():
                        self.task_queue.get_nowait()
                except:
                    pass
                
                # Close and join the queue
                self.task_queue.close()
                self.task_queue.join_thread()
                logger.info("Task queue cleaned up")
                self.task_queue = None
            
            # Don't clean up websocket_queue here - it's managed by WebSocketManager
            # Just set reference to None
            self.websocket_queue = None
                
        except Exception as e:
            logger.error(f"Error cleaning up queues: {e}")
    
    def start(self):
        """启动MQTT多进程处理系统"""
        if self.running:
            logger.warning("MQTT processor already running")
            return
        
        print("🎯 启动MQTT多进程处理系统")
        logger.info("Starting MQTT multiprocess system")
        
        try:
            # Initialize WebSocket manager queue
            from app.websocket.manager import websocket_manager
            websocket_manager.initialize_queue()
            
            # 启动Worker进程
            self.start_workers()
            
            # 设置MQTT客户端的任务队列
            mqtt_client.set_task_queue(self.task_queue)
            
            # 连接MQTT客户端
            mqtt_client.connect()
            
            # 等待连接建立
            retry_count = 0
            while not mqtt_client.connected and retry_count < 10:
                time.sleep(1)
                retry_count += 1
            
            if mqtt_client.connected:
                self.running = True
                print("✅ MQTT多进程处理系统启动成功")
                logger.info("MQTT multiprocess system started successfully")
            else:
                print("❌ MQTT连接失败")
                logger.error("Failed to connect to MQTT broker")
                self.stop_workers()
                
        except Exception as e:
            logger.error(f"Failed to start MQTT processor: {e}")
            self.stop_workers()
            raise
    
    def stop(self):
        """停止MQTT多进程处理系统"""
        if not self.running:
            return
        
        print("🔚 停止MQTT多进程处理系统")
        logger.info("Stopping MQTT multiprocess system")
        
        try:
            # 断开MQTT连接
            mqtt_client.disconnect()
            
            # 停止Worker进程
            self.stop_workers()
            
            # Clean up WebSocket manager queue
            from app.websocket.manager import websocket_manager
            websocket_manager.cleanup_queue()
            
            self.running = False
            print("✅ MQTT多进程处理系统已停止")
            logger.info("MQTT multiprocess system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping MQTT processor: {e}")

    def get_status(self):
        """获取系统状态"""
        alive_workers = sum(1 for w in self.workers if w.is_alive())
        return {
            "running": self.running,
            "mqtt_connected": mqtt_client.connected,
            "total_workers": len(self.workers),
            "alive_workers": alive_workers,
            "queue_size": self.task_queue.qsize() if hasattr(self.task_queue, 'qsize') else 0
        }

# 全局MQTT处理器实例
mqtt_processor = MQTTProcessor()