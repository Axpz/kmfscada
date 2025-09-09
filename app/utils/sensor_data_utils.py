from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import statistics
from app.models.sensor import SensorData


def calculate_temperature_gradient(temperatures: List[float]) -> float:
    """计算温度梯度"""
    if len(temperatures) < 2:
        return 0.0
    
    # 计算相邻温度点的差值
    gradients = [abs(temperatures[i] - temperatures[i-1]) for i in range(1, len(temperatures))]
    return statistics.mean(gradients) if gradients else 0.0


def detect_temperature_anomalies(temperatures: List[float], threshold: float = 2.0) -> List[int]:
    """检测温度异常点"""
    if len(temperatures) < 3:
        return []
    
    anomalies = []
    for i in range(1, len(temperatures) - 1):
        # 使用3点移动平均检测异常
        prev_temp = temperatures[i-1]
        curr_temp = temperatures[i]
        next_temp = temperatures[i+1]
        
        # 如果当前温度与前后温度差异过大，认为是异常
        if (abs(curr_temp - prev_temp) > threshold and 
            abs(curr_temp - next_temp) > threshold):
            anomalies.append(i)
    
    return anomalies


def calculate_thermal_efficiency(target_temp: float, actual_temp: float, 
                               energy_consumption: float) -> float:
    """计算热效率"""
    if energy_consumption <= 0:
        return 0.0
    
    # 简化的热效率计算
    temp_efficiency = max(0, 100 - abs(target_temp - actual_temp) / target_temp * 100)
    energy_efficiency = min(100, 1000 / energy_consumption * 100)  # 假设1000为基准能耗
    
    return (temp_efficiency + energy_efficiency) / 2


def analyze_motor_performance(speed: float, torque: float, current: float, 
                            max_speed: float, max_torque: float, max_current: float) -> Dict[str, Any]:
    """分析电机性能"""
    if max_speed <= 0 or max_torque <= 0 or max_current <= 0:
        return {"error": "Invalid maximum values"}
    
    # 计算各项性能指标
    speed_efficiency = min(100, max(0, (speed / max_speed) * 100))
    torque_efficiency = min(100, max(0, (torque / max_torque) * 100))
    current_efficiency = min(100, max(0, (1 - current / max_current) * 100))
    
    # 计算综合性能
    overall_efficiency = (speed_efficiency + torque_efficiency + current_efficiency) / 3
    
    # 性能评级
    if overall_efficiency >= 90:
        performance_grade = "A"
    elif overall_efficiency >= 80:
        performance_grade = "B"
    elif overall_efficiency >= 70:
        performance_grade = "C"
    else:
        performance_grade = "D"
    
    return {
        "speed_efficiency": round(speed_efficiency, 2),
        "torque_efficiency": round(torque_efficiency, 2),
        "current_efficiency": round(current_efficiency, 2),
        "overall_efficiency": round(overall_efficiency, 2),
        "performance_grade": performance_grade,
        "recommendations": _generate_motor_recommendations(speed_efficiency, torque_efficiency, current_efficiency)
    }


def _generate_motor_recommendations(speed_eff: float, torque_eff: float, current_eff: float) -> List[str]:
    """生成电机性能建议"""
    recommendations = []
    
    if speed_eff < 70:
        recommendations.append("电机速度效率较低，建议检查负载和调整参数")
    
    if torque_eff < 70:
        recommendations.append("电机扭矩效率较低，建议检查传动系统和润滑")
    
    if current_eff < 70:
        recommendations.append("电机电流效率较低，建议检查电气系统和负载")
    
    if not recommendations:
        recommendations.append("电机性能良好，继续保持")
    
    return recommendations


def calculate_production_efficiency(current_length: float, target_length: float,
                                 production_time: float, target_time: float) -> Dict[str, Any]:
    """计算生产效率"""
    if target_length <= 0 or target_time <= 0:
        return {"error": "Invalid target values"}
    
    # 长度完成率
    length_completion = min(100, max(0, (current_length / target_length) * 100))
    
    # 时间效率
    time_efficiency = min(100, max(0, (target_time / production_time) * 100)) if production_time > 0 else 0
    
    # 综合效率
    overall_efficiency = (length_completion + time_efficiency) / 2
    
    # 效率评级
    if overall_efficiency >= 95:
        efficiency_grade = "Excellent"
    elif overall_efficiency >= 85:
        efficiency_grade = "Good"
    elif overall_efficiency >= 75:
        efficiency_grade = "Fair"
    else:
        efficiency_grade = "Poor"
    
    return {
        "length_completion": round(length_completion, 2),
        "time_efficiency": round(time_efficiency, 2),
        "overall_efficiency": round(overall_efficiency, 2),
        "efficiency_grade": efficiency_grade,
        "length_deviation": round(abs(current_length - target_length) / target_length * 100, 2),
        "time_deviation": round(abs(production_time - target_time) / target_time * 100, 2) if target_time > 0 else 0
    }


