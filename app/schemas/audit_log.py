from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class AuditLogBase(BaseModel):
    """审计日志基础模型"""
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    action: str = Field(..., min_length=1, max_length=128, description="操作类型")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    detail: Optional[str] = Field(None, description="操作详情")


class AuditLogCreate(AuditLogBase):
    """创建审计日志请求模型"""
    pass


class AuditLogFilter(BaseModel):
    """审计日志查询过滤模型"""
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    action: Optional[str] = Field(None, description="操作类型")
    ip_address: Optional[str] = Field(None, description="IP地址")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(1, ge=1, description="页码，从1开始")
    size: int = Field(100, ge=1, le=1000, description="每页大小")


class AuditLogResponse(BaseModel):
    """审计日志响应模型"""
    id: int
    email: Optional[EmailStr] = None
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    detail: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """审计日志列表响应模型"""
    items: list[AuditLogResponse]
    total: int
    page: int
    size: int

