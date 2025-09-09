# AlarmRule 报警规则表使用说明

## 🎯 概述

`AlarmRule` 是一个用于存放用户定义的报警规则的数据表，它允许用户为不同的生产线和参数设置自定义的报警阈值，实现灵活的报警管理。

## 🏗️ 表结构

### 核心字段

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| `id` | Integer | 主键，自增 | PRIMARY KEY |
| `line_id` | Text | 生产线ID | NOT NULL, INDEX |
| `parameter_name` | Text | 监控的参数名称 | NOT NULL |
| `lower_limit` | Double | 报警下限值 | NULLABLE |
| `upper_limit` | Double | 报警上限值 | NULLABLE |
| `is_enabled` | Boolean | 规则启用状态 | NOT NULL, DEFAULT TRUE |
| `priority` | Integer | 规则优先级(1-5) | NOT NULL, DEFAULT 3 |
| `description` | Text | 规则描述 | NULLABLE |
| `created_at` | DateTime | 创建时间 | NOT NULL, DEFAULT NOW() |
| `updated_at` | DateTime | 更新时间 | NOT NULL, DEFAULT NOW() |
| `created_by` | Text | 创建者 | NULLABLE |
| `updated_by` | Text | 最后修改者 | NULLABLE |

### 约束和索引

- **唯一约束**: `(line_id, parameter_name)` - 确保同一生产线的同一参数只能有一条规则
- **索引**: 
  - `idx_line_enabled` - 生产线和启用状态组合索引
  - `idx_parameter_enabled` - 参数名和启用状态组合索引
  - `idx_priority_enabled` - 优先级和启用状态组合索引

## 🚀 使用方法

### 1. 创建报警规则

```python
from app.models.alarm_rule import AlarmRule

# 创建温度上限报警规则
temp_rule = AlarmRule(
    line_id="line_001",
    parameter_name="temp_body_zone1",
    lower_limit=None,           # 无下限
    upper_limit=190.0,          # 上限190°C
    priority=2,                 # 优先级2
    description="机体区域1温度上限报警",
    created_by="admin"
)

# 创建温度范围报警规则
range_rule = AlarmRule(
    line_id="line_001",
    parameter_name="diameter",
    lower_limit=4.0,           # 下限4mm
    upper_limit=6.0,           # 上限6mm
    priority=1,                 # 最高优先级
    description="产品直径范围报警",
    created_by="admin"
)
```

### 2. 检查报警触发

```python
# 检查给定值是否触发报警
value = 195.0
is_triggered = temp_rule.is_triggered(value)

if is_triggered:
    # 获取报警消息
    message = temp_rule.get_alarm_message(value)
    # 获取报警级别
    level = temp_rule.get_alarm_level(value)
    
    print(f"报警触发: {message}")
    print(f"报警级别: {level}")
```

### 3. 获取可用参数和生产线

```python
# 获取所有可用的参数名称
parameter_names = AlarmRule.get_parameter_names()
print(f"可用参数: {parameter_names}")

# 获取所有生产线ID
line_ids = AlarmRule.get_line_ids()
print(f"生产线: {line_ids}")
```

### 4. 创建默认规则

```python
# 获取默认的报警规则配置
default_rules = AlarmRule.create_default_rules()

# 这些规则可以用于初始化数据库
for rule_config in default_rules:
    rule = AlarmRule(**rule_config)
    # 保存到数据库
    db.add(rule)
```

## 📊 报警级别说明

报警级别根据偏离程度和优先级自动确定：

- **Critical (严重)**: 偏离 > 20%
- **Error (错误)**: 偏离 > 10%
- **Warning (警告)**: 其他触发情况

## 🔧 数据库操作

### 创建表

运行迁移脚本创建表：

```bash
cd kmfscada
python scripts/create_alarm_rules_table.py
```

### 基本CRUD操作

