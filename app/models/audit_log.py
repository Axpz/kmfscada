from sqlalchemy import Column, Integer, String, Text, DateTime, Index, Boolean
from sqlalchemy.sql import func
from app.db.base_class import Base


class AuditLog(Base):
    """审计日志模型 - 记录用户操作和系统事件"""
    
    __tablename__ = "audit_logs"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="审计日志ID")
    
    # 基本信息
    email = Column(String(128), nullable=True, index=True, comment="Email")
    action = Column(String(128), nullable=False, index=True, comment="操作类型")
    
    # 网络信息
    ip_address = Column(String(45), nullable=True, comment="IP地址（兼容IPv4和IPv6）")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    
    # 操作详情
    detail = Column(Text, nullable=True, comment="操作详情")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="记录创建时间")
    
    __table_args__ = (
        Index("idx_audit_user_time", "email", "created_at"),  # 用户操作时间查询
        Index("idx_audit_action_time", "action", "created_at"),  # 操作类型时间查询
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, email='{self.email}', action='{self.action}', created_at='{self.created_at}')>"