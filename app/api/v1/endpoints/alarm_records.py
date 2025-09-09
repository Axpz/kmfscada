from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.services.alarm_record_service import AlarmRecordService
from app.schemas.alarm_record import (
    AlarmRecordCreate, 
    AlarmRecordAcknowledge, 
    AlarmRecordFilter,
    AlarmRecordResponse,
    AlarmRecordListResponse
)

router = APIRouter()


@router.post("/", response_model=AlarmRecordResponse)
def create_alarm_record(
    *,
    db: Session = Depends(deps.get_db),
    alarm_record: AlarmRecordCreate,
) -> Any:
    """
    创建报警记录
    """
    service = AlarmRecordService(db)
    record = service.create_alarm_record(alarm_record)
    return record


@router.put("/{alarm_record_id}/ack", response_model=AlarmRecordResponse)
def acknowledge_alarm_record(
    *,
    db: Session = Depends(deps.get_db),
    alarm_record_id: int,
    acknowledge_data: AlarmRecordAcknowledge,
) -> Any:
    """
    确认报警记录
    """
    service = AlarmRecordService(db)
    record = service.acknowledge_alarm(alarm_record_id, acknowledge_data.acknowledged_by)
    
    if not record:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    return record


@router.put("/ack-all", response_model=int)
def acknowledge_alarm_record(
    *,
    db: Session = Depends(deps.get_db),
    acknowledge_data: AlarmRecordAcknowledge,
) -> Any:
    """
    确认报警记录
    """
    service = AlarmRecordService(db)
    affected = service.acknowledge_all(None)
    
    if affected is None:
        raise HTTPException(status_code=500, detail="确认报警记录失败")
    
    return affected


@router.post("/list", response_model=AlarmRecordListResponse)
def list_alarm_records(
    *,
    db: Session = Depends(deps.get_db),
    filters: AlarmRecordFilter,
) -> Any:
    service = AlarmRecordService(db)
    records, total = service.list_alarm_records(filters)
    
    return {
        "items": records,
        "total": total,
        "page": filters.page,
        "size": filters.size
    }


@router.get("/{alarm_record_id}", response_model=AlarmRecordResponse)
def get_alarm_record(
    *,
    db: Session = Depends(deps.get_db),
    alarm_record_id: int,
) -> Any:
    service = AlarmRecordService(db)
    record = service.get_alarm_record_by_id(alarm_record_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="报警记录不存在")
    
    return record
