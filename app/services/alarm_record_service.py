from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from app.models.alarm_record import AlarmRecord
from app.schemas.alarm_record import AlarmRecordCreate, AlarmRecordFilter
from app.core.logging import get_logger
from app.services.audit_log_service import AuditLogService

logger = get_logger(__name__)


class AlarmRecordService:
    """报警记录服务 - 处理报警记录的业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditLogService(db)
    
    def create_alarm_record(self, record_data: AlarmRecordCreate) -> AlarmRecord:
        """创建报警记录"""
        try:
            # 检查是否已存在相同的报警记录（基于唯一性约束）
            existing_record = self.db.query(AlarmRecord).filter(
                and_(
                    AlarmRecord.timestamp == record_data.timestamp,
                    AlarmRecord.line_id == record_data.line_id,
                    AlarmRecord.parameter_name == record_data.parameter_name
                )
            ).first()
            
            if existing_record:
                logger.warning(
                    f"报警记录已存在: timestamp={record_data.timestamp}, "
                    f"line_id={record_data.line_id}, parameter_name={record_data.parameter_name}"
                )
                # 返回已存在的记录，而不是创建重复记录
                return existing_record
            
            # 创建新的报警记录
            record = AlarmRecord(**record_data.model_dump())
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"创建报警记录: {record.line_id}/{record.parameter_name} - {record.alarm_message}")
            return record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建报警记录失败: {e}")
            raise
    
    def acknowledge_alarm(self, record_id: int, user: str) -> Optional[AlarmRecord]:
        """确认报警记录"""
        try:
            record = self.db.query(AlarmRecord).filter(AlarmRecord.id == record_id).first()
            if not record:
                logger.warning(f"报警记录不存在: {record_id}")
                return None
            
            if record.is_acknowledged:
                logger.info(f"报警记录已确认: {record_id}")
                return record
            
            # 更新确认状态
            record.is_acknowledged = True
            record.acknowledged_at = datetime.now(timezone.utc)
            record.acknowledged_by = user
            
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"确认报警记录: {record_id} by {user}")
            self.audit.create_log_entry(
                email=user,
                action="acknowledge_alarm",
                detail=f"确认报警记录: {record_id}"
            )
            return record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"确认报警记录失败: {e}")
            raise

    def acknowledge_all(self, user: str) -> int:
        """确认报警记录"""
        try:
            update_value = {
                "is_acknowledged": True,
                "acknowledged_at": datetime.now(timezone.utc),
            }
            if user:
                update_value["acknowledged_by"] = user

            rows = self.db.query(AlarmRecord).filter(
                AlarmRecord.is_acknowledged == False
            ).update(update_value, synchronize_session=False)

            self.db.commit()
            return rows
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"确认报警记录失败: {e}")
            raise
    
    def list_alarm_records(self, filters: AlarmRecordFilter) -> Tuple[List[AlarmRecord], int]:
        """查询报警记录（支持复杂过滤和分页）"""
        try:
            query = self.db.query(AlarmRecord)
            
            # 应用过滤条件
            if filters.line_id:
                query = query.filter(AlarmRecord.line_id.contains(filters.line_id))
            
            if filters.parameter_name:
                query = query.filter(AlarmRecord.parameter_name.contains(filters.parameter_name))
            
            if filters.alarm_message:
                # 支持消息内容模糊搜索
                query = query.filter(AlarmRecord.alarm_message.contains(filters.alarm_message))
            
            if filters.is_acknowledged is not None:
                query = query.filter(AlarmRecord.is_acknowledged == filters.is_acknowledged)
            
            if filters.start_time:
                query = query.filter(AlarmRecord.timestamp >= filters.start_time)
            
            if filters.end_time:
                query = query.filter(AlarmRecord.timestamp <= filters.end_time)
            
            # 获取总数
            total = query.count()
            
            # 应用分页和排序
            skip = (filters.page - 1) * filters.size
            records = (
                query
                .order_by(desc(AlarmRecord.id))
                .offset(skip)
                .limit(filters.size)
                .all()
            )
            
            logger.debug(f"查询报警记录: 过滤条件={filters}, 总数={total}, 返回={len(records)}")
            return records, total
            
        except Exception as e:
            logger.error(f"查询报警记录失败: {e}")
            raise
    
    def get_alarm_record_by_id(self, record_id: int) -> Optional[AlarmRecord]:
        """根据ID获取报警记录"""
        return self.db.query(AlarmRecord).filter(AlarmRecord.id == record_id).first()
    
    def get_unacknowledged_count(self, line_id: Optional[str] = None) -> int:
        """获取未确认的报警数量"""
        try:
            query = self.db.query(AlarmRecord).filter(AlarmRecord.is_acknowledged == False)
            
            if line_id:
                query = query.filter(AlarmRecord.line_id == line_id)
            
            return query.count()
            
        except Exception as e:
            logger.error(f"获取未确认报警数量失败: {e}")
            raise
