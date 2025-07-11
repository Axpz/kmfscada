### 1. 结构化日志
- JSON格式输出，便于日志分析
- 开发环境使用彩色控制台输出
- 生产环境使用结构化JSON格式

### 2. 性能监控
- 自动记录API请求性能
- 函数执行时间监控
- 数据库操作性能跟踪

### 3. 安全事件记录
- 登录尝试记录
- 敏感操作监控
- 可疑请求检测

### 4. 请求追踪
- 每个请求分配唯一ID
- 完整的请求生命周期记录
- 用户行为追踪

## 使用方法

### 基本日志记录

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# 基本日志
logger.info("用户登录成功")
logger.warning("数据库连接超时")
logger.error("API调用失败", exc_info=True)

# 结构化日志
logger.info("处理用户请求", extra={
    "extra_fields": {
        "user_id": "123",
        "action": "login",
        "ip_address": "192.168.1.1"
    }
})
```

### 性能监控

```python
from app.core.logging import performance_logger

# 使用上下文管理器
with performance_logger.time_operation("数据库查询", table="users"):
    # 执行数据库操作
    result = db.query(User).all()

# 使用装饰器
@performance_logger.log_function_performance("用户认证")
def authenticate_user(user_id: str):
    # 认证逻辑
    pass
```

### 安全事件记录

```python
from app.core.logging import log_security_event

# 记录登录尝试
log_security_event(
    event_type="login_attempt",
    user_id="user123",
    ip_address="192.168.1.1",
    details={"method": "password", "success": True}
)

# 记录可疑活动
log_security_event(
    event_type="suspicious_activity",
    ip_address="192.168.1.1",
    details={"pattern": "sql_injection", "query": "SELECT * FROM users"},
    severity="WARNING"
)
```

### 数据库操作记录

```python
from app.core.logging import log_database_operation

# 记录数据库操作
log_database_operation(
    operation="SELECT",
    table="users",
    record_id="123",
    user_id="admin",
    details={"query": "SELECT * FROM users WHERE id = 123"}
)
```

## 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息，如请求处理、用户操作
- **WARNING**: 警告信息，如性能问题、配置问题
- **ERROR**: 错误信息，如异常、失败操作
- **CRITICAL**: 严重错误，如系统崩溃

## 环境配置

### 开发环境
- 彩色控制台输出
- 详细调试信息
- 本地文件日志

### 生产环境
- JSON结构化日志
- 日志文件轮转
- 错误日志分离
- 性能监控

### 测试环境
- 简化日志格式
- 关键信息记录
- 性能基准测试

## 日志文件

- `logs/app.log`: 应用主日志
- `logs/error.log`: 错误日志
- `logs/security.log`: 安全事件日志
- `logs/performance.log`: 性能监控日志
