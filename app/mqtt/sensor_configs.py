from typing import Dict, Any, Tuple, Optional, List
import math
import random
import time
import json
from datetime import datetime

# 传感器配置
SENSOR_CONFIGS = {
    "temp_line1_01": {
        "type": "temperature",
        "unit": "°C",
        "range": (20, 80),
        "location": "production_line_1",
        "base_value": 45,  # 基准值
        "variation": 10    # 变化幅度
    },
    "humid_line1_01": {
        "type": "humidity", 
        "unit": "%",
        "range": (30, 90),
        "location": "production_line_1",
        "base_value": 60,
        "variation": 15
    },
    "press_line2_01": {
        "type": "pressure",
        "unit": "bar", 
        "range": (1, 10),
        "location": "production_line_2",
        "base_value": 5.5,
        "variation": 2
    },
    "flow_line2_01": {
        "type": "flow_rate",
        "unit": "L/min",
        "range": (0, 100), 
        "location": "production_line_2",
        "base_value": 50,
        "variation": 20
    }
}

def generate_sensor_value(sensor_id: str, config: Dict[str, Any]) -> float:
    """生成传感器数值"""
    # 基于时间的正弦波 + 随机噪声
    now = datetime.now()
    time_factor = now.hour * 3600 + now.minute * 60 + now.second
    
    # 正弦波变化（模拟日常波动）
    sine_wave = math.sin(time_factor / 3600) * config["variation"] * 0.3
    
    # 随机噪声
    noise = random.uniform(-config["variation"] * 0.2, config["variation"] * 0.2)
    
    # 计算最终值
    value = config["base_value"] + sine_wave + noise
    
    # 确保在合理范围内
    min_val, max_val = config["range"]
    value = max(min_val, min(max_val, value))
    
    # 偶尔生成异常值（5%概率）
    if random.random() < 0.05:
        if random.random() < 0.5:
            value = min_val - random.uniform(1, 5)  # 低异常
        else:
            value = max_val + random.uniform(1, 5)  # 高异常
    
    return round(value, 2)

def get_sensor_status(value: float, config: Dict[str, Any]) -> str:
    """根据数值判断传感器状态"""
    min_val, max_val = config["range"]
    
    if value < min_val or value > max_val:
        return "error"
    elif value < min_val * 1.1 or value > max_val * 0.9:
        return "warning" 
    else:
        return "normal"
    


def random_sensor_value(min_val: float, max_val: float, alarm_threshold: Optional[float] = None) -> Dict[str, Any]:
    """生成随机传感器数值，带报警标记"""
    value = round(random.uniform(min_val, max_val), 2)
    alarm = False
    alarm_code = None
    alarm_message = None

    if alarm_threshold is not None and value > alarm_threshold:
        alarm = True
        alarm_code = "OVER_THRESHOLD"
        alarm_message = f"超过阈值 {alarm_threshold}"

    return {
        "value": value,
        "alarm": alarm,
        "alarmCode": alarm_code,
        "alarmMessage": alarm_message
    }


def generate_production_line_data(line_id: str, name: str) -> Dict[str, Any]:
    return {
        "id": line_id,
        "name": name,
        "status": random.choice(["running", "idle", "offline"]),
        "production": {
            "batch": {
                "product": f"P-{random.randint(1000,9999)}",
                "material": f"M-{random.randint(1000,9999)}"
            },
            "metrics": {
                "length": random_sensor_value(0, 500, alarm_threshold=450),
                "targetLength": random_sensor_value(400, 500),
                "diameter": random_sensor_value(4.0, 6.0, alarm_threshold=5.5),
                "fluorideConcentration": random_sensor_value(0.5, 2.0, alarm_threshold=1.5)
            }
        },
        "sensors": {
            "temperatures": {
                "body": {
                    "zone1": random_sensor_value(170, 200, alarm_threshold=190),
                    "zone2": random_sensor_value(170, 200, alarm_threshold=190),
                    "zone3": random_sensor_value(170, 200, alarm_threshold=190),
                    "zone4": random_sensor_value(170, 200, alarm_threshold=190)
                },
                "flange": {
                    "zone1": random_sensor_value(140, 160, alarm_threshold=155),
                    "zone2": random_sensor_value(140, 160, alarm_threshold=155)
                },
                "mold": {
                    "zone1": random_sensor_value(150, 170, alarm_threshold=165),
                    "zone2": random_sensor_value(150, 170, alarm_threshold=165)
                }
            },
            "motors": {
                "screwSpeed": random_sensor_value(80, 150, alarm_threshold=140),
                "tractionSpeed": random_sensor_value(2.0, 5.0, alarm_threshold=4.5),
                "torque": random_sensor_value(50, 100, alarm_threshold=90),
                "mainSpindleCurrent": random_sensor_value(30, 60, alarm_threshold=55)
            }
        },
        "metadata": {
            "dataSource": "mock",
            "timestamp": int(time.time() * 1000),
            "rawData": {"debug": "simulated data packet"}
        }
    }


def generate_sensor_data_for_db(line_id: str, component_id: str) -> Dict[str, Any]:
    """
    生成符合SensorData数据库模型的数据
    返回的字典可以直接用于创建SensorData实例
    """
    # 生成基础时间戳
    timestamp = datetime.now()
    
    # 生成生产业务数据
    batch_product_number = f"P-{random.randint(1000, 9999)}"
    current_length = round(random.uniform(0, 500), 2)
    target_length = round(random.uniform(400, 500), 2)
    diameter = round(random.uniform(4.0, 6.0), 2)
    fluoride_concentration = round(random.uniform(0.5, 2.0), 2)
    
    # 生成温度传感器数据
    temp_body_zone1 = round(random.uniform(170, 200), 2)
    temp_body_zone2 = round(random.uniform(170, 200), 2)
    temp_body_zone3 = round(random.uniform(170, 200), 2)
    temp_body_zone4 = round(random.uniform(170, 200), 2)
    temp_flange_zone1 = round(random.uniform(140, 160), 2)
    temp_flange_zone2 = round(random.uniform(140, 160), 2)
    temp_mold_zone1 = round(random.uniform(150, 170), 2)
    temp_mold_zone2 = round(random.uniform(150, 170), 2)
    
    # 生成电流传感器数据
    current_body_zone1 = round(random.uniform(5, 15), 2)
    current_body_zone2 = round(random.uniform(5, 15), 2)
    current_body_zone3 = round(random.uniform(5, 15), 2)
    current_body_zone4 = round(random.uniform(5, 15), 2)
    current_flange_zone1 = round(random.uniform(3, 10), 2)
    current_flange_zone2 = round(random.uniform(3, 10), 2)
    current_mold_zone1 = round(random.uniform(4, 12), 2)
    current_mold_zone2 = round(random.uniform(4, 12), 2)
    
    # 生成电机参数
    motor_screw_speed = round(random.uniform(80, 150), 2)
    motor_screw_torque = round(random.uniform(50, 100), 2)
    motor_current = round(random.uniform(30, 60), 2)
    motor_traction_speed = round(random.uniform(2.0, 5.0), 2)
    motor_vacuum_speed = round(random.uniform(10, 30), 2)
    
    # 生成收卷机数据
    winder_speed = round(random.uniform(100, 300), 2)
    winder_torque = round(random.uniform(20, 80), 2)
    winder_layer_count = round(random.uniform(1, 50), 0)
    winder_tube_speed = round(random.uniform(5, 15), 2)
    winder_tube_count = round(random.uniform(1, 20), 0)
    
    return {
        "timestamp": timestamp.isoformat().replace('Z', '+00:00'),
        "line_id": line_id,
        "component_id": component_id,
        "batch_product_number": batch_product_number,
        "current_length": current_length,
        "target_length": target_length,
        "diameter": diameter,
        "fluoride_concentration": fluoride_concentration,
        "temp_body_zone1": temp_body_zone1,
        "temp_body_zone2": temp_body_zone2,
        "temp_body_zone3": temp_body_zone3,
        "temp_body_zone4": temp_body_zone4,
        "temp_flange_zone1": temp_flange_zone1,
        "temp_flange_zone2": temp_flange_zone2,
        "temp_mold_zone1": temp_mold_zone1,
        "temp_mold_zone2": temp_mold_zone2,
        "current_body_zone1": current_body_zone1,
        "current_body_zone2": current_body_zone2,
        "current_body_zone3": current_body_zone3,
        "current_body_zone4": current_body_zone4,
        "current_flange_zone1": current_flange_zone1,
        "current_flange_zone2": current_flange_zone2,
        "current_mold_zone1": current_mold_zone1,
        "current_mold_zone2": current_mold_zone2,
        "motor_screw_speed": motor_screw_speed,
        "motor_screw_torque": motor_screw_torque,
        "motor_current": motor_current,
        "motor_traction_speed": motor_traction_speed,
        "motor_vacuum_speed": motor_vacuum_speed,
        "winder_speed": winder_speed,
        "winder_torque": winder_torque,
        "winder_layer_count": winder_layer_count,
        "winder_tube_speed": winder_tube_speed,
        "winder_tube_count": winder_tube_count
    }


def generate_multiple_sensor_data_records(line_ids: Optional[List[str]] = None, component_ids: Optional[List[str]] = None, count: int = 2) -> List[Dict[str, Any]]:
    """
    生成多条SensorData记录
    
    Args:
        line_ids: 生产线ID列表，默认为["line_001", "line_002", "line_003"]
        component_ids: 组件ID列表，默认为["extruder", "cooler", "winder", "cutter"]
        count: 生成记录数量
    
    Returns:
        包含多条SensorData记录的列表
    """
    if line_ids is None:
        line_ids = ["line_001", "line_002", "line_003"]
    
    if component_ids is None:
        component_ids = ["extruder", "cooler", "winder", "cutter"]
    
    records = []
    for _ in range(count):
        line_id = random.choice(line_ids)
        component_id = random.choice(component_ids)
        record = generate_sensor_data_for_db(line_id, component_id)
        records.append(record)
    
    return records