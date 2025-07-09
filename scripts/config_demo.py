#!/usr/bin/env python3
"""
演示配置类的使用方法
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings, get_settings


def demonstrate_config_loading():
    """演示配置加载过程"""
    print("🔧 配置加载演示")
    print("=" * 50)
    
    # 1. 显示当前配置
    print("📋 当前配置值:")
    print(f"  • DATABASE_URL: {settings.DATABASE_URL}")
    print(f"  • SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"  • JWT_SECRET: {settings.JWT_SECRET[:20]}...")
    print(f"  • ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"  • DEBUG: {settings.DEBUG}")
    print(f"  • CORS_ORIGINS: {settings.CORS_ORIGINS}")
    
    # 2. 检查.env文件
    env_file = project_root / ".env"
    print(f"\n📁 .env文件状态: {'存在' if env_file.exists() else '不存在'}")
    
    if env_file.exists():
        print("📄 .env文件内容预览:")
        with open(env_file, 'r') as f:
            lines = f.readlines()[:10]  # 只显示前10行
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    print(f"    {line.strip()}")
    
    # 3. 环境变量优先级演示
    print("\n🔄 环境变量优先级演示:")
    print("  1. 系统环境变量 (最高优先级)")
    print("  2. .env文件中的变量")
    print("  3. Settings类中的默认值 (最低优先级)")
    
    # 4. 演示如何设置环境变量
    print("\n💡 如何设置环境变量:")
    print("  # 方法1: 在.env文件中设置")
    print("  DATABASE_URL=postgresql://user:pass@host:5432/db")
    print("  ")
    print("  # 方法2: 在系统环境变量中设置")
    print("  export DATABASE_URL=postgresql://user:pass@host:5432/db")
    print("  ")
    print("  # 方法3: 在Docker中设置")
    print("  environment:")
    print("    DATABASE_URL: postgresql://user:pass@host:5432/db")


def demonstrate_settings_usage():
    """演示如何在代码中使用配置"""
    print("\n🔧 配置使用演示")
    print("=" * 50)
    
    # 1. 直接使用settings实例
    print("📋 直接使用settings实例:")
    print(f"  • 数据库URL: {settings.DATABASE_URL}")
    print(f"  • Supabase URL: {settings.SUPABASE_URL}")
    print(f"  • 项目名称: {settings.PROJECT_NAME}")
    print(f"  • API版本: {settings.API_V1_STR}")
    
    # 2. 使用get_settings函数（带缓存）
    print("\n📋 使用get_settings函数（带缓存）:")
    cached_settings = get_settings()
    print(f"  • 环境: {cached_settings.ENVIRONMENT}")
    print(f"  • 调试模式: {cached_settings.DEBUG}")
    print(f"  • 日志级别: {cached_settings.LOG_LEVEL}")
    
    # 3. 配置验证
    print("\n✅ 配置验证:")
    try:
        # 检查必要的配置
        required_configs = [
            'DATABASE_URL',
            'SUPABASE_URL',
            'JWT_SECRET',
            'SUPABASE_SERVICE_KEY'
        ]
        
        for config_name in required_configs:
            value = getattr(settings, config_name)
            if value and value != "your-super-secret-jwt-token-with-at-least-32-characters-long":
                print(f"  ✅ {config_name}: 已配置")
            else:
                print(f"  ⚠️  {config_name}: 使用默认值，建议配置")
                
    except Exception as e:
        print(f"  ❌ 配置验证失败: {e}")


def demonstrate_env_file_creation():
    """演示如何创建.env文件"""
    print("\n📝 .env文件创建演示")
    print("=" * 50)
    
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("📄 创建.env文件...")
        
        # 从env.example复制
        example_file = project_root / "env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ 已从env.example创建.env文件")
            print("💡 请编辑.env文件并设置正确的值")
        else:
            print("❌ env.example文件不存在")
    else:
        print("✅ .env文件已存在")


def main():
    """主函数"""
    print("🚀 配置系统演示")
    print("=" * 60)
    
    # 演示配置加载
    demonstrate_config_loading()
    
    # 演示配置使用
    demonstrate_settings_usage()
    
    # 演示.env文件创建
    demonstrate_env_file_creation()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("\n💡 使用提示:")
    print("  1. 复制 env.example 到 .env")
    print("  2. 编辑 .env 文件设置正确的值")
    print("  3. 重启应用使配置生效")
    print("  4. 使用 settings.配置名 访问配置")


if __name__ == "__main__":
    main() 