```python
from sqlalchemy.orm import Session
from app.models.alarm_rule import AlarmRule

# 查询规则
def get_rules_by_line(db: Session, line_id: str):
    return db.query(AlarmRule).filter(
        AlarmRule.line_id == line_id,
        AlarmRule.is_enabled == True
    ).all()

# 创建规则
def create_rule(db: Session, rule_data: dict):
    rule = AlarmRule(**rule_data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

# 更新规则
def update_rule(db: Session, rule_id: int, updates: dict):
    rule = db.query(AlarmRule).filter(AlarmRule.id == rule_id).first()
    if rule:
        for key, value in updates.items():
            setattr(rule, key, value)
        db.commit()
        db.refresh(rule)
    return rule

# 删除规则
def delete_rule(db: Session, rule_id: int):
    rule = db.query(AlarmRule).filter(AlarmRule.id == rule_id).first()
    if rule:
        db.delete(rule)
        db.commit()
        return True
    return False
```

## 📋 参数名称列表

### 生产业务数据
- `current_length` - 当前长度
- `target_length` - 目标长度  
- `diameter` - 直径
- `fluoride_concentration` - 氟化物浓度

### 温度传感器组
- `temp_body_zone1` - 机体区域1温度
- `temp_body_zone2` - 机体区域2温度
- `temp_body_zone3` - 机体区域3温度
- `temp_body_zone4` - 机体区域4温度
- `temp_flange_zone1` - 法兰区域1温度
- `temp_flange_zone2` - 法兰区域2温度
- `temp_mold_zone1` - 模具区域1温度
- `temp_mold_zone2` - 模具区域2温度

### 电流传感器组
- `current_body_zone1` - 机体区域1电流
- `current_body_zone2` - 机体区域2电流
- `current_body_zone3` - 机体区域3电流
- `current_body_zone4` - 机体区域4电流
- `current_flange_zone1` - 法兰区域1电流
- `current_flange_zone2` - 法兰区域2电流
- `current_mold_zone1` - 模具区域1电流
- `current_mold_zone2` - 模具区域2电流

### 电机参数
- `motor_screw_speed` - 螺杆电机速度
- `motor_screw_torque` - 螺杆电机扭矩
- `motor_current` - 主电机电流
- `motor_traction_speed` - 牵引电机速度
- `motor_vacuum_speed` - 真空电机速度

### 收卷机
- `winder_speed` - 收卷速度
- `winder_torque` - 收卷扭矩
- `winder_layer_count` - 层数
- `winder_tube_speed` - 管材速度
- `winder_tube_count` - 管材数量

## 🧪 测试

运行测试脚本验证功能：

```bash
cd kmfscada
python test_alarm_rule.py
```

测试内容包括：
- 规则创建和验证
- 报警触发逻辑
- 参数名称获取
- 生产线ID获取
- 默认规则创建
- 规则序列化

## 💡 最佳实践

### 1. 规则设计原则

- **优先级设置**: 关键参数设置高优先级(1-2)，一般参数设置中等优先级(3-4)
- **阈值设置**: 根据工艺要求和设备规格合理设置阈值
- **描述信息**: 提供清晰的规则描述，便于维护和理解

### 2. 性能优化

- 使用索引优化查询性能
- 批量操作时使用事务
- 定期清理无效规则

### 3. 维护建议

- 定期检查和更新阈值
- 监控规则使用情况
- 备份重要规则配置

## 🔄 集成到现有系统

### 1. 与SensorData集成

```python
from app.models.alarm_rule import AlarmRule
from app.services.alarm_rule_service import AlarmRuleService

# 获取服务实例
service = AlarmRuleService(db)

# 检查传感器数据是否触发报警
sensor_data = get_sensor_data()
alarms = service.check_sensor_data_alarms(sensor_data, sensor_data.line_id)

for alarm in alarms:
    print(f"报警: {alarm['message']}")
    print(f"级别: {alarm['level']}")
```

### 2. 使用服务层的便捷方法

