import os
import time
import multiprocessing
from multiprocessing import Process, Queue, Event
import threading
from typing import List
from app.core.config import settings
from app.core.logging import get_logger
from app.mqtt.worker import worker_process
from app.mqtt.client import mqtt_client
from app.mqtt.sensor_configs import generate_multiple_sensor_data_records
from app.websocket.manager import websocket_manager

logger = get_logger("mqtt.manager")

class MQTTManager:
    """MQTT系统管理器，负责协调MQTT客户端、Worker进程和WebSocket广播"""
    
    def __init__(self):
        self.workers: List[Process] = []
        self.task_queue = Queue(maxsize=settings.MQTT_QUEUE_SIZE)
        self.websocket_queue = websocket_manager.broadcast_queue
        self.stop_event = Event()
        self.running = False
    
    def start_worker_pool(self):
        """启动Worker进程池"""
        print(f"🚀 启动 {settings.MQTT_WORKER_PROCESSES} 个Worker进程")
        logger.info(f"Starting {settings.MQTT_WORKER_PROCESSES} worker processes")
        
        self.workers = []
        for i in range(settings.MQTT_WORKER_PROCESSES):
            worker = Process(target=worker_process, args=(self.task_queue, self.websocket_queue, self.stop_event))
            worker.start()
            self.workers.append(worker)
            logger.info(f"Started worker process {i} with pid {worker.pid}")
        
        return self.workers
    
    def stop_worker_pool(self):
        """停止Worker进程池"""
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
    
    def start_system(self):
        """启动MQTT多进程处理系统"""
        if self.running:
            logger.warning("MQTT manager already running")
            return
        
        print("🎯 启动MQTT多进程处理系统")
        logger.info("Starting MQTT multiprocess system")
        
        try:
            # 启动Worker进程池
            self.start_worker_pool()
            
            # 设置MQTT客户端的任务队列
            mqtt_client.set_task_queue(self.task_queue)
            
            # 连接MQTT客户端
            mqtt_thread = threading.Thread(target=mqtt_client.run, daemon=True)
            mqtt_thread.start()

            self.running = True

            logger.info("MQTT multiprocess system started successfully (waiting for connection)")
                
        except KeyboardInterrupt:
            logger.info("用户手动中断，退出程序。")
            mqtt_client.disconnect()
            self.stop_worker_pool()

        except Exception as e:
            logger.error(f"Failed to start MQTT manager: {e}")
            mqtt_client.disconnect()
            self.stop_worker_pool()
            raise
    
    def stop_system(self):
        """停止MQTT多进程处理系统"""
        if not self.running:
            return
        
        print("🔚 停止MQTT多进程处理系统")
        logger.info("Stopping MQTT multiprocess system")
        
        try:
            # 断开MQTT连接
            mqtt_client.disconnect()
            
            # 停止Worker进程池
            self.stop_worker_pool()
            
            # Clean up WebSocket manager queue
            from app.websocket.manager import websocket_manager
            websocket_manager.cleanup_queue()
            
            self.running = False
            print("✅ MQTT多进程处理系统已停止")
            logger.info("MQTT multiprocess system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping MQTT manager: {e}")

# 全局MQTT管理器实例
mqtt_manager = MQTTManager()