from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from app.models.export_record import ExportRecord
from app.schemas.export_record import ExportRecordCreate, ExportRecordFilter, ExportRecordListResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExportRecordService:
    """导出记录服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_export_record(self, export_data: ExportRecordCreate) -> ExportRecord:
        """创建导出记录"""
        try:
            db_export = ExportRecord(
                line_names=export_data.line_names,
                fields=export_data.fields,
                start_time=export_data.start_time,
                end_time=export_data.end_time,
                format=export_data.format,
                size=export_data.size,
                created_by=export_data.created_by,
                status='pending'
            )
            
            self.db.add(db_export)
            self.db.commit()
            self.db.refresh(db_export)
            logger.info(f"Created export record: ID {db_export.id}")
            return db_export
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error when creating export record: {str(e)}")
            raise
    
    def get_export_records(self, filters: ExportRecordFilter) -> ExportRecordListResponse:
        """获取导出记录列表"""
        try:
            query = self.db.query(ExportRecord)
            
            # 应用过滤条件
            if filters.status:
                query = query.filter(ExportRecord.status == filters.status)
            
            if filters.created_by:
                query = query.filter(ExportRecord.created_by == filters.created_by)
            
            if filters.format:
                query = query.filter(ExportRecord.format == filters.format)
            
            # 获取总数
            total = query.count()
            
            # 分页
            offset = (filters.page - 1) * filters.size
            items = query.order_by(ExportRecord.created_at.desc()).offset(offset).limit(filters.size).all()
            
            return ExportRecordListResponse(
                items=items,
                total=total,
                page=filters.page,
                size=filters.size
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error when getting export records: {str(e)}")
            raise
    
    def get_export_record_by_id(self, export_id: int) -> Optional[ExportRecord]:
        """根据ID获取导出记录"""
        try:
            return self.db.query(ExportRecord).filter(ExportRecord.id == export_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error when getting export record by ID {export_id}: {str(e)}")
            raise
    
    def update_export_record_status_and_size(self, export_id: int, status: str, size: int=None) -> Optional[ExportRecord]:
        """更新导出记录状态"""
        try:
            db_export = self.get_export_record_by_id(export_id)
            if not db_export:
                return None
            
            logger.info(f"Updating export record {export_id} status to {status} and size to {size}")
            db_export.status = status
            if size is not None:
                db_export.size = size
            self.db.commit()
            self.db.refresh(db_export)
            logger.info(f"Updated export record {export_id} status to {status}")
            return db_export
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error when updating export record {export_id}: {str(e)}")
            raise