def analyze_winder_performance(speed: float, torque: float, layer_count: float,
                             tube_speed: float, tube_count: float) -> Dict[str, Any]:
    """分析收卷机性能"""
    # 速度效率（假设300为最大速度）
    max_speed = 300
    speed_efficiency = min(100, max(0, (speed / max_speed) * 100))
    
    # 扭矩效率（假设80为最大扭矩）
    max_torque = 80
    torque_efficiency = min(100, max(0, (torque / max_torque) * 100))
    
    # 层数效率（假设50为最大层数）
    max_layers = 50
    layer_efficiency = min(100, max(0, (layer_count / max_layers) * 100))
    
    # 综合效率
    overall_efficiency = (speed_efficiency + torque_efficiency + layer_efficiency) / 3
    
    # 性能评级
    if overall_efficiency >= 90:
        performance_grade = "A"
    elif overall_efficiency >= 80:
        performance_grade = "B"
    elif overall_efficiency >= 70:
        performance_grade = "C"
    else:
        performance_grade = "D"
    
    return {
        "speed_efficiency": round(speed_efficiency, 2),
        "torque_efficiency": round(torque_efficiency, 2),
        "layer_efficiency": round(layer_efficiency, 2),
        "overall_efficiency": round(overall_efficiency, 2),
        "performance_grade": performance_grade,
        "tube_throughput": round(tube_speed * tube_count, 2),
        "recommendations": _generate_winder_recommendations(speed_efficiency, torque_efficiency, layer_efficiency)
    }


def _generate_winder_recommendations(speed_eff: float, torque_eff: float, layer_eff: float) -> List[str]:
    """生成收卷机性能建议"""
    recommendations = []
    
    if speed_eff < 70:
        recommendations.append("收卷速度效率较低，建议检查传动系统和张力控制")
    
    if torque_eff < 70:
        recommendations.append("收卷扭矩效率较低，建议检查制动系统和负载分布")
    
    if layer_eff < 70:
        recommendations.append("层数效率较低，建议检查卷绕机构和张力控制")
    
    if not recommendations:
        recommendations.append("收卷机性能良好，继续保持")
    
    return recommendations


def calculate_data_consistency(sensor_data_list: List[SensorData], field_name: str) -> Dict[str, Any]:
    """计算数据一致性"""
    if not sensor_data_list:
        return {"error": "No data provided"}
    
    # 提取指定字段的值
    values = []
    for data in sensor_data_list:
        value = getattr(data, field_name, None)
        if value is not None:
            values.append(value)
    
    if not values:
        return {"error": f"No valid values for field: {field_name}"}
    
    # 计算统计指标
    mean_value = statistics.mean(values)
    std_dev = statistics.stdev(values) if len(values) > 1 else 0
    min_value = min(values)
    max_value = max(values)
    range_value = max_value - min_value
    
    # 计算变异系数
    coefficient_of_variation = (std_dev / mean_value * 100) if mean_value != 0 else 0
    
    # 一致性评级
    if coefficient_of_variation < 5:
        consistency_grade = "Excellent"
    elif coefficient_of_variation < 10:
        consistency_grade = "Good"
    elif coefficient_of_variation < 20:
        consistency_grade = "Fair"
    else:
        consistency_grade = "Poor"
    
    return {
        "field_name": field_name,
        "sample_count": len(values),
        "mean": round(mean_value, 4),
        "std_dev": round(std_dev, 4),
        "min": round(min_value, 4),
        "max": round(max_value, 4),
        "range": round(range_value, 4),
        "coefficient_of_variation": round(coefficient_of_variation, 2),
        "consistency_grade": consistency_grade
    }


