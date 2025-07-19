import logging
import logging.config
import sys
import json
from datetime import datetime, UTC
from typing import Any, Dict, Optional
from pathlib import Path
import traceback
from contextlib import contextmanager
import time
import uuid
from functools import wraps

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器，输出JSON格式的日志"""
    
    def format(self, record: logging.LogRecord) -> str:
        # 创建结构化日志记录
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 添加额外字段
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # 添加请求ID（如果存在）
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        # 添加用户信息（如果存在）
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """彩色控制台日志格式化器，用于开发环境"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # 添加颜色
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # 格式化消息
        formatted = super().format(record)
        
        # 添加颜色前缀
        return f"{color}{formatted}{reset}"


class RequestIdFilter(logging.Filter):
    """为日志记录添加请求ID的过滤器"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.request_id = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        if self.request_id:
            record.request_id = self.request_id
        return True


class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    @contextmanager
    def time_operation(self, operation_name: str, **kwargs):
        """记录操作执行时间的上下文管理器"""
        start_time = time.time()
        operation_id = str(uuid.uuid4())
        
        self.logger.info(
            f"Starting operation: {operation_name}",
            extra={
                'operation_name': operation_name,
                'operation_id': operation_id,
                'extra_fields': kwargs
            }
        )
        
        try:
            yield operation_id
        except Exception as e:
            self.logger.error(
                f"Operation failed: {operation_name}",
                extra={
                    'operation_name': operation_name,
                    'operation_id': operation_id,
                    'error': str(e),
                    'extra_fields': kwargs
                },
                exc_info=True
            )
            raise
        finally:
            duration = time.time() - start_time
            self.logger.info(
                f"Operation completed: {operation_name}",
                extra={
                    'operation_name': operation_name,
                    'operation_id': operation_id,
                    'duration_seconds': round(duration, 3),
                    'extra_fields': kwargs
                }
            )
    
    def log_function_performance(self, operation_name: str = None):
        """装饰器：记录函数执行性能"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                with self.time_operation(op_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


def setup_logging(
    log_level: str = None,
    log_format: str = "json",
    log_file: str = None,
    enable_console: bool = True
) -> None:
    """设置日志配置"""
    
    if log_level is None:
        log_level = settings.LOG_LEVEL
    
    # 创建日志目录
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        if settings.ENVIRONMENT == "development":
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s'
            )
        else:
            console_formatter = StructuredFormatter()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # 创建应用日志记录器
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 添加请求ID过滤器
    request_filter = RequestIdFilter()
    app_logger.addFilter(request_filter)
    
    return app_logger


def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    if name is None:
        name = "app"
    return logging.getLogger(name)


def log_request_info(request_id: str, user_id: str = None):
    """为当前请求设置日志上下文"""
    logger = get_logger()
    
    # 设置请求ID过滤器
    for handler in logger.handlers:
        for filter_obj in handler.filters:
            if isinstance(filter_obj, RequestIdFilter):
                filter_obj.request_id = request_id
                break
    
    # 为所有日志记录添加用户ID
    if user_id:
        logger = logging.getLogger()
        for handler in logger.handlers:
            handler.addFilter(lambda record: setattr(record, 'user_id', user_id) or True)


def log_security_event(
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    details: Dict[str, Any] = None,
    severity: str = "INFO"
):
    """记录安全事件"""
    logger = get_logger("security")
    
    extra_fields = {
        "event_type": event_type,
        "security_event": True,
        "ip_address": ip_address,
        "details": details or {}
    }
    
    if user_id:
        extra_fields["user_id"] = user_id
    
    log_method = getattr(logger, severity.lower())
    log_method(
        f"Security event: {event_type}",
        extra={"extra_fields": extra_fields}
    )


def log_database_operation(
    operation: str,
    table: str = None,
    record_id: str = None,
    user_id: str = None,
    details: Dict[str, Any] = None
):
    """记录数据库操作"""
    logger = get_logger("database")
    
    extra_fields = {
        "operation": operation,
        "table": table,
        "record_id": record_id,
        "database_operation": True,
        "details": details or {}
    }
    
    if user_id:
        extra_fields["user_id"] = user_id
    
    logger.info(
        f"Database operation: {operation}",
        extra={"extra_fields": extra_fields}
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    request_id: str = None
):
    """记录API请求"""
    logger = get_logger("api")
    
    extra_fields = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
        "api_request": True
    }
    
    if user_id:
        extra_fields["user_id"] = user_id
    
    if request_id:
        extra_fields["request_id"] = request_id
    
    # 根据状态码选择日志级别
    if status_code >= 500:
        log_level = "error"
    elif status_code >= 400:
        log_level = "warning"
    else:
        log_level = "info"
    
    log_method = getattr(logger, log_level)
    log_method(
        f"API {method} {path} - {status_code}",
        extra={"extra_fields": extra_fields}
    )


# 初始化日志系统
def init_logging():
    """初始化日志系统"""
    log_file = None
    if settings.ENVIRONMENT == "production":
        log_file = "logs/app.log"
    elif settings.ENVIRONMENT == "staging":
        log_file = "logs/staging.log"
    else:
        # 开发环境也创建文件日志用于测试
        log_file = "logs/dev.log"
    
    return setup_logging(
        log_level=settings.LOG_LEVEL,
        log_format="json" if settings.ENVIRONMENT != "development" else "colored",
        log_file=log_file,
        enable_console=True
    )


# 创建性能日志记录器实例
performance_logger = PerformanceLogger(get_logger("performance")) 