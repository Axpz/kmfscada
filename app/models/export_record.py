from sqlalchemy import Column, Integer, String, Text, DateTime, Index, BIGINT
from sqlalchemy.sql import func
from app.db.base_class import Base


class ExportRecord(Base):
    """导出记录模型 - 记录数据导出任务的状态和配置"""
    
    __tablename__ = "export_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="导出记录ID")
    line_names = Column(Text, nullable=False, comment="导出的生产线名称（多个用逗号分隔）")
    fields = Column(Text, nullable=False, comment="导出的数据字段（多个用逗号分隔）")
    start_time = Column(DateTime(timezone=True), nullable=False, comment="导出的开始时间")
    end_time = Column(DateTime(timezone=True), nullable=False, comment="导出的结束时间")
    format = Column(String(10), nullable=False, default="xlsx", comment="文件格式")
    size = Column(BIGINT, nullable=True, comment="文件大小")
    status = Column(String(20), nullable=False, default="pending", index=True, comment="任务状态")
    created_by = Column(String(100), nullable=True, comment="创建用户")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    __table_args__ = (
        Index("idx_export_status", "status"),
    )
    
    def __repr__(self):
        return f"<ExportRecord(id={self.id}, status='{self.status}', format='{self.format}')>"