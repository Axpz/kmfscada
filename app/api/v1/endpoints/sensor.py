from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.SensorReading])
def read_sensor_readings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sensor readings.
    """
    sensor_readings = crud.sensor_reading.get_multi(db, skip=skip, limit=limit)
    return sensor_readings


@router.post("/", response_model=schemas.SensorReading)
def create_sensor_reading(
    *,
    db: Session = Depends(deps.get_db),
    sensor_reading_in: schemas.SensorReadingCreate,
) -> Any:
    """
    Create new sensor reading.
    """
    sensor_reading = crud.sensor_reading.create(db=db, obj_in=sensor_reading_in)
    return sensor_reading


@router.get("/{sensor_reading_id}", response_model=schemas.SensorReading)
def read_sensor_reading(
    *,
    db: Session = Depends(deps.get_db),
    sensor_reading_id: int,
) -> Any:
    """
    Get sensor reading by ID.
    """
    sensor_reading = crud.sensor_reading.get(db=db, id=sensor_reading_id)
    if not sensor_reading:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    return sensor_reading


@router.put("/{sensor_reading_id}", response_model=schemas.SensorReading)
def update_sensor_reading(
    *,
    db: Session = Depends(deps.get_db),
    sensor_reading_id: int,
    sensor_reading_in: schemas.SensorReadingUpdate,
) -> Any:
    """
    Update sensor reading.
    """
    sensor_reading = crud.sensor_reading.get(db=db, id=sensor_reading_id)
    if not sensor_reading:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    sensor_reading = crud.sensor_reading.update(db=db, db_obj=sensor_reading, obj_in=sensor_reading_in)
    return sensor_reading


@router.delete("/{sensor_reading_id}", response_model=schemas.SensorReading)
def delete_sensor_reading(
    *,
    db: Session = Depends(deps.get_db),
    sensor_reading_id: int,
) -> Any:
    """
    Delete sensor reading.
    """
    sensor_reading = crud.sensor_reading.get(db=db, id=sensor_reading_id)
    if not sensor_reading:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    sensor_reading = crud.sensor_reading.remove(db=db, id=sensor_reading_id)
    return sensor_reading


@router.get("/sensor/{sensor_id}", response_model=List[schemas.SensorReading])
def read_sensor_readings_by_sensor_id(
    *,
    db: Session = Depends(deps.get_db),
    sensor_id: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sensor readings by sensor ID.
    """
    sensor_readings = crud.sensor_reading.get_by_sensor_id(
        db=db, sensor_id=sensor_id, skip=skip, limit=limit
    )
    return sensor_readings


@router.get("/sensor/{sensor_id}/latest", response_model=schemas.SensorReading)
def read_latest_sensor_reading(
    *,
    db: Session = Depends(deps.get_db),
    sensor_id: str,
) -> Any:
    """
    Get latest sensor reading by sensor ID.
    """
    sensor_reading = crud.sensor_reading.get_latest_by_sensor_id(db=db, sensor_id=sensor_id)
    if not sensor_reading:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    return sensor_reading


@router.get("/location/{location}", response_model=List[schemas.SensorReading])
def read_sensor_readings_by_location(
    *,
    db: Session = Depends(deps.get_db),
    location: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sensor readings by location.
    """
    sensor_readings = crud.sensor_reading.get_by_location(
        db=db, location=location, skip=skip, limit=limit
    )
    return sensor_readings


@router.get("/recent/", response_model=List[schemas.SensorReading])
def read_recent_sensor_readings(
    *,
    db: Session = Depends(deps.get_db),
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve recent sensor readings (last N hours).
    """
    sensor_readings = crud.sensor_reading.get_recent_readings(
        db=db, hours=hours, skip=skip, limit=limit
    )
    return sensor_readings


@router.get("/sensor/{sensor_id}/average")
def read_sensor_average(
    *,
    db: Session = Depends(deps.get_db),
    sensor_id: str,
    hours: int = Query(24, ge=1, le=168),
) -> Any:
    """
    Get average value for a sensor over the last N hours.
    """
    average = crud.sensor_reading.get_average_by_sensor_id(
        db=db, sensor_id=sensor_id, hours=hours
    )
    if average is None:
        raise HTTPException(status_code=404, detail="No data found for the specified period")
    return {"sensor_id": sensor_id, "average": average, "hours": hours}


@router.get("/sensor/{sensor_id}/statistics")
def read_sensor_statistics(
    *,
    db: Session = Depends(deps.get_db),
    sensor_id: str,
    hours: int = Query(24, ge=1, le=168),
) -> Any:
    """
    Get statistics for a sensor over the last N hours.
    """
    statistics = crud.sensor_reading.get_statistics_by_sensor_id(
        db=db, sensor_id=sensor_id, hours=hours
    )
    if statistics["count"] == 0:
        raise HTTPException(status_code=404, detail="No data found for the specified period")
    return {"sensor_id": sensor_id, "statistics": statistics, "hours": hours} 