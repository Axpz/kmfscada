#!/usr/bin/env python3
"""
用户测试运行器
User Test Runner

运行所有用户相关的测试，包括：
- 用户模式验证测试
- 认证端点测试  
- 用户管理端点测试
- Supabase认证服务测试

Run all user-related tests including:
- User schema validation tests
- Authentication endpoint tests
- User management endpoint tests
- Supabase auth service tests
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """运行用户测试 / Run user tests"""
    print("🧪 开始运行用户功能综合测试...")
    print("🧪 Starting comprehensive user functionality tests...")
    print("=" * 60)
    
    # 确保在正确的目录中
    # Ensure we're in the correct directory
    os.chdir(Path(__file__).parent)
    
    # 运行测试
    # Run tests
    try:
        # 运行用户核心测试
        # Run user core tests
        print("\n📋 运行用户核心测试 / Running user core tests...")
        result1 = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_user_core.py",
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=False)
        
        # 运行用户综合测试
        # Run comprehensive user tests
        print("\n📋 运行用户综合测试 / Running comprehensive user tests...")
        result2 = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_users_comprehensive.py",
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=False)
        
        if result1.returncode == 0 and result2.returncode == 0:
            print("\n✅ 所有用户测试通过！/ All user tests passed!")
        else:
            print("\n❌ 部分用户测试失败 / Some user tests failed")
            return False
            
        # 可选：运行现有的验证测试
        # Optional: Run existing validation tests
        print("\n📋 运行现有验证测试 / Running existing validation tests...")
        if os.path.exists("test_user_validation.py"):
            result2 = subprocess.run([
                sys.executable, "test_user_validation.py"
            ], capture_output=False)
            
            if result2.returncode != 0:
                print("⚠️  现有验证测试有问题 / Issues with existing validation tests")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试运行出错 / Error running tests: {e}")
        return False


def main():
    """主函数 / Main function"""
    print("🚀 用户功能测试套件 / User Functionality Test Suite")
    print("=" * 60)
    
    success = run_tests()
    
    if success:
        print("\n🎉 测试完成！/ Tests completed!")
        print("📊 测试覆盖了以下功能 / Test coverage includes:")
        print("   • 用户模式验证 / User schema validation")
        print("   • 用户注册和登录 / User signup and signin")
        print("   • 令牌验证和刷新 / Token verification and refresh")
        print("   • 用户资料更新 / User profile updates")
        print("   • 管理员用户管理 / Admin user management")
        print("   • Supabase认证服务 / Supabase auth service")
        sys.exit(0)
    else:
        print("\n💥 测试失败，请检查错误信息 / Tests failed, please check error messages")
        sys.exit(1)


if __name__ == "__main__":
    main()