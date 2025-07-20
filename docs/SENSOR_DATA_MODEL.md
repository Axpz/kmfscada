# 传感器数据模型

本文档描述了KMF SCADA系统中的传感器数据模型，包括数据模型定义、CRUD操作、API端点和测试方法。

## 数据模型

### SensorReading 模型

```python
class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(BigInteger, primary_key=True, index=True)
    sensor_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    location = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True, default={})
```

### 字段说明

- `id`: 主键，自增的BigInteger类型
- `sensor_id`: 传感器ID，字符串类型，必填，有索引
- `timestamp`: 时间戳，带时区的DateTime类型，默认为当前时间，有索引
- `value`: 传感器数值，Float类型，必填
- `unit`: 单位，字符串类型，可选
- `location`: 位置，字符串类型，可选
- `metadata`: 元数据，JSON类型，可选，默认为空对象

## CRUD 操作

### 基本操作

传感器数据模型支持完整的CRUD操作：

- **Create**: 创建新的传感器读数
- **Read**: 读取传感器读数（按ID、传感器ID、位置等）
- **Update**: 更新传感器读数
- **Delete**: 删除传感器读数

### 高级查询

还提供了一些高级查询功能：

- 按传感器ID查询最新读数
- 按位置查询读数
- 查询最近N小时的读数
- 计算传感器在指定时间段内的平均值
- 获取传感器在指定时间段内的统计信息（平均值、最小值、最大值、计数）

## API 端点

### 基本CRUD端点

- `GET /api/v1/sensor/` - 获取传感器读数列表
- `POST /api/v1/sensor/` - 创建新的传感器读数
- `GET /api/v1/sensor/{id}` - 获取指定ID的传感器读数
- `PUT /api/v1/sensor/{id}` - 更新指定ID的传感器读数
- `DELETE /api/v1/sensor/{id}` - 删除指定ID的传感器读数

### 查询端点

- `GET /api/v1/sensor/sensor/{sensor_id}` - 按传感器ID查询读数
- `GET /api/v1/sensor/sensor/{sensor_id}/latest` - 获取传感器的最新读数
- `GET /api/v1/sensor/location/{location}` - 按位置查询读数
- `GET /api/v1/sensor/recent/` - 查询最近的读数（可指定小时数）

### 统计端点

- `GET /api/v1/sensor/sensor/{sensor_id}/average` - 获取传感器的平均值
- `GET /api/v1/sensor/sensor/{sensor_id}/statistics` - 获取传感器的统计信息

## 使用示例

### 创建传感器读数

```python
from app.schemas.sensor import SensorReadingCreate
from app.crud.crud_sensor import sensor_reading

# 创建传感器读数
sensor_data = SensorReadingCreate(
    sensor_id="temp_sensor_001",
    value=25.5,
    unit="°C",
    location="workshop",
    metadata={"source": "manual", "operator": "john"}
)

# 保存到数据库
db = SessionLocal()
reading = sensor_reading.create(db=db, obj_in=sensor_data)
db.close()
```

### 查询传感器读数

```python
# 获取传感器的最新读数
latest = sensor_reading.get_latest_by_sensor_id(db=db, sensor_id="temp_sensor_001")

# 获取传感器的统计信息
stats = sensor_reading.get_statistics_by_sensor_id(db=db, sensor_id="temp_sensor_001", hours=24)
```

### API调用示例

```bash
# 创建传感器读数
curl -X POST "http://localhost:8000/api/v1/sensor/" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "temp_sensor_001",
    "value": 25.5,
    "unit": "°C",
    "location": "workshop"
  }'

# 获取传感器的最新读数
curl "http://localhost:8000/api/v1/sensor/sensor/temp_sensor_001/latest"

# 获取传感器的统计信息
curl "http://localhost:8000/api/v1/sensor/sensor/temp_sensor_001/statistics?hours=24"
```

## 测试

### 运行CRUD测试

```bash
make test-sensor-crud
```

这个测试会验证所有的CRUD操作和高级查询功能。

### 运行数据插入测试

```bash
make test-sensor-data
```

这个测试会每秒插入一条模拟的传感器数据，用于测试数据插入功能。

### 手动运行测试

```bash
# CRUD测试
python scripts/test_sensor_crud.py

# 数据插入测试（连续运行）
python scripts/test_sensor_data.py
```

## 数据库迁移

### 创建迁移

```bash
make db-migrate message="create sensor readings table"
```

### 应用迁移

```bash
make db-upgrade
```

### 回滚迁移

```bash
make db-downgrade
```

## 注意事项

1. **性能考虑**: 对于高频数据插入，建议使用批量插入或异步处理
2. **数据清理**: 定期清理旧数据以保持数据库性能
3. **索引优化**: 已为常用查询字段创建了索引
4. **时区处理**: 时间戳使用UTC时区存储，显示时可根据需要转换

## 扩展功能

可以考虑添加以下扩展功能：

1. **数据压缩**: 对于历史数据使用TimescaleDB的压缩功能
2. **数据聚合**: 自动计算小时、天、月的聚合数据
3. **告警功能**: 基于传感器数值的告警机制
4. **数据验证**: 添加数据范围验证和异常检测
5. **实时推送**: 使用WebSocket推送实时数据更新 