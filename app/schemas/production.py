from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ProductionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = "active"
    is_active: Optional[bool] = True


class ProductionCreate(ProductionBase):
    name: str
    value: float
    unit: str


class ProductionUpdate(ProductionBase):
    pass


class ProductionInDBBase(ProductionBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Production(ProductionInDBBase):
    pass


class ProductionInDB(ProductionInDBBase):
    pass 