```python
# 批量检查传感器数据
service = AlarmRuleService(db)

# 获取指定生产线的所有规则
line_rules = service.get_rules_by_line("line_001")

# 检查特定参数的规则
param_rules = service.get_rules_by_parameter("temp_body_zone1")

# 获取规则统计信息
stats = service.get_rule_statistics()
print(f"总规则数: {stats['total_rules']}")
print(f"启用规则数: {stats['enabled_rules']}")

# 创建新规则
new_rule_data = {
    "line_id": "line_002",
    "parameter_name": "temp_body_zone1",
    "upper_limit": 180.0,
    "description": "生产线2温度上限报警"
}
rule = service.create_rule(new_rule_data)

# 更新规则
service.update_rule(rule.id, {"upper_limit": 175.0})

# 启用/禁用规则
service.enable_rule(rule.id)
service.disable_rule(rule.id)
```

### 3. 测试服务层功能

```bash
# 测试重构后的服务层
python test_alarm_rule_service.py
```
from app.models.sensor import SensorData
from app.models.alarm_rule import AlarmRule

def check_sensor_data_alarms(sensor_data: SensorData, db: Session):
    """检查传感器数据的报警"""
    # 获取该生产线的所有启用规则
    rules = db.query(AlarmRule).filter(
        AlarmRule.line_id == sensor_data.line_id,
        AlarmRule.is_enabled == True
    ).all()
    
    alarms = []
    for rule in rules:
        # 获取参数值
        value = getattr(sensor_data, rule.parameter_name, None)
        if value is not None and rule.is_triggered(value):
            alarm = {
                "rule_id": rule.id,
                "parameter": rule.parameter_name,
                "value": value,
                "message": rule.get_alarm_message(value),
                "level": rule.get_alarm_level(value),
                "priority": rule.priority
            }
            alarms.append(alarm)
    
    return alarms
```

### 2. 与报警处理器集成

```python
from app.processors.alarm_processor import AlarmProcessor

class EnhancedAlarmProcessor(AlarmProcessor):
    def __init__(self, db_session):
        super().__init__()
        self.db = db_session
    
    def process_with_custom_rules(self, sensor_data: SensorData):
        """使用自定义规则处理报警"""
        # 获取自定义规则
        custom_rules = self.db.query(AlarmRule).filter(
            AlarmRule.line_id == sensor_data.line_id,
            AlarmRule.is_enabled == True
        ).all()
        
        # 检查自定义规则
        for rule in custom_rules:
            value = getattr(sensor_data, rule.parameter_name, None)
            if value is not None and rule.is_triggered(value):
                # 创建报警
                alarm = self._create_alarm_from_rule(rule, value, sensor_data)
                self._process_alarm(alarm)
```

## 📈 扩展功能

### 1. 规则模板

可以创建规则模板，快速应用到多个生产线：

```python
def create_rule_template(template_name: str, rules: list):
    """创建规则模板"""
    template = {
        "name": template_name,
        "rules": rules,
        "created_at": datetime.now(),
        "created_by": "system"
    }
    return template

def apply_template_to_line(template: dict, line_id: str, db: Session):
    """将模板应用到指定生产线"""
    for rule_config in template["rules"]:
        rule_config["line_id"] = line_id
        rule = AlarmRule(**rule_config)
        db.add(rule)
    db.commit()
```

### 2. 规则版本管理

```python
class AlarmRuleVersion(Base):
    """报警规则版本管理"""
    __tablename__ = "alarm_rule_versions"
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey("alarm_rules.id"))
    version = Column(Integer, default=1)
    changes = Column(Text)  # JSON格式的变更记录
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Text)
```

## 🚧 注意事项

1. **数据一致性**: 确保规则参数名与SensorData模型字段名一致
2. **性能考虑**: 大量规则时注意查询性能优化
3. **权限控制**: 考虑添加规则创建和修改的权限控制
4. **审计日志**: 记录规则的创建、修改和删除操作

---

这个报警规则表为你的系统提供了灵活的报警管理能力，可以根据实际需求进行扩展和定制。
