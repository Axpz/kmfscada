#!/usr/bin/env python3
"""
测试新的SensorData架构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app.models.sensor import SensorData
from app.services.sensor_data_service import SensorDataService
from app.utils.sensor_data_utils import generate_health_score, analyze_motor_performance
from app.processors.data_transformer import DataTransformer


def test_sensor_data_enhancement():
    """测试传感器数据增强功能"""
    print("=== 测试传感器数据增强功能 ===")
    
    # 创建模拟的传感器数据
    sensor_data = SensorData(
        timestamp=datetime.now(),
        line_id="line_001",
        component_id="extruder",
        batch_product_number="P-1234",
        current_length=450.0,
        target_length=500.0,
        diameter=5.2,
        fluoride_concentration=1.8,
        temp_body_zone1=195.0,  # 超过阈值190
        temp_body_zone2=185.0,
        temp_body_zone3=175.0,
        temp_body_zone4=180.0,
        temp_flange_zone1=158.0,  # 超过阈值155
        temp_flange_zone2=150.0,
        temp_mold_zone1=160.0,
        temp_mold_zone2=155.0,
        current_body_zone1=13.5,  # 超过阈值12
        current_body_zone2=10.0,
        current_body_zone3=11.0,
        current_body_zone4=9.5,
        current_flange_zone1=8.5,
        current_flange_zone2=7.0,
        current_mold_zone1=11.5,  # 超过阈值10
        current_mold_zone2=9.0,
        motor_screw_speed=145.0,  # 超过阈值140
        motor_screw_torque=95.0,  # 超过阈值90
        motor_current=58.0,  # 超过阈值55
        motor_traction_speed=4.8,  # 超过阈值4.5
        motor_vacuum_speed=28.0,  # 超过阈值25
        winder_speed=280.0,
        winder_torque=75.0,
        winder_layer_count=45.0,
        winder_tube_speed=12.0,
        winder_tube_count=15.0
    )
    
    # 创建服务实例
    service = SensorDataService()
    
    # 处理传感器数据
    result = service.process_sensor_data(sensor_data)
    
    print(f"处理结果: {result['alarm_count']} 个报警")
    print(f"是否有报警: {result['has_alarms']}")
    
    # 检查报警详情
    if result['alarms']:
        print("\n报警详情:")
        for alarm in result['alarms']:
            print(f"  - {alarm.level.value.upper()}: {alarm.message}")
    
    # 检查数据质量
    if result['quality']:
        print(f"\n数据质量分数: {result['quality']['score']}")
        if result['quality']['issues']:
            print("数据质量问题:")
            for issue in result['quality']['issues']:
                print(f"  - {issue}")
    
    return result


def test_data_transformation():
    """测试数据转换功能"""
    print("\n=== 测试数据转换功能 ===")
    
    # 创建模拟数据
    sensor_data = SensorData(
        timestamp=datetime.now(),
        line_id="line_002",
        component_id="cooler",
        batch_product_number="P-5678",
        current_length=380.0,
        target_length=400.0,
        diameter=4.8,
        fluoride_concentration=1.2,
        temp_body_zone1=160.0,
        temp_body_zone2=165.0,
        temp_body_zone3=170.0,
        temp_body_zone4=175.0,
        temp_flange_zone1=140.0,
        temp_flange_zone2=145.0,
        temp_mold_zone1=150.0,
        temp_mold_zone2=155.0,
        current_body_zone1=8.0,
        current_body_zone2=8.5,
        current_body_zone3=9.0,
        current_body_zone4=8.8,
        current_flange_zone1=6.0,
        current_flange_zone2=6.5,
        current_mold_zone1=7.0,
        current_mold_zone2=7.5,
        motor_screw_speed=120.0,
        motor_screw_torque=70.0,
        motor_current=45.0,
        motor_traction_speed=3.5,
        motor_vacuum_speed=20.0,
        winder_speed=250.0,
        winder_torque=60.0,
        winder_layer_count=35.0,
        winder_tube_speed=10.0,
        winder_tube_count=12.0
    )
    
    # 增强数据
    service = SensorDataService()
    enhanced_data = service.enhance_sensor_data(sensor_data)
    
    # 测试各种转换格式
    transformer = DataTransformer()
    
    # 仪表板格式
    dashboard_format = transformer.to_dashboard_format(enhanced_data)
    print(f"仪表板格式 - 状态: {dashboard_format['status']}")
    print(f"温度统计 - 机体平均: {dashboard_format['temperatures']['body']['average']}°C")
    print(f"电流统计 - 机体总电流: {dashboard_format['currents']['body']['total']}A")
    
    # API格式
    api_format = transformer.to_api_format(enhanced_data)
    print(f"API格式 - 成功: {api_format['success']}")
    
    # MQTT格式
    mqtt_format = transformer.to_mqtt_format(enhanced_data)
    print(f"MQTT格式 - 主题: {mqtt_format['topic']}")
    
    return {
        "dashboard": dashboard_format,
        "api": api_format,
        "mqtt": mqtt_format
    }


def test_utility_functions():
    """测试工具函数"""
    print("\n=== 测试工具函数 ===")
    
    # 测试电机性能分析
    motor_performance = analyze_motor_performance(
        speed=130.0,
        torque=75.0,
        current=50.0,
        max_speed=150.0,
        max_torque=100.0,
        max_current=60.0
    )
    
    print(f"电机性能分析:")
    print(f"  综合效率: {motor_performance['overall_efficiency']}%")
    print(f"  性能评级: {motor_performance['performance_grade']}")
    print(f"  建议:")
    for rec in motor_performance['recommendations']:
        print(f"    - {rec}")
    
    # 测试健康评分
    # 首先需要创建有报警检查功能的数据
    sensor_data = SensorData(
        timestamp=datetime.now(),
        line_id="line_003",
        component_id="winder",
        temp_body_zone1=200.0,  # 超过阈值
        temp_body_zone2=190.0,  # 超过阈值
        temp_body_zone3=180.0,
        temp_body_zone4=175.0,
        temp_flange_zone1=160.0,  # 超过阈值
        temp_flange_zone2=150.0,
        temp_mold_zone1=170.0,  # 超过阈值
        temp_mold_zone2=165.0,  # 超过阈值
        current_body_zone1=15.0,  # 超过阈值
        current_body_zone2=14.0,  # 超过阈值
        current_body_zone3=13.0,  # 超过阈值
        current_body_zone4=12.5,  # 超过阈值
        motor_screw_speed=150.0,  # 超过阈值
        motor_screw_torque=100.0,  # 超过阈值
        motor_current=65.0,  # 超过阈值
        motor_traction_speed=5.5,  # 超过阈值
        motor_vacuum_speed=35.0,  # 超过阈值
        winder_speed=320.0,
        winder_torque=85.0,
        winder_layer_count=48.0,
        winder_tube_speed=14.0,
        winder_tube_count=18.0
    )
    
    # 增强数据
    service = SensorDataService()
    enhanced_data = service.enhance_sensor_data(sensor_data)
    
    # 生成健康评分
    health_score = generate_health_score(enhanced_data)
    
    if "error" not in health_score:
        print(f"\n设备健康评分:")
        print(f"  健康分数: {health_score['health_score']}")
        print(f"  健康评级: {health_score['health_grade']}")
        print(f"  健康状态: {health_score['health_status']}")
        print(f"  报警数量: {health_score['total_alarms']}")
        print(f"  建议:")
        for rec in health_score['recommendations']:
            print(f"    - {rec}")
    else:
        print(f"健康评分错误: {health_score['error']}")
    
    return {
        "motor_performance": motor_performance,
        "health_score": health_score
    }


def test_service_methods():
    """测试服务方法"""
    print("\n=== 测试服务方法 ===")
    
    service = SensorDataService()
    
    # 测试报警统计
    alarm_stats = service.get_alarm_statistics(hours=1)
    print(f"报警统计 (1小时):")
    print(f"  总报警数: {alarm_stats['total_alarms']}")
    print(f"  活跃报警数: {alarm_stats['active_alarms']}")
    
    # 测试活跃报警摘要
    active_summary = service.get_active_alarms_summary()
    print(f"\n活跃报警摘要:")
    print(f"  总活跃报警: {active_summary['total_active']}")
    print(f"  按级别分布: {active_summary['by_level']}")
    print(f"  按类型分布: {active_summary['by_type']}")
    
    return {
        "alarm_stats": alarm_stats,
        "active_summary": active_summary
    }


def main():
    """主测试函数"""
    print("开始测试新的SensorData架构...\n")
    
    try:
        # 运行所有测试
        test_results = {}
        
        # 测试1: 传感器数据增强
        test_results["enhancement"] = test_sensor_data_enhancement()
        
        # 测试2: 数据转换
        test_results["transformation"] = test_data_transformation()
        
        # 测试3: 工具函数
        test_results["utilities"] = test_utility_functions()
        
        # 测试4: 服务方法
        test_results["service"] = test_service_methods()
        
        print("\n=== 测试完成 ===")
        print("✅ 所有测试都成功运行！")
        
        # 输出测试摘要
        print(f"\n测试摘要:")
        print(f"  - 数据增强: {'成功' if 'enhancement' in test_results else '失败'}")
        print(f"  - 数据转换: {'成功' if 'transformation' in test_results else '失败'}")
        print(f"  - 工具函数: {'成功' if 'utilities' in test_results else '失败'}")
        print(f"  - 服务方法: {'成功' if 'service' in test_results else '失败'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 新架构测试成功！")
    else:
        print("\n⚠️  新架构测试失败，请检查相关功能")
