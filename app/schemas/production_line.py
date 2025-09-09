from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime

# This is the Python equivalent of your TypeScript type
ProductionLineStatus = Literal['running', 'idle', 'offline']

class ProductionLineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="生产线名称")
    description: Optional[str] = Field(None, max_length=500, description="生产线描述")
    enabled: bool = Field(True, description="是否启用")
    status: ProductionLineStatus = Field('idle', description="运行状态")

class ProductionLineCreate(ProductionLineBase):
    pass  # 继承 Base 的所有字段，不需要额外的 id 字段

class ProductionLineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="生产线名称")
    description: Optional[str] = Field(None, max_length=500, description="生产线描述")
    enabled: Optional[bool] = Field(None, description="是否启用")
    status: Optional[ProductionLineStatus] = Field(None, description="运行状态")

class ProductionLineInDB(ProductionLineBase):
    id: int = Field(..., description="数据库自增主键")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)

# 分页和过滤模型
class ProductionLineFilter(BaseModel):
    page: int = Field(1, ge=1, description="页码，从1开始")
    size: int = Field(100, ge=1, le=1000, description="每页数量，最大1000")
    enabled: Optional[bool] = Field(None, description="启用状态过滤")
    status: Optional[ProductionLineStatus] = Field(None, description="运行状态过滤")
    name: Optional[str] = Field(None, description="名称模糊搜索")
    description: Optional[str] = Field(None, description="描述模糊搜索")

class ProductionLineListResponse(BaseModel):
    items: list[ProductionLineInDB] = Field(..., description="生产线列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
