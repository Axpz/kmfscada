from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.services.audit_log_service import AuditLogService
from app.schemas.audit_log import (
    AuditLogFilter,
    AuditLogListResponse,
    AuditLogResponse,
    AuditLogCreate
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/list", response_model=AuditLogListResponse)
async def list_audit_logs(
    filters: AuditLogFilter,
    db: Session = Depends(deps.get_db),
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
) -> AuditLogListResponse:
    """
    查询审计日志列表 (管理员权限)
    使用POST方法支持复杂的过滤条件
    """
    try:
        logger.info(f"Admin {current_user.get('email')} querying audit logs with filters: {filters}")
        
        # 使用审计日志服务查询数据
        audit_service = AuditLogService(db)
        logs, total = audit_service.list_audit_logs(filters)
        
        # 转换为响应模型
        log_responses = [
            AuditLogResponse(
                id=log.id,
                email=log.email,
                action=log.action,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                detail=log.detail,
                created_at=log.created_at
            )
            for log in logs
        ]
        
        return AuditLogListResponse(
            items=log_responses,
            total=total,
            page=filters.page,
            size=filters.size
        )
        
    except Exception as e:
        logger.error(f"Failed to query audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query audit logs"
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AuditLogResponse)
async def create_audit_log(
    log_data: AuditLogCreate,
    db: Session = Depends(deps.get_db),
    current_user: Dict[str, Any] = Depends(deps.get_current_active_superuser)
) -> AuditLogResponse:
    """
    创建审计日志条目 (管理员权限)
    """
    try:
        logger.info(f"Admin {current_user.get('email')} creating audit log: {log_data.action}")
        
        # 使用审计日志服务创建日志
        audit_service = AuditLogService(db)
        log = audit_service.create_audit_log(log_data)
        
        return AuditLogResponse(
            id=log.id,
            email=log.email,
            action=log.action,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            detail=log.detail,
            created_at=log.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create audit log"
        )
