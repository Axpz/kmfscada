import asyncio
import functools
import inspect
from typing import Optional, Callable, Any
from app.core.context import get_request
from app.services.audit_log_service import AuditLogService
from app.db.session import SessionLocal
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_client_ip(request) -> Optional[str]:
    """获取客户端IP地址"""
    if not request:
        return None
    
    headers = getattr(request, "headers", {})
    # 优先从代理头获取真实IP
    ip = headers.get("x-forwarded-for") or headers.get("x-real-ip")
    if ip:
        # 处理多个IP的情况，取第一个
        return ip.split(",")[0].strip()
    
    # 从客户端连接获取
    client = getattr(request, "client", None)
    if client:
        return client.host
    
    return None


def get_user_agent(request) -> Optional[str]:
    """获取用户代理"""
    if not request:
        return None
    
    headers = getattr(request, "headers", {})
    return headers.get("user-agent")


def determine_success(result: Any) -> bool:
    """判断操作是否成功"""
    # 1. 检查是否是HTTP响应
    if hasattr(result, 'status_code'):
        return result.status_code < 400
    
    # 2. 检查是否是Supabase用户对象
    if hasattr(result, 'id') and hasattr(result, 'email'):
        return result.id is not None
    
    # 3. 检查是否是列表（查询操作）
    if isinstance(result, list):
        return True  # 查询操作通常总是成功的
    
    # 4. 检查是否是字典
    if isinstance(result, dict):
        return result.get('id') is not None or result.get('success', True)
    
    # 5. 默认判断
    return result is not None and result is not False


def get_result_summary(result: Any) -> str:
    if isinstance(result, dict) and 'items' in result:
        return f"返回 {len(result.get('items') or [])} 条记录"
    
    if isinstance(result, list):
        return f"返回 {len(result)} 条记录"

    if hasattr(result, 'status_code'):
        return f"状态码: {result.status_code}"
    
    return ""


def audit_log(
    msg: str, 
):
    """
    审计日志装饰器
    
    Args:
        msg: 操作描述消息
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"🔍 审计日志装饰器被调用: {func.__name__}")
            
            request = kwargs.get("request") or get_request()
            user = None

            logger.error("------------------------aaaaaa")
            print(args)
            print(kwargs)
            print("------------------------aaaaaa")
            bound_args = {}
            sig = inspect.signature(func)
            try:
                bound_args = sig.bind_partial(*args, **kwargs).arguments
                logger.info(f"🔍 绑定参数: {list(bound_args.keys())}")
            except Exception as e:
                logger.error(f"🔍 参数绑定失败: {e}")
                bound_args = {}
            
            for k in ("current_user", "user", "supabase_user"):
                if k in bound_args:
                    user = bound_args[k]
                    logger.info(f"🔍 找到用户参数: {k}")
                    break
            
            # 获取用户和网络信息
            email = user.get("email") if user else None
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            logger.info(f"🔍 用户信息: email={email}, ip={ip_address}")
            
            try:
                result = await func(*args, **kwargs)
                
                action = func.__name__
                is_success = determine_success(result)
                
                action_name = f"{action}_success" if is_success else f"{action}_failed"
                
                detail = msg + (get_result_summary(result) if is_success else "操作失败")
                
                asyncio.create_task(
                    _create_audit_log_async(
                        email=email,
                        action=action_name,
                        detail=detail,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                )
                
                return result
                
            except Exception as e:
                # 记录失败的审计日志
                action = func.__name__
                detail = f"{msg}操作失败: {str(e)}"
                
                asyncio.create_task(
                    _create_audit_log_async(
                        email=email,
                        action=f"{action}_failed",
                        detail=detail,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                )
                
                logger.error(f"审计日志记录失败: {e}")
                raise
        
        return wrapper
    return decorator


async def _create_audit_log_async(
    email: Optional[str],
    action: str,
    detail: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """异步创建审计日志"""
    logger.info(f"🔍 开始异步创建审计日志: {action}")
    try:
        db = SessionLocal()
        try:
            audit_service = AuditLogService(db)
            result = audit_service.create_log_entry(
                email=email,
                action=action,
                detail=detail,
                ip_address=ip_address,
                user_agent=user_agent
            )
            logger.info(f"🔍 审计日志创建成功: {result.id if result else 'None'}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"🔍 异步创建审计日志失败: {e}")


# 测试函数
@audit_log("测试操作")
async def test_audit_function():
    """测试审计日志装饰器"""
    logger.info("🔍 测试函数被调用")
    return {"status": "success", "message": "测试成功"}
