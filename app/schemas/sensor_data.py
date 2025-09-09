from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SensorDataBase(BaseModel):
    timestamp: datetime
    line_id: str
    component_id: str
    
    # 生产业务数据
    batch_product_number: Optional[str] = None
    current_length: Optional[float] = None
    target_length: Optional[float] = None
    diameter: Optional[float] = None
    fluoride_concentration: Optional[float] = None

    # 温度传感器组
    temp_body_zone1: Optional[float] = None
    temp_body_zone2: Optional[float] = None
    temp_body_zone3: Optional[float] = None
    temp_body_zone4: Optional[float] = None
    temp_flange_zone1: Optional[float] = None
    temp_flange_zone2: Optional[float] = None
    temp_mold_zone1: Optional[float] = None
    temp_mold_zone2: Optional[float] = None

    # 电流传感器组
    current_body_zone1: Optional[float] = None
    current_body_zone2: Optional[float] = None
    current_body_zone3: Optional[float] = None
    current_body_zone4: Optional[float] = None
    current_flange_zone1: Optional[float] = None
    current_flange_zone2: Optional[float] = None
    current_mold_zone1: Optional[float] = None
    current_mold_zone2: Optional[float] = None

    # 电机参数
    motor_screw_speed: Optional[float] = None
    motor_screw_torque: Optional[float] = None
    motor_current: Optional[float] = None
    motor_traction_speed: Optional[float] = None
    motor_vacuum_speed: Optional[float] = None

    # 收卷机
    winder_speed: Optional[float] = None
    winder_torque: Optional[float] = None
    winder_layer_count: Optional[float] = None
    winder_tube_speed: Optional[float] = None
    winder_tube_count: Optional[float] = None

    # 时间戳字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SensorData(SensorDataBase):
    model_config = ConfigDict(from_attributes=True)


class SensorDataFilter(BaseModel):
    line_id: str = Field(..., description="生产线ID", example="LINE_001")
    component_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    parameter_name: Optional[str] = None
    page: Optional[int] = 1
    size: Optional[int] = 100


class SensorDataExportFilter(BaseModel):
    line_ids: str = Field(..., description="生产线ID", example="LINE_001,LINE_002")
    component_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    parameter_names: Optional[str] = None


class SensorDataListResponse(BaseModel):
    items: List[SensorData]
    total: int
    page: int
    size: int


class UtilizationResponse(BaseModel):
    line_id: str
    total_run_time_seconds: int
    total_idle_time_seconds: int
    total_offline_time_seconds: int