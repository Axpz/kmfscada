from sqlalchemy import (
    Column, BIGINT, Integer, String, Text, Boolean, DateTime, Double,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.sql import func
from app.db.base_class import Base


class AlarmRecord(Base):
    """报警记录模型 - 记录已发生的报警事件"""
    
    __tablename__ = "alarm_records"
    
    # 主键（代理键，推荐做法）
    id = Column(BIGINT, primary_key=True, index=True, autoincrement=True)
    
    # 报警基本信息
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="报警发生时间")
    line_id = Column(String(50), nullable=False, index=True, comment="生产线ID")
    parameter_name = Column(String(100), nullable=False, index=True, comment="监控参数名称")
    parameter_value = Column(Double, nullable=False, comment="触发报警的参数值")
    alarm_message = Column(Text, nullable=False, comment="报警消息")
    
    # 确认状态
    is_acknowledged = Column(Boolean, default=False, index=True, comment="是否已确认")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="确认时间")
    acknowledged_by = Column(String(100), nullable=True, comment="确认人")
    
    # 关联关系（外键约束，删除规则为置空）
    alarm_rule_id = Column(
        Integer,
        ForeignKey("alarm_rules.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联的报警规则ID"
    )
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    __table_args__ = (
        # 确保同一时间戳在同一生产线的同一参数上只能有一条报警记录
        UniqueConstraint("timestamp", "line_id", "parameter_name", name="uq_alarm_timestamp_line_param"),
        Index("idx_alarm_line_time", "line_id", "timestamp"),  # 查询优化
        Index("idx_alarm_acknowledged", "is_acknowledged"),  # 确认状态索引，用于快速筛选已确认/未确认的报警
    )
    
    def __repr__(self):
        return f"<AlarmRecord(id={self.id}, line_id='{self.line_id}', parameter_name='{self.parameter_name}', timestamp='{self.timestamp}')>"
