from sqlalchemy import Column, BigInteger, String, DateTime, Float, Text, JSON, PrimaryKeyConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    sensor_id = Column(Text, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    value = Column(Float, nullable=False)
    unit = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True, default={})

    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
     
    __table_args__ = (
        PrimaryKeyConstraint('sensor_id', 'timestamp', name='sensor_readings_pkey'),
    )