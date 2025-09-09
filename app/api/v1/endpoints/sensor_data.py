from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api import deps
from app.schemas.sensor_data import SensorDataFilter, SensorDataListResponse, UtilizationResponse, SensorDataExportFilter
from app.services.export_record_service import ExportRecordService
from app.services.sensor_data_service import SensorDataService
from datetime import datetime
import io
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/list", response_model=SensorDataListResponse)
def list_sensor_data(
    db: Session = Depends(deps.get_db),
    filters: SensorDataFilter = Body(...),
) -> Any:
    """
    Retrieve sensor data.
    """
    service = SensorDataService(db)
    return service.list_sensor_data(filters)

@router.post("/utilization", response_model=UtilizationResponse)
def get_utilization(
    db: Session = Depends(deps.get_db),
    filters: SensorDataFilter = Body(...),
) -> Any:
    """
    Get utilization data.
    """
    service = SensorDataService(db)
    return service.get_utilization(filters)

@router.post("/export")
def export_sensor_data(
    db: Session = Depends(deps.get_db),
    filters: SensorDataExportFilter = Body(...),
) -> Any:
    """
    流式导出传感器数据到Excel文件，适用于大数据量场景。
    使用临时文件避免内存溢出。
    """
    try:
        export_record_service = ExportRecordService(db)
        service = SensorDataService(db, export_record_service=export_record_service)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        start_time = filters.start_time.strftime("%Y%m%d%H%M%S")
        end_time = filters.end_time.strftime("%Y%m%d%H%M%S")
        # 清理文件名中的特殊字符
        clean_line_ids = str(filters.line_ids).replace(',', '_').replace(' ', '_').replace('-', '_')
        filename = f"sensor_data_export_{clean_line_ids}_{start_time}_{end_time}_{timestamp}.xlsx"
        
        logger.info("Starting streaming Excel export")
        
        # 使用流式导出
        return StreamingResponse(
            service.export_sensor_data_streaming(filters),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming export: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"流式导出失败: {str(e)}"
        )
