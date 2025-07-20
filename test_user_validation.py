#!/usr/bin/env python3
"""
测试用户验证模型的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas.user import (
    UserCreateValidator,
    UserUpdateValidator,
    UserSignupValidator,
    UserSigninValidator,
    UserProfileUpdateValidator
)
from pydantic import ValidationError


def test_user_validation():
    """测试用户验证逻辑"""
    print("🧪 开始测试用户验证模型...")
    
    # 测试 UserSignupValidator
    print("\n1. 测试用户注册验证:")
    
    # 正确的数据
    try:
        valid_signup = UserSignupValidator(
            email="test@example.com",
            password="abc123",
            username="testuser",
            full_name="Test User"
        )
        print("✅ 正确数据验证通过")
    except ValidationError as e:
        print(f"❌ 正确数据验证失败: {e}")
    
    # 测试无效的用户名
    try:
        invalid_username = UserSignupValidator(
            email="test@example.com",
            password="abc123",
            username="ab",  # 太短
            full_name="Test User"
        )
        print("❌ 短用户名应该验证失败")
    except ValidationError as e:
        print("✅ 短用户名验证失败 (预期行为)")
    
    # 测试无效的密码
    try:
        invalid_password = UserSignupValidator(
            email="test@example.com",
            password="123",  # 太短且没有字母
            username="testuser",
            full_name="Test User"
        )
        print("❌ 弱密码应该验证失败")
    except ValidationError as e:
        print("✅ 弱密码验证失败 (预期行为)")
    
    # 测试无效的邮箱
    try:
        invalid_email = UserSignupValidator(
            email="invalid-email",  # 无效邮箱格式
            password="abc123",
            username="testuser",
            full_name="Test User"
        )
        print("❌ 无效邮箱应该验证失败")
    except ValidationError as e:
        print("✅ 无效邮箱验证失败 (预期行为)")
    
    # 测试 UserCreateValidator (管理员创建用户)
    print("\n2. 测试管理员创建用户验证:")
    
    try:
        valid_create = UserCreateValidator(
            email="admin@example.com",
            password="admin123",
            username="adminuser",
            role="admin"
        )
        print("✅ 管理员创建用户验证通过")
    except ValidationError as e:
        print(f"❌ 管理员创建用户验证失败: {e}")
    
    # 测试无效角色
    try:
        invalid_role = UserCreateValidator(
            email="test@example.com",
            password="abc123",
            username="testuser",
            role="invalid_role"  # 无效角色
        )
        print("❌ 无效角色应该验证失败")
    except ValidationError as e:
        print("✅ 无效角色验证失败 (预期行为)")
    
    # 测试 UserUpdateValidator
    print("\n3. 测试用户更新验证:")
    
    try:
        valid_update = UserUpdateValidator(
            username="newusername",
            password="newpass123"
        )
        print("✅ 用户更新验证通过")
    except ValidationError as e:
        print(f"❌ 用户更新验证失败: {e}")
    
    # 测试可选字段为空
    try:
        empty_update = UserUpdateValidator()
        print("✅ 空更新验证通过 (所有字段都是可选的)")
    except ValidationError as e:
        print(f"❌ 空更新验证失败: {e}")
    
    print("\n🎉 用户验证模型测试完成!")


if __name__ == "__main__":
    test_user_validation()