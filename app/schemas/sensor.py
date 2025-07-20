from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class SensorReadingBase(BaseModel):
    sensor_id: str
    value: float
    unit: Optional[str] = None
    location: Optional[str] = None
    meta: Optional[Dict[str, Any]] = {}


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReadingUpdate(SensorReadingBase):
    sensor_id: Optional[str] = None
    value: Optional[float] = None


class SensorReadingInDBBase(SensorReadingBase):
    id: Optional[int] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class SensorReading(SensorReadingInDBBase):
    pass


class SensorReadingInDB(SensorReadingInDBBase):
    pass 