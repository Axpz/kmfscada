from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AlarmRuleBase(BaseModel):
    """报警规则基础模型"""
    line_id: str
    parameter_name: str
    lower_limit: Optional[float] = None
    upper_limit: Optional[float] = None
    is_enabled: bool = True


class AlarmRuleCreate(AlarmRuleBase):
    """创建报警规则"""
    pass


class AlarmRuleUpdate(BaseModel):
    """更新报警规则"""
    line_id: Optional[str] = None
    parameter_name: Optional[str] = None
    lower_limit: Optional[float] = None
    upper_limit: Optional[float] = None
    is_enabled: Optional[bool] = None


class AlarmRule(AlarmRuleBase):
    """报警规则完整模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlarmRuleList(BaseModel):
    """报警规则列表响应"""
    items: list[AlarmRule]
    total: int
    page: int
    size: int
