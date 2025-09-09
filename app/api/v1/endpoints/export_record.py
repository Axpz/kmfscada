from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.api.deps import get_db, get_current_active_user
from app.schemas.export_record import (
    ExportRecordCreate, 
    ExportRecordInDB, 
    ExportRecordFilter,
    ExportRecordListResponse
)
from app.services.export_record_service import ExportRecordService

router = APIRouter()


@router.post("/", response_model=ExportRecordInDB, status_code=status.HTTP_201_CREATED)
def create_export_record(
    export_data: ExportRecordCreate,
    db: Session = Depends(get_db),
    # current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """创建导出任务"""
    service = ExportRecordService(db)
    
    # 设置创建用户
    # export_data.created_by = current_user.username
    
    try:
        export_record = service.create_export_record(export_data)
        return export_record
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建导出任务失败: {str(e)}"
        )


@router.post("/list", response_model=ExportRecordListResponse)
def get_export_records(
    filters: ExportRecordFilter,
    db: Session = Depends(get_db),
    # current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """获取导出记录列表"""
    service = ExportRecordService(db)
    
    try:
        result = service.get_export_records(filters)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导出记录失败: {str(e)}"
        )

