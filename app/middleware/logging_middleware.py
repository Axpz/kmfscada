import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import (
    get_logger,
    log_request_info,
    log_api_request,
    log_security_event,
    performance_logger
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件，记录请求信息、性能和安全事件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 记录请求开始
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
                "extra_fields": {
                    "request_start": True
                }
            }
        )
        
        # 设置请求上下文
        log_request_info(request_id)
        
        # 记录安全事件（登录尝试等）
        await self._log_security_events(request, request_id, client_ip)
        
        try:
            # 执行请求
            with performance_logger.time_operation(
                f"HTTP {request.method} {request.url.path}",
                request_id=request_id,
                client_ip=client_ip
            ):
                response = await call_next(request)
            
            # 计算请求持续时间
            duration = time.time() - start_time
            
            # 记录API请求
            user_id = self._extract_user_id(request)
            log_api_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration=duration,
                user_id=user_id,
                request_id=request_id
            )
            
            # 记录请求完成
            self.logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "duration_seconds": round(duration, 3),
                    "client_ip": client_ip,
                    "extra_fields": {
                        "request_completed": True
                    }
                }
            )
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # 记录异常
            duration = time.time() - start_time
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "client_ip": client_ip,
                    "duration_seconds": round(duration, 3),
                    "error": str(e),
                    "extra_fields": {
                        "request_failed": True
                    }
                },
                exc_info=True
            )
            
            # 记录安全事件（异常访问）
            log_security_event(
                event_type="request_exception",
                user_id=self._extract_user_id(request),
                ip_address=client_ip,
                details={
                    "method": request.method,
                    "path": str(request.url.path),
                    "error": str(e),
                    "request_id": request_id
                },
                severity="WARNING"
            )
            
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _extract_user_id(self, request: Request) -> str:
        """从请求中提取用户ID"""
        # 这里可以根据你的认证方式来实现
        # 例如从JWT token中提取用户ID
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # 这里可以解析JWT token获取用户ID
            # 为了简化，这里返回一个占位符
            return "user_from_token"
        return None
    
    async def _log_security_events(self, request: Request, request_id: str, client_ip: str):
        """记录安全相关事件"""
        path = str(request.url.path)
        
        # 记录登录尝试
        if path.endswith("/auth/login") and request.method == "POST":
            log_security_event(
                event_type="login_attempt",
                ip_address=client_ip,
                details={
                    "method": request.method,
                    "path": path,
                    "request_id": request_id
                },
                severity="INFO"
            )
        
        # 记录敏感操作
        sensitive_paths = [
            "/api/v1/users",
            "/api/v1/auth/register",
            "/api/v1/auth/delete-account"
        ]
        
        for sensitive_path in sensitive_paths:
            if path.startswith(sensitive_path):
                log_security_event(
                    event_type="sensitive_operation",
                    user_id=self._extract_user_id(request),
                    ip_address=client_ip,
                    details={
                        "method": request.method,
                        "path": path,
                        "request_id": request_id
                    },
                    severity="INFO"
                )
                break
        
        # 记录可能的攻击尝试
        suspicious_patterns = [
            "admin",
            "password",
            "sql",
            "script",
            "eval(",
            "exec("
        ]
        
        query_string = str(request.query_params)
        for pattern in suspicious_patterns:
            if pattern.lower() in query_string.lower():
                log_security_event(
                    event_type="suspicious_request",
                    user_id=self._extract_user_id(request),
                    ip_address=client_ip,
                    details={
                        "method": request.method,
                        "path": path,
                        "query_string": query_string,
                        "suspicious_pattern": pattern,
                        "request_id": request_id
                    },
                    severity="WARNING"
                )
                break 