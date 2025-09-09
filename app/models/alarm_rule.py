from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Text,
    DateTime,
    Double,
    Boolean,
    Integer,
    UniqueConstraint,
    Index,
)

from app.db.base_class import Base


class AlarmRule(Base):
    """报警规则表 - 用于存放用户定义的报警规则"""

    __tablename__ = "alarm_rules"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 生产线ID
    line_id = Column(Text, nullable=False, index=True, comment="生产线ID")
    
    # 监控的参数名称
    parameter_name = Column(Text, nullable=False, comment="监控的参数名称")
    
    # 报警下限值
    lower_limit = Column(Double, nullable=True, comment="报警下限值")
    
    # 报警上限值
    upper_limit = Column(Double, nullable=True, comment="报警上限值")
    
    # 规则启用状态
    is_enabled = Column(Boolean, default=True, nullable=False, comment="规则启用状态")
    
    # 创建和更新时间
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 表约束
    __table_args__ = (
        # 确保同一生产线的同一参数只能有一条规则
        UniqueConstraint('line_id', 'parameter_name', name='uq_line_parameter'),
        # 为常用查询创建索引
        Index('idx_line_enabled', 'line_id', 'is_enabled'),
    )

    def __repr__(self):
        return f"<AlarmRule(id={self.id}, line_id='{self.line_id}', parameter_name='{self.parameter_name}')>"
