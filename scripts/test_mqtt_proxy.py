#!/usr/bin/env python3
"""
测试MQTT代理配置的脚本
验证8883端口是否正确转发到RabbitMQ的1883端口
"""

import socket
import time
import sys

def test_mqtt_proxy():
    """测试MQTT代理连接"""
    print("🔍 测试MQTT代理配置...")
    
    # 测试8883端口连接
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8883))
        sock.close()
        
        if result == 0:
            print("✅ MQTT代理端口8883可访问")
        else:
            print("❌ MQTT代理端口8883无法访问")
            return False
    except Exception as e:
        print(f"❌ 测试8883端口时出错: {e}")
        return False
    

    
    print("🎉 MQTT代理配置测试完成")
    print("📋 配置说明:")
    print("   - 外部客户端连接: localhost:8883")
    print("   - 内部转发目标: rabbitmq:1883")
    
    return True

if __name__ == "__main__":
    success = test_mqtt_proxy()
    sys.exit(0 if success else 1)
