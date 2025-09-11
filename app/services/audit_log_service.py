from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogFilter
from app.core.logging import get_logger
from app.core.context import get_request
from app.utils.request import get_client_ip

logger = get_logger(__name__)


class AuditLogService:
    """审计日志服务 - 处理审计日志的业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_audit_log(self, log_data: AuditLogCreate) -> AuditLog:
        """创建审计日志"""
        try:
            # 创建新的审计日志
            log = AuditLog(**log_data.model_dump())
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            
            logger.info(f"创建审计日志: {log.email} - {log.action}")
            return log
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建审计日志失败: {e}")
            raise
    
    def create_log_entry(
        self,
        email: Optional[str] = None,
        action: str = "",
        detail: Optional[str] = None
    ) -> AuditLog:
        """便捷方法：创建审计日志条目"""
        log_data = AuditLogCreate(
            email=email,
            action=action,
            ip_address=get_client_ip(get_request()),
            user_agent=None,
            detail=detail
        )
        return self.create_audit_log(log_data)
    
    def list_audit_logs(self, filters: AuditLogFilter) -> Tuple[List[AuditLog], int]:
        """查询审计日志（支持复杂过滤和分页）"""
        try:
            query = self.db.query(AuditLog)
            
            # 应用过滤条件
            if filters.email:
                query = query.filter(AuditLog.email.contains(filters.email))
            
            if filters.action:
                query = query.filter(AuditLog.action.contains(filters.action))
            
            if filters.ip_address:
                query = query.filter(AuditLog.ip_address.contains(filters.ip_address))
            
            if filters.start_time:
                query = query.filter(AuditLog.created_at >= filters.start_time)
            
            if filters.end_time:
                query = query.filter(AuditLog.created_at <= filters.end_time)
            
            # 获取总数
            total = query.count()
            
            # 应用分页和排序
            skip = (filters.page - 1) * filters.size
            logs = (
                query
                .order_by(desc(AuditLog.id))
                .offset(skip)
                .limit(filters.size)
                .all()
            )
            
            logger.debug(f"查询审计日志: 过滤条件={filters}, 总数={total}, 返回={len(logs)}")
            return logs, total
            
        except Exception as e:
            logger.error(f"查询审计日志失败: {e}")
            raise

