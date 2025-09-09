from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AlarmRecordBase(BaseModel):
    """报警记录基础模型"""
    timestamp: datetime = Field(..., description="报警发生时间（传感器数据时间戳，唯一切不变的值）")
    line_id: str = Field(..., description="生产线ID")
    parameter_name: str = Field(..., description="监控参数名称")
    parameter_value: float = Field(..., description="触发报警的参数值")  # 对应数据库 Double 类型
    alarm_message: str = Field(..., description="报警消息")
    alarm_rule_id: Optional[int] = Field(None, description="关联的报警规则ID")


class AlarmRecordCreate(AlarmRecordBase):
    """创建报警记录请求模型"""
    pass


class AlarmRecordAcknowledge(BaseModel):
    """确认报警记录请求模型"""
    acknowledged_by: str = Field(..., description="确认人")


class AlarmRecordFilter(BaseModel):
    """报警记录查询过滤模型"""
    line_id: Optional[str] = Field(None, description="生产线ID")
    parameter_name: Optional[str] = Field(None, description="监控参数名称")
    alarm_message: Optional[str] = Field(None, description="报警消息内容")
    is_acknowledged: Optional[bool] = Field(None, description="是否已确认")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(1, ge=1, description="页码，从1开始")
    size: int = Field(100, ge=1, le=1000, description="每页大小")


class AlarmRecordResponse(BaseModel):
    """报警记录响应模型"""
    id: int
    timestamp: datetime
    line_id: str
    parameter_name: str
    parameter_value: float  # 对应数据库 Double 类型
    alarm_message: str
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    alarm_rule_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlarmRecordListResponse(BaseModel):
    """报警记录列表响应模型"""
    items: list[AlarmRecordResponse]
    total: int
    page: int
    size: int