def detect_data_drift(sensor_data_list: List[SensorData], field_name: str, 
                     window_size: int = 10) -> Dict[str, Any]:
    """检测数据漂移"""
    if not sensor_data_list or len(sensor_data_list) < window_size:
        return {"error": "Insufficient data for drift detection"}
    
    # 按时间排序
    sorted_data = sorted(sensor_data_list, key=lambda x: x.timestamp)
    
    # 提取指定字段的值
    values = []
    timestamps = []
    for data in sorted_data:
        value = getattr(data, field_name, None)
        if value is not None:
            values.append(value)
            timestamps.append(data.timestamp)
    
    if len(values) < window_size:
        return {"error": f"Insufficient valid values for field: {field_name}"}
    
    # 计算移动平均
    moving_averages = []
    for i in range(window_size - 1, len(values)):
        window_values = values[i - window_size + 1:i + 1]
        moving_averages.append(statistics.mean(window_values))
    
    # 计算漂移指标
    if len(moving_averages) > 1:
        # 线性回归斜率作为漂移指标
        x = list(range(len(moving_averages)))
        y = moving_averages
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        else:
            slope = 0
        
        # 漂移评级
        if abs(slope) < 0.01:
            drift_grade = "Stable"
        elif abs(slope) < 0.05:
            drift_grade = "Slight Drift"
        elif abs(slope) < 0.1:
            drift_grade = "Moderate Drift"
        else:
            drift_grade = "Significant Drift"
        
        return {
            "field_name": field_name,
            "window_size": window_size,
            "total_samples": len(values),
            "moving_average_samples": len(moving_averages),
            "drift_slope": round(slope, 6),
            "drift_grade": drift_grade,
            "trend_direction": "Increasing" if slope > 0 else "Decreasing" if slope < 0 else "Stable",
            "first_value": round(values[0], 4),
            "last_value": round(values[-1], 4),
            "total_change": round(values[-1] - values[0], 4),
            "change_rate": round(slope * 3600, 4)  # 每小时变化率
        }
    else:
        return {"error": "Insufficient data for drift calculation"}


def generate_health_score(sensor_data: SensorData) -> Dict[str, Any]:
    """生成设备健康评分"""
    try:
        # 检查是否有必要的方法
        if not hasattr(sensor_data, 'check_all_alarms'):
            return {"error": "Sensor data not enhanced with alarm checking capabilities"}
        
        # 获取报警信息
        alarms = sensor_data.check_all_alarms()
        alarm_count = len(alarms)
        
        # 计算报警扣分
        alarm_penalty = 0
        for alarm in alarms:
            if alarm.level.value == 'critical':
                alarm_penalty += 20
            elif alarm.level.value == 'error':
                alarm_penalty += 15
            elif alarm.level.value == 'warning':
                alarm_penalty += 10
            elif alarm.level.value == 'info':
                alarm_penalty += 5
        
        # 基础分数
        base_score = 100
        
        # 最终健康分数
        health_score = max(0, base_score - alarm_penalty)
        
        # 健康评级
        if health_score >= 90:
            health_grade = "Excellent"
            health_status = "Healthy"
        elif health_score >= 80:
            health_grade = "Good"
            health_status = "Healthy"
        elif health_score >= 70:
            health_grade = "Fair"
            health_status = "Attention Required"
        elif health_score >= 60:
            health_grade = "Poor"
            health_status = "Maintenance Required"
        else:
            health_grade = "Critical"
            health_status = "Immediate Action Required"
        
        return {
            "health_score": health_score,
            "health_grade": health_grade,
            "health_status": health_status,
            "base_score": base_score,
            "alarm_penalty": alarm_penalty,
            "total_alarms": alarm_count,
            "alarm_breakdown": {
                "critical": len([a for a in alarms if a.level.value == 'critical']),
                "error": len([a for a in alarms if a.level.value == 'error']),
                "warning": len([a for a in alarms if a.level.value == 'warning']),
                "info": len([a for a in alarms if a.level.value == 'info'])
            },
            "recommendations": _generate_health_recommendations(health_score, alarm_count)
        }
        
    except Exception as e:
        return {"error": f"Error calculating health score: {str(e)}"}


def _generate_health_recommendations(health_score: float, alarm_count: int) -> List[str]:
    """生成健康评分建议"""
    recommendations = []
    
    if health_score < 60:
        recommendations.append("设备健康状态严重，建议立即停机检查")
        recommendations.append("联系维护人员进行紧急维修")
    elif health_score < 70:
        recommendations.append("设备需要维护，建议安排停机时间")
        recommendations.append("检查所有报警项并逐一解决")
    elif health_score < 80:
        recommendations.append("设备状态一般，建议关注报警信息")
        recommendations.append("考虑预防性维护")
    elif health_score < 90:
        recommendations.append("设备状态良好，继续保持")
        recommendations.append("定期检查关键参数")
    else:
        recommendations.append("设备状态优秀，继续保持")
        recommendations.append("定期进行预防性维护")
    
    if alarm_count > 0:
        recommendations.append(f"当前有{alarm_count}个报警需要处理")
    
    return recommendations
