#!/usr/bin/env python3
"""
日志系统测试脚本
用于验证日志配置和功能
"""

import sys
import os
import time
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import (
    init_logging,
    get_logger,
    performance_logger,
    log_security_event,
    log_database_operation,
    log_api_request
)

logger = get_logger(__name__)


def test_basic_logging():
    """测试基本日志功能"""
    print("=== 测试基本日志功能 ===")
        
    logger.debug("这是一条调试信息")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    
    # 测试结构化日志
    logger.info("用户操作", extra={
        "extra_fields": {
            "user_id": "test_user_123",
            "action": "login",
            "ip_address": "192.168.1.100",
            "timestamp": time.time()
        }
    })


def test_performance_logging():
    """测试性能日志功能"""
    print("\n=== 测试性能日志功能 ===")
    
    # 使用上下文管理器
    with performance_logger.time_operation("模拟数据库查询", table="users"):
        time.sleep(0.1)  # 模拟耗时操作
    
    # 使用装饰器
    @performance_logger.log_function_performance("模拟API调用")
    def simulate_api_call():
        time.sleep(0.05)
        return {"status": "success"}
    
    simulate_api_call()


def test_security_logging():
    """测试安全事件日志"""
    print("\n=== 测试安全事件日志 ===")
    
    # 记录登录尝试
    log_security_event(
        event_type="login_attempt",
        user_id="test_user",
        ip_address="192.168.1.100",
        details={
            "method": "password",
            "success": True,
            "user_agent": "Mozilla/5.0"
        }
    )
    
    # 记录可疑活动
    log_security_event(
        event_type="suspicious_activity",
        ip_address="192.168.1.101",
        details={
            "pattern": "sql_injection",
            "query": "SELECT * FROM users WHERE id = 1 OR 1=1"
        },
        severity="WARNING"
    )


def test_database_logging():
    """测试数据库操作日志"""
    print("\n=== 测试数据库操作日志 ===")
    
    log_database_operation(
        operation="SELECT",
        table="users",
        record_id="123",
        user_id="admin",
        details={
            "query": "SELECT * FROM users WHERE id = 123",
            "execution_time_ms": 15.5
        }
    )
    
    log_database_operation(
        operation="INSERT",
        table="users",
        user_id="admin",
        details={
            "query": "INSERT INTO users (email, name) VALUES (?, ?)",
            "affected_rows": 1
        }
    )


def test_api_logging():
    """测试API请求日志"""
    print("\n=== 测试API请求日志 ===")
    
    request_id = str(uuid.uuid4())
    
    log_api_request(
        method="GET",
        path="/api/v1/users",
        status_code=200,
        duration=0.125,
        user_id="test_user",
        request_id=request_id
    )
    
    log_api_request(
        method="POST",
        path="/api/v1/auth/login",
        status_code=401,
        duration=0.050,
        user_id=None,
        request_id=str(uuid.uuid4())
    )


def test_error_logging():
    """测试错误日志"""
    print("\n=== 测试错误日志 ===")
        
    try:
        # 模拟一个异常
        result = 1 / 0
    except Exception as e:
        logger.error("发生了一个异常", extra={
            "extra_fields": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "operation": "division"
            }
        }, exc_info=True)


def main():
    """主测试函数"""
    print("开始测试日志系统...")
    
    # 初始化日志系统
    init_logging()
    
    # 运行各种测试
    test_basic_logging()
    test_performance_logging()
    test_security_logging()
    test_database_logging()
    test_api_logging()
    test_error_logging()
    
    print("\n=== 日志系统测试完成 ===")
    print("请检查以下日志文件:")
    print("- 控制台输出")
    print("- logs/app.log (如果配置了文件日志)")
    print("- logs/error.log (错误日志)")
    print("- logs/security.log (安全事件)")
    print("- logs/performance.log (性能监控)")


if __name__ == "__main__":
    main() 