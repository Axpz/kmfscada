from typing import Dict, Any, Tuple
import math
import random
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