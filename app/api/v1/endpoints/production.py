from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime
from app.api import deps

router = APIRouter()

# Mock production data - in real implementation, this would come from database
MOCK_PRODUCTION_DATA = [
    {
        "id": 1,
        "line_id": "LINE_001",
        "batch_number": "BATCH_2024_001",
        "status": "running",
        "current": 15.5,
        "voltage": 220.0,
        "power": 3410.0,
        "temperature": 45.2,
        "fluoride_concentration": 0.8,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "line_id": "LINE_002",
        "batch_number": "BATCH_2024_002",
        "status": "stopped",
        "current": 0.0,
        "voltage": 0.0,
        "power": 0.0,
        "temperature": 25.0,
        "fluoride_concentration": 0.2,
        "created_at": "2024-01-15T09:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
    }
]

@router.get("/lines")
async def get_production_lines(
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
):
    """Get all production lines status"""
    # Return production lines data
    return {
        "lines": [
            {
                "id": line["line_id"],
                "status": line["status"],
                "batch_number": line["batch_number"],
                "current": line["current"],
                "voltage": line["voltage"],
                "power": line["power"],
                "temperature": line["temperature"],
                "fluoride_concentration": line["fluoride_concentration"],
                "last_updated": line["updated_at"]
            }
            for line in MOCK_PRODUCTION_DATA
        ]
    }

@router.get("/lines/{line_id}")
async def get_production_line(
    line_id: str,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
):
    """Get specific production line details"""
    # Find the specific line
    line_data = next((line for line in MOCK_PRODUCTION_DATA if line["line_id"] == line_id), None)
    
    if not line_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production line not found"
        )
    
    return {
        "id": line_data["line_id"],
        "status": line_data["status"],
        "batch_number": line_data["batch_number"],
        "current": line_data["current"],
        "voltage": line_data["voltage"],
        "power": line_data["power"],
        "temperature": line_data["temperature"],
        "fluoride_concentration": line_data["fluoride_concentration"],
        "created_at": line_data["created_at"],
        "updated_at": line_data["updated_at"]
    }

@router.post("/lines/{line_id}/start")
async def start_production_line(
    line_id: str,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
):
    """Start a production line"""
    # In real implementation, this would send command to MQTT or PLC
    return {
        "message": f"Production line {line_id} started successfully",
        "line_id": line_id,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/lines/{line_id}/stop")
async def stop_production_line(
    line_id: str,
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
):
    """Stop a production line"""
    # In real implementation, this would send command to MQTT or PLC
    return {
        "message": f"Production line {line_id} stopped successfully",
        "line_id": line_id,
        "status": "stopped",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/analytics/energy")
async def get_energy_analytics(
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
):
    """Get energy consumption analytics"""
    # Mock energy analytics data
    return {
        "total_energy_consumption": 1250.5,  # kWh
        "average_power": 3410.0,  # W
        "peak_power": 5000.0,  # W
        "energy_efficiency": 85.5,  # %
        "cost_per_hour": 12.50,  # USD
        "daily_consumption": 82.0,  # kWh
        "monthly_consumption": 2460.0,  # kWh
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/analytics/fluoride")
async def get_fluoride_analytics(
    current_user: Dict[str, Any] = Depends(deps.get_current_active_user)
):
    """Get fluoride concentration analytics"""
    # Mock fluoride analytics data
    return {
        "current_concentration": 0.8,  # mg/L
        "average_concentration": 0.75,  # mg/L
        "max_concentration": 1.2,  # mg/L
        "min_concentration": 0.2,  # mg/L
        "safety_threshold": 1.0,  # mg/L
        "status": "normal",  # normal, warning, critical
        "last_measurement": "2024-01-15T10:30:00Z",
        "measurement_frequency": "1s"
    } 