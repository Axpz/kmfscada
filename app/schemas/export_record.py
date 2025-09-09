from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime

# 导出任务状态类型
ExportRecordStatus = Literal['pending', 'processing', 'completed', 'failed']


class ExportRecordBase(BaseModel):
    line_names: str = Field(..., description="导出的生产线名称（多个用逗号分隔）")
    fields: str = Field(..., description="导出的数据字段（多个用逗号分隔）")
    start_time: datetime = Field(..., description="导出的开始时间")
    end_time: datetime = Field(..., description="导出的结束时间")
    format: str = Field('xlsx', description="文件格式")
    size: Optional[int] = Field(None, description="文件大小")
    created_by: Optional[str] = Field(None, description="创建用户")

class ExportRecordCreate(ExportRecordBase):
    pass

class ExportRecordInDB(ExportRecordBase):
    id: int = Field(..., description="导出记录ID")
    status: ExportRecordStatus = Field(..., description="任务状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)

# 导出记录过滤模型
class ExportRecordFilter(BaseModel):
    page: int = Field(1, description="页码，从1开始")
    size: int = Field(100, description="每页数量，最大100")
    status: Optional[ExportRecordStatus] = Field(None, description="状态过滤")
    created_by: Optional[str] = Field(None, description="创建用户过滤")
    format: Optional[str] = Field(None, description="文件格式过滤")

# 导出记录列表响应
class ExportRecordListResponse(BaseModel):
    items: list[ExportRecordInDB] = Field(..., description="导出记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")