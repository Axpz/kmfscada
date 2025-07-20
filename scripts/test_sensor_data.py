#!/usr/bin/env python3
"""
Test script for sensor data insertion.
Inserts a new sensor reading every second with simulated sensor data.
"""

import asyncio
import random
import time
from datetime import datetime
from typing import Dict, Any

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.crud.crud_sensor import sensor_reading
from app.schemas.sensor import SensorReadingCreate

# API base URL for testing
API_BASE_URL = "http://localhost:8080"


def create_sensor_reading_via_api(sensor_data: Dict[str, Any]) -> bool:
    """Create sensor reading via API endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sensor/",
            json=sensor_data,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"API call failed: {e}")
        return False


def create_sensor_reading_via_db(sensor_data: Dict[str, Any]) -> bool:
    """Create sensor reading directly via database"""
    try:
        db = SessionLocal()
        sensor_reading_in = SensorReadingCreate(**sensor_data)
        sensor_reading.create(db=db, obj_in=sensor_reading_in)
        db.close()
        return True
    except Exception as e:
        print(f"Database insertion failed: {e}")
        return False


def generate_sensor_data(sensor_id: str, location: str = "workshop") -> Dict[str, Any]:
    """Generate simulated sensor data"""
    # Simulate temperature sensor (20-30°C with some noise)
    base_temp = 25.0
    noise = random.uniform(-2, 2)
    temperature = base_temp + noise
    
    # Simulate humidity sensor (40-60% with some noise)
    base_humidity = 50.0
    noise = random.uniform(-5, 5)
    humidity = max(0, min(100, base_humidity + noise))
    
    # Simulate pressure sensor (1000-1020 hPa with some noise)
    base_pressure = 1013.25
    noise = random.uniform(-10, 10)
    pressure = base_pressure + noise
    
    # Choose a random sensor type
    sensor_types = [
        {"sensor_id": f"{sensor_id}_temp", "value": temperature, "unit": "°C", "location": location},
        {"sensor_id": f"{sensor_id}_humidity", "value": humidity, "unit": "%", "location": location},
        {"sensor_id": f"{sensor_id}_pressure", "value": pressure, "unit": "hPa", "location": location},
    ]
    
    return random.choice(sensor_types)


def main():
    """Main function to run the sensor data insertion test"""
    print("Starting sensor data insertion test...")
    print("Press Ctrl+C to stop")
    
    sensor_id = "test_sensor"
    location = "workshop"
    use_api = True  # Set to True to use API calls
    
    try:
        while True:
            # Generate sensor data
            sensor_data = generate_sensor_data(sensor_id, location)
            
            # Add metadata
            sensor_data["meta"] = {
                "test_run": True,
                "timestamp_created": datetime.utcnow().isoformat(),
                "random_seed": random.randint(1, 1000)
            }
            
            # Insert data
            success = False
            if use_api:
                success = create_sensor_reading_via_api(sensor_data)
            else:
                success = create_sensor_reading_via_db(sensor_data)
            
            if success:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Inserted: {sensor_data['sensor_id']} = {sensor_data['value']} {sensor_data['unit']}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed to insert sensor data")
            
            # Wait for 1 second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping sensor data insertion test...")


if __name__ == "__main__":
    main() 