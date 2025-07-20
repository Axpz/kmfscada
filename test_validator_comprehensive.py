#!/usr/bin/env python3
"""
简单的用户验证器测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas.user import UserSignupValidator, UserCreateValidator
from pydantic import ValidationError


def test_validators():
    """测试验证器"""
    print("🧪 开始测试验证器...")
    
    # 测试正常数据
    print("\n✅ 测试正常数据:")
    try:
        user = UserSignupValidator(
            email="test@example.com",
            password="abc123",
            username="testuser"
        )
        print(f"   用户创建成功: {user.email}, {user.username}")
    except ValidationError as e:
        print(f"   ❌ 失败: {e}")
    
    # 测试用户名验证
    print("\n🔍 测试用户名验证:")
    
    # 用户名太短
    try:
        UserSignupValidator(
            email="test@example.com", 
            password="abc123",
            username="ab"
        )
        print("   ❌ 短用户名应该失败")
    except ValidationError:
        print("   ✅ 短用户名验证失败 (正确)")
    
    # 用户名包含特殊字符
    try:
        UserSignupValidator(
            email="test@example.com",
            password="abc123", 
            username="test@user"
        )
        print("   ❌ 特殊字符用户名应该失败")
    except ValidationError:
        print("   ✅ 特殊字符用户名验证失败 (正确)")
    
    # 测试密码验证
    print("\n🔒 测试密码验证:")
    
    # 密码太短
    try:
        UserSignupValidator(
            email="test@example.com",
            password="123",
            username="testuser"
        )
        print("   ❌ 短密码应该失败")
    except ValidationError:
        print("   ✅ 短密码验证失败 (正确)")
    
    # 密码只有数字
    try:
        UserSignupValidator(
            email="test@example.com",
            password="123456",
            username="testuser"
        )
        print("   ❌ 纯数字密码应该失败")
    except ValidationError:
        print("   ✅ 纯数字密码验证失败 (正确)")
    
    # 测试邮箱验证
    print("\n📧 测试邮箱验证:")
    try:
        UserSignupValidator(
            email="invalid-email",
            password="abc123",
            username="testuser"
        )
        print("   ❌ 无效邮箱应该失败")
    except ValidationError:
        print("   ✅ 无效邮箱验证失败 (正确)")
    
    # 测试角色验证
    print("\n👤 测试角色验证:")
    try:
        UserCreateValidator(
            email="admin@example.com",
            password="admin123",
            role="admin"
        )
        print("   ✅ 有效角色验证通过")
    except ValidationError as e:
        print(f"   ❌ 有效角色验证失败: {e}")
    
    try:
        UserCreateValidator(
            email="test@example.com",
            password="abc123",
            role="invalid_role"
        )
        print("   ❌ 无效角色应该失败")
    except ValidationError:
        print("   ✅ 无效角色验证失败 (正确)")
    
    print("\n🎉 验证器测试完成!")


if __name__ == "__main__":
    test_validators()