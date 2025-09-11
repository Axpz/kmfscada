from typing import Optional


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