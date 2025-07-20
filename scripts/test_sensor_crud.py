#!/usr/bin/env python3
"""
Test script for sensor data CRUD operations.
Tests all CRUD operations and some advanced queries.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any

from app.db.session import SessionLocal
from app.crud.crud_sensor import sensor_reading
from app.schemas.sensor import SensorReadingCreate, SensorReadingUpdate


def test_create_sensor_reading():
    """Test creating a sensor reading"""
    print("Testing sensor reading creation...")
    
    db = SessionLocal()
    try:
        # Create test sensor reading
        sensor_data = {
            "sensor_id": "test_sensor_001",
            "value": 25.5,
            "unit": "°C",
            "location": "workshop",
            "meta": {"test": True, "created_at": datetime.utcnow().isoformat()}
        }
        
        sensor_reading_in = SensorReadingCreate(**sensor_data)
        created_reading = sensor_reading.create(db=db, obj_in=sensor_reading_in)
        
        print(f"✓ Created sensor reading: ID={created_reading.id}, Value={created_reading.value} {created_reading.unit}")
        return created_reading.id
        
    except Exception as e:
        print(f"✗ Failed to create sensor reading: {e}")
        return None
    finally:
        db.close()


def test_read_sensor_reading(reading_id: int):
    """Test reading a sensor reading by ID"""
    print(f"Testing sensor reading retrieval (ID: {reading_id})...")
    
    db = SessionLocal()
    try:
        reading = sensor_reading.get(db=db, id=reading_id)
        if reading:
            print(f"✓ Retrieved sensor reading: {reading.sensor_id} = {reading.value} {reading.unit}")
            return reading
        else:
            print("✗ Sensor reading not found")
            return None
    except Exception as e:
        print(f"✗ Failed to retrieve sensor reading: {e}")
        return None
    finally:
        db.close()


def test_update_sensor_reading(reading_id: int):
    """Test updating a sensor reading"""
    print(f"Testing sensor reading update (ID: {reading_id})...")
    
    db = SessionLocal()
    try:
        # Get the reading first
        reading = sensor_reading.get(db=db, id=reading_id)
        if not reading:
            print("✗ Sensor reading not found for update")
            return None
        
        # Update the reading
        update_data = {
            "value": reading.value + 1.0,
            "meta": {"updated": True, "updated_at": datetime.utcnow().isoformat()}
        }
        
        updated_reading = sensor_reading.update(
            db=db, 
            db_obj=reading, 
            obj_in=SensorReadingUpdate(**update_data)
        )
        
        print(f"✓ Updated sensor reading: {updated_reading.value} {updated_reading.unit}")
        return updated_reading
        
    except Exception as e:
        print(f"✗ Failed to update sensor reading: {e}")
        return None
    finally:
        db.close()


def test_delete_sensor_reading(reading_id: int):
    """Test deleting a sensor reading"""
    print(f"Testing sensor reading deletion (ID: {reading_id})...")
    
    db = SessionLocal()
    try:
        deleted_reading = sensor_reading.remove(db=db, id=reading_id)
        print(f"✓ Deleted sensor reading: ID={deleted_reading.id}")
        return True
    except Exception as e:
        print(f"✗ Failed to delete sensor reading: {e}")
        return False
    finally:
        db.close()


def test_advanced_queries():
    """Test advanced query operations"""
    print("Testing advanced queries...")
    
    db = SessionLocal()
    try:
        # Create multiple test readings
        sensor_ids = ["temp_sensor_001", "humidity_sensor_001", "pressure_sensor_001"]
        locations = ["workshop", "office", "lab"]
        
        for i in range(10):
            sensor_id = random.choice(sensor_ids)
            unit = "°C" if "temp" in sensor_id else "%" if "humidity" in sensor_id else "hPa"
            sensor_data = {
                "sensor_id": sensor_id,
                "value": random.uniform(20, 30),
                "unit": unit,
                "location": random.choice(locations),
                "meta": {"test_batch": True, "batch_id": i}
            }
            
            sensor_reading_in = SensorReadingCreate(**sensor_data)
            sensor_reading.create(db=db, obj_in=sensor_reading_in)
        
        print("✓ Created 10 test sensor readings")
        
        # Test get by sensor_id
        readings = sensor_reading.get_by_sensor_id(db=db, sensor_id="temp_sensor_001", limit=5)
        print(f"✓ Found {len(readings)} readings for temp_sensor_001")
        
        # Test get by location
        readings = sensor_reading.get_by_location(db=db, location="workshop", limit=5)
        print(f"✓ Found {len(readings)} readings from workshop")
        
        # Test get recent readings
        readings = sensor_reading.get_recent_readings(db=db, hours=1, limit=10)
        print(f"✓ Found {len(readings)} recent readings (last hour)")
        
        # Test get average
        avg = sensor_reading.get_average_by_sensor_id(db=db, sensor_id="temp_sensor_001", hours=1)
        if avg:
            print(f"✓ Average temperature: {avg:.2f}°C")
        
        # Test get statistics
        stats = sensor_reading.get_statistics_by_sensor_id(db=db, sensor_id="temp_sensor_001", hours=1)
        if stats["count"] > 0:
            print(f"✓ Statistics: avg={stats['avg_value']:.2f}, min={stats['min_value']:.2f}, max={stats['max_value']:.2f}, count={stats['count']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Advanced queries failed: {e}")
        return False
    finally:
        db.close()


def main():
    """Main test function"""
    print("=== Sensor Data CRUD Test ===")
    print()
    
    # Test basic CRUD operations
    reading_id = test_create_sensor_reading()
    if reading_id:
        test_read_sensor_reading(reading_id)
        test_update_sensor_reading(reading_id)
        test_delete_sensor_reading(reading_id)
    
    print()
    
    # Test advanced queries
    test_advanced_queries()
    
    print()
    print("=== Test completed ===")


if __name__ == "__main__":
    main() 