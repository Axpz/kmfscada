import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List
from multiprocessing import Queue
from queue import Empty
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.config import settings
from app.models.sensor import SensorReading
from app.core.logging import get_logger
from app.websocket.manager import WebSocketManager

logger = get_logger(__name__)

# 全局WebSocket广播队列（用于进程间通信）
websocket_broadcast_queue = None

def create_worker_db_session():
    """为Worker进程创建独立的数据库会话"""
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def parse_mqtt_message(payload: Any) -> Dict[str, Any]:
    """解析MQTT消息"""
    try:
        data = payload.copy()
        
        # 确保必要字段存在
        required_fields = ['sensor_id', 'value']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # 处理时间戳
        if 'timestamp' in data:
            if isinstance(data['timestamp'], str):
                # 尝试解析ISO格式时间戳
                try:
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    data['timestamp'] = datetime.now(timezone.utc)
            elif not isinstance(data['timestamp'], datetime):
                data['timestamp'] = datetime.now(timezone.utc)
        else:
            data['timestamp'] = datetime.now(timezone.utc)
        
        # 确保时间戳有时区信息
        if data['timestamp'].tzinfo is None:
            data['timestamp'] = data['timestamp'].replace(tzinfo=timezone.utc)
        
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing message: {e}")

def save_sensor_readings_batch(db: Session, readings: List[Dict[str, Any]]) -> int:
    """批量保存传感器读数到数据库"""
    saved_count = 0
    
    try:
        sensor_objects = []
        
        for reading_data in readings:
            sensor_reading = SensorReading(
                sensor_id=reading_data['sensor_id'],
                timestamp=reading_data['timestamp'],
                value=float(reading_data['value']),
                unit=reading_data.get('unit'),
                location=reading_data.get('location'),
                meta=reading_data.get('meta', {})
            )
            sensor_objects.append(sensor_reading)
        
        # 批量插入
        db.add_all(sensor_objects)
        db.commit()
        saved_count = len(sensor_objects)
        
        logger.info(f"✅ Worker进程保存了 {saved_count} 条传感器数据")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 批量保存数据失败: {e}")
        
        # 尝试逐个保存
        for reading_data in readings:
            try:
                sensor_reading = SensorReading(
                    sensor_id=reading_data['sensor_id'],
                    timestamp=reading_data['timestamp'],
                    value=float(reading_data['value']),
                    unit=reading_data.get('unit'),
                    location=reading_data.get('location'),
                    meta=reading_data.get('meta', {})
                )
                db.add(sensor_reading)
                db.commit()
                saved_count += 1
                
            except Exception as individual_error:
                db.rollback()
                logger.error(f"❌ 保存单条数据失败 {reading_data.get('sensor_id', 'unknown')}: {individual_error}")
    
    return saved_count

def dispatch(q: Queue, data: Dict[str, Any], raw: Dict[str, Any]):
    try:
        raw["created_at"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        logger.error(f"❌ 处理消息时出------------错: {e}")
        logger.error(f"-----{data}, -----{raw}-----")
        return
    q.put(raw)

def worker_process(task_queue: Queue, websocket_queue: Queue):
    """Worker进程主函数"""
    worker_id = os.getpid()
    logger.info(f"🚀 Worker进程 {worker_id} 启动")
    
    # 创建独立的数据库会话
    db = create_worker_db_session()
    
    try:
        while True:
            try:
                try:
                    msg = task_queue.get(timeout=5)
                except Empty:
                    continue
                
                # 检查退出信号
                if msg is None:
                    logger.warning(f"🔚 Worker进程 {worker_id} 收到退出信号")
                    break
                
                try:
                    raw = json.loads(msg)
                    parsed = parse_mqtt_message(raw)
                    save_sensor_readings_batch(db, [parsed])
                    dispatch(websocket_queue, parsed.copy(), raw)
                except ValueError as e:
                    logger.error(f"⚠️ Worker {worker_id} 消息解析失败: {e}")
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} 处理消息时出错: {e}")
    
    finally:
        db.close()
        logger.info(f"🔚 Worker进程 {worker_id} 已停止")