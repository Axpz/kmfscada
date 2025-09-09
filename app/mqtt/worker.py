import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List
import multiprocessing
from multiprocessing import Queue, Event
from queue import Empty
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dateutil import parser

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.config import settings
from app.models.sensor_data import SensorData
from app.core.logging import get_logger
from app.websocket.manager import WebSocketManager
from app.services.alarm_rule_service import AlarmRuleService
from app.services.alarm_record_service import AlarmRecordService
from app.services.sensor_data_service import SensorDataService
from app.mqtt.sensor_configs import generate_multiple_sensor_data_records
import random

logger = get_logger(__name__)

def create_worker_db_session():
    """为Worker进程创建独立的数据库会话"""
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def worker_process(task_queue: Queue, websocket_queue: Queue, stop_event: Event):
    """Worker进程主函数"""
    worker_id = os.getpid()
    logger.info(f"🚀 Worker进程 {worker_id} 启动")
    
    # 创建独立的数据库会话
    db = create_worker_db_session()
    alarm_rule_service = AlarmRuleService(db)
    alarm_record_service = AlarmRecordService(db)
    sensor_data_service = SensorDataService(db, alarm_rule_service, alarm_record_service)

    try:
        while not stop_event.is_set():
            try:
                # try:
                #     msg = task_queue.get(timeout=5)
                # except Empty:
                #     continue
                # except KeyboardInterrupt:
                #     logger.info(f"🔚 Worker进程 {worker_id} 收到键盘中断信号")
                #     break

                
                # 检查退出信号
                # if msg is None:
                #     logger.warning(f"🔚 Worker进程 {worker_id} 收到退出信号")
                #     break
                
                try:
                    # msg_data = json.loads(msg)
                    time.sleep(60)
                    msg_data = generate_multiple_sensor_data_records(count=2)[0]
                    
                    mutated_sensor_data = sensor_data_service.process_sensor_data(msg_data)

                    if websocket_queue is not None:
                        websocket_queue.put(mutated_sensor_data)
                except ValueError as e:
                    logger.error(f"⚠️ Worker {worker_id} 消息解析失败: {e}")
            except KeyboardInterrupt:
                logger.info(f"🔚 Worker进程 {worker_id} 收到键盘中断信号")
                break
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} 处理消息时出错: {e}")
    
    except KeyboardInterrupt:
        logger.info(f"🔚 Worker进程 {worker_id} 被键盘中断")
    finally:
        try:
            db.close()
        except:
            pass
        logger.info(f"🔚 Worker进程 {worker_id} 已停止")