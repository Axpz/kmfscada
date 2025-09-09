from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Text,
    DateTime,
    Double,
    PrimaryKeyConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.schema import DDL
from sqlalchemy.event import listen

from app.db.base_class import Base


class SensorData(Base):

    __tablename__ = "sensor_data"

    # 核心维度：标识数据来源和时间
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False, default=func.now())
    line_id = Column(Text, primary_key=True, nullable=False, index=True)
    component_id = Column(Text, primary_key=True, nullable=False, index=True)
    
    # === 生产业务数据 ===
    batch_product_number = Column(Text)
    current_length = Column(Double)
    target_length = Column(Double)
    diameter = Column(Double)
    fluoride_concentration = Column(Double)

    # === 温度传感器组 ===
    temp_body_zone1 = Column(Double)
    temp_body_zone2 = Column(Double)
    temp_body_zone3 = Column(Double)
    temp_body_zone4 = Column(Double)
    temp_flange_zone1 = Column(Double)
    temp_flange_zone2 = Column(Double)
    temp_mold_zone1 = Column(Double)
    temp_mold_zone2 = Column(Double)

    # === 电流传感器组 ===
    current_body_zone1 = Column(Double)
    current_body_zone2 = Column(Double)
    current_body_zone3 = Column(Double)
    current_body_zone4 = Column(Double)
    current_flange_zone1 = Column(Double)
    current_flange_zone2 = Column(Double)
    current_mold_zone1 = Column(Double)
    current_mold_zone2 = Column(Double)

    # === 电机参数 ===
    motor_screw_speed = Column(Double)
    motor_screw_torque = Column(Double)
    motor_current = Column(Double)
    motor_traction_speed = Column(Double)
    motor_vacuum_speed = Column(Double)

    # === 收卷机 ===
    winder_speed = Column(Double)
    winder_torque = Column(Double)
    winder_layer_count = Column(Double)
    winder_tube_speed = Column(Double)
    winder_tube_count = Column(Double)

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # 使用复合主键来确保每个条目的唯一性
    __table_args__ = (
        PrimaryKeyConstraint('timestamp', 'line_id', 'component_id', name='sensor_data_pkey'),
    )

# 监听表创建事件，自动将其转换为 hypertable
# 该 DDL 语句在表创建后立即执行
create_hypertable_ddl = DDL("""
    SELECT create_hypertable('sensor_data', 'timestamp', chunk_time_interval => INTERVAL '1 day');
""")

listen(SensorData.__table__, 'after_create', create_hypertable_ddl)