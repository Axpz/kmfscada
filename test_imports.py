#!/usr/bin/env python3
"""
测试文件 - 用于验证代码跳转功能
在这个文件中测试以下跳转：
1. 将光标放在 settings 上，按 Cmd+Click 或 F12
2. 将光标放在 get_logger 上，按 Cmd+Click 或 F12
3. 将光标放在 SupabaseAuthService 上，按 Cmd+Click 或 F12
"""

from app.core.config import settings
from app.core.logging import get_logger
from app.core.supabase import SupabaseAuthService

# 测试变量
logger = get_logger(__name__)
auth_service = SupabaseAuthService()

print(f"Database URL: {settings.DATABASE_URL}")
print(f"Project Name: {settings.PROJECT_NAME}")
logger.info("Test completed")