# SensorData 新架构设计文档

## 🎯 概述

本文档描述了为 `SensorData` 模型添加处理函数的最佳实践架构。该架构采用分层设计，为传感器数据提供了强大的业务逻辑处理能力，包括报警检查、数据转换、质量验证等功能。

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│           API Layer                 │  ← 控制器层
├─────────────────────────────────────┤
│         Service Layer               │  ← 服务层
├─────────────────────────────────────┤
│       Processor Layer               │  ← 处理器层
├─────────────────────────────────────┤
│         Mixin Layer                 │  ← 模型扩展层
├─────────────────────────────────────┤
│         Model Layer                 │  ← 数据模型层
└─────────────────────────────────────┘
```

### 核心组件

1. **Model Layer**: `SensorData` 基础模型
2. **Mixin Layer**: `SensorDataMixin` 功能扩展
3. **Processor Layer**: 各种业务逻辑处理器
4. **Service Layer**: 业务逻辑协调服务
5. **API Layer**: 接口控制器

## 📁 文件结构

```
app/
├── models/
│   ├── sensor.py                    # 原始SensorData模型
│   └── mixins/
│       ├── __init__.py
│       └── sensor_data_mixin.py     # 功能扩展Mixin
├── processors/
│   ├── __init__.py
│   ├── alarm_processor.py           # 报警处理器
│   └── data_transformer.py          # 数据转换处理器
├── services/
│   ├── __init__.py
│   └── sensor_data_service.py       # 传感器数据服务
└── utils/
    ├── __init__.py
    └── sensor_data_utils.py         # 工具函数
```

## 🔧 核心功能

### 1. 报警处理 (AlarmProcessor)

- **温度报警**: 各区域温度超限检测
- **电流报警**: 电机过载检测
- **生产报警**: 长度、直径偏差检测
- **设备状态报警**: 设备离线、异常检测

**特性:**
- 多级别报警 (INFO, WARNING, ERROR, CRITICAL)
- 报警状态跟踪
- 多种通知渠道 (日志、WebSocket、MQTT)
- 报警统计和趋势分析
- 报警报告导出

### 2. 数据转换 (DataTransformer)

- **仪表板格式**: 转换为前端展示格式
- **报表格式**: 转换为报表数据格式
- **API格式**: 转换为API响应格式
- **MQTT格式**: 转换为MQTT消息格式

**特性:**
- 智能数据聚合
- 统计计算 (平均值、最大值、最小值)
- 效率计算
- 状态评估

### 3. 数据质量验证

- **完整性检查**: 必要字段验证
- **合理性检查**: 数值范围验证
- **一致性检查**: 数据一致性分析
- **质量评分**: 0-100分质量评估

### 4. 性能分析

- **电机性能**: 速度、扭矩、电流效率分析
- **收卷机性能**: 速度、扭矩、层数效率分析
- **生产效率**: 长度完成率、时间效率分析
- **热效率**: 温度控制和能耗分析

## 🚀 使用方法

### 基本使用

```python
from app.services.sensor_data_service import SensorDataService
from app.models.sensor import SensorData

# 创建服务实例
service = SensorDataService()

# 处理传感器数据
result = service.process_sensor_data(sensor_data)

# 获取报警信息
alarms = result['alarms']
alarm_count = result['alarm_count']

# 获取数据质量
quality = result['quality']
quality_score = quality['score']
```

### 数据增强

```python
# 为SensorData添加业务逻辑功能
enhanced_data = service.enhance_sensor_data(sensor_data)

# 检查报警
alarms = enhanced_data.check_all_alarms()

# 验证数据质量
quality = enhanced_data.validate_data_quality()

# 获取数据摘要
summary = enhanced_data.get_summary()
```

### 数据转换

```python
from app.processors.data_transformer import DataTransformer

transformer = DataTransformer()

# 转换为仪表板格式
dashboard_data = transformer.to_dashboard_format(enhanced_data)

# 转换为API格式
api_data = transformer.to_api_format(enhanced_data)

# 转换为MQTT格式
mqtt_data = transformer.to_mqtt_format(enhanced_data)
```

### 报警处理

```python
from app.processors.alarm_processor import AlarmProcessor

processor = AlarmProcessor()

# 处理传感器数据报警
alarms = processor.process_sensor_data(enhanced_data)

# 获取报警统计
stats = processor.get_alarm_statistics(hours=24)

# 获取活跃报警摘要
active_summary = processor.get_active_alarms_summary()

# 导出报警报告
report = processor.export_alarm_report(
    start_time=datetime.now() - timedelta(hours=24),
    end_time=datetime.now(),
    format="json"
)
```

### 工具函数

```python
from app.utils.sensor_data_utils import (
    analyze_motor_performance,
    generate_health_score,
    calculate_data_consistency
)

# 分析电机性能
motor_perf = analyze_motor_performance(
    speed=130.0, torque=75.0, current=50.0,
    max_speed=150.0, max_torque=100.0, max_current=60.0
)

# 生成健康评分
health = generate_health_score(enhanced_data)

# 计算数据一致性
consistency = calculate_data_consistency(
    sensor_data_list, "temp_body_zone1"
)
```

## ⚙️ 配置选项

### 报警阈值配置

```python
# 在 sensor_data_mixin.py 中修改阈值
thresholds = {
    'temp_body_zone1': 190,      # 机体区域1温度阈值
    'temp_body_zone2': 190,      # 机体区域2温度阈值
    'current_body_zone1': 12,    # 机体区域1电流阈值
    'motor_screw_speed': 140,    # 螺杆电机速度阈值
    # ... 更多阈值配置
}
```

### 通知渠道配置

```python
from app.processors.alarm_processor import NotificationChannel, NotificationConfig

# 配置通知渠道
config = NotificationConfig(
    channel=NotificationChannel.EMAIL,
    enabled=True,
    recipients=["admin@company.com"],
    retry_count=3,
    retry_delay=60
)

processor.update_notification_config(NotificationChannel.EMAIL, config)
```

## 🧪 测试

运行测试脚本验证新架构：

```bash
cd kmfscada
python test_new_architecture.py
```

测试内容包括：
- 传感器数据增强功能
- 数据转换功能
- 工具函数功能
- 服务方法功能

## 📊 性能特性

- **懒加载**: 只在需要时计算复杂属性
- **缓存机制**: 缓存计算结果
- **批量处理**: 支持批量数据处理
- **异步处理**: 非阻塞的报警处理

## 🔒 设计原则

1. **单一职责**: 每个类只负责一个特定功能
2. **开闭原则**: 对扩展开放，对修改封闭
3. **依赖注入**: 通过依赖注入降低耦合
4. **接口隔离**: 定义清晰的接口边界
5. **可测试性**: 便于单元测试和集成测试

## 🚧 扩展指南

### 添加新的报警类型

1. 在 `AlarmType` 枚举中添加新类型
2. 在 `SensorDataMixin` 中添加检查方法
3. 在 `AlarmProcessor` 中添加处理逻辑

### 添加新的数据格式

1. 在 `DataTransformer` 中添加转换方法
2. 定义输出格式结构
3. 实现数据聚合和计算逻辑

### 添加新的分析功能

1. 在 `sensor_data_utils.py` 中添加分析函数
2. 在 `SensorDataService` 中集成新功能
3. 更新相关的测试用例

## 📈 未来规划

- [ ] 机器学习异常检测
- [ ] 预测性维护分析
- [ ] 实时性能监控
- [ ] 多设备协同分析
- [ ] 历史数据趋势分析
- [ ] 自动化报告生成

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

---

**注意**: 这是一个完整的架构重构，建议在测试环境中充分验证后再部署到生产环境。
