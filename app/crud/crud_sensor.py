from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from app.crud.base import CRUDBase
from app.models.sensor import SensorReading
from app.schemas.sensor import SensorReadingCreate, SensorReadingUpdate


class CRUDSensorReading(CRUDBase[SensorReading, SensorReadingCreate, SensorReadingUpdate]):
    def get_by_sensor_id(self, db: Session, *, sensor_id: str, skip: int = 0, limit: int = 100) -> List[SensorReading]:
        return (
            db.query(SensorReading)
            .filter(SensorReading.sensor_id == sensor_id)
            .order_by(desc(SensorReading.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_by_sensor_id(self, db: Session, *, sensor_id: str) -> Optional[SensorReading]:
        return (
            db.query(SensorReading)
            .filter(SensorReading.sensor_id == sensor_id)
            .order_by(desc(SensorReading.timestamp))
            .first()
        )

    def get_by_location(self, db: Session, *, location: str, skip: int = 0, limit: int = 100) -> List[SensorReading]:
        return (
            db.query(SensorReading)
            .filter(SensorReading.location == location)
            .order_by(desc(SensorReading.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent_readings(self, db: Session, *, hours: int = 24, skip: int = 0, limit: int = 100) -> List[SensorReading]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return (
            db.query(SensorReading)
            .filter(SensorReading.timestamp >= cutoff_time)
            .order_by(desc(SensorReading.timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_average_by_sensor_id(self, db: Session, *, sensor_id: str, hours: int = 24) -> Optional[float]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        result = (
            db.query(func.avg(SensorReading.value))
            .filter(SensorReading.sensor_id == sensor_id)
            .filter(SensorReading.timestamp >= cutoff_time)
            .scalar()
        )
        return float(result) if result else None

    def get_statistics_by_sensor_id(self, db: Session, *, sensor_id: str, hours: int = 24) -> Dict[str, Any]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        result = (
            db.query(
                func.avg(SensorReading.value).label('avg_value'),
                func.min(SensorReading.value).label('min_value'),
                func.max(SensorReading.value).label('max_value'),
                func.count(SensorReading.id).label('count')
            )
            .filter(SensorReading.sensor_id == sensor_id)
            .filter(SensorReading.timestamp >= cutoff_time)
            .first()
        )
        
        if result:
            return {
                'avg_value': float(result.avg_value) if result.avg_value else None,
                'min_value': float(result.min_value) if result.min_value else None,
                'max_value': float(result.max_value) if result.max_value else None,
                'count': result.count
            }
        return {'avg_value': None, 'min_value': None, 'max_value': None, 'count': 0}


sensor_reading = CRUDSensorReading(SensorReading) 