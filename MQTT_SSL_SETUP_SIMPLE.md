# MQTT SSL 简化配置指南

## 概述

本文档描述了简化的MQTT SSL终端配置，使用NGINX代理实现8883端口SSL卸载并转发到RabbitMQ的1883端口。

## 配置特点

✅ **简化架构**: 使用专用NGINX容器替代复杂的Kong配置  
✅ **生产可用**: 支持TLS 1.2/1.3，安全的SSL/TLS配置  
✅ **易于维护**: 去除复杂的初始化脚本，配置清晰直观  
✅ **自动化测试**: 完整的Makefile命令支持  

## 架构图

```
客户端 --[SSL/TLS 8883]--> NGINX代理 --[Plain 1883]--> RabbitMQ MQTT
```

## 文件结构

```
kmfscada/
├── docker-compose.rabbitmq.yml     # RabbitMQ + MQTT SSL代理配置
├── volumes/
│   ├── api/ssl/                    # SSL证书目录
│   │   ├── ca.crt                  # CA根证书
│   │   ├── ca.key                  # CA私钥
│   │   ├── mqtt.crt                # MQTT服务器证书
│   │   └── mqtt.key                # MQTT服务器私钥
│   └── nginx/
│       └── mqtt-ssl.conf           # NGINX配置文件
└── scripts/
    └── test_mqtt_ssl_simple.py     # 测试脚本
```

## 核心配置

### 1. NGINX配置 (`volumes/nginx/mqtt-ssl.conf`)

```nginx
stream {
    upstream mqtt_backend {
        server rabbitmq:1883;
    }
    
    server {
        listen 8883 ssl;
        proxy_pass mqtt_backend;
        
        ssl_certificate /etc/nginx/ssl/mqtt.crt;
        ssl_certificate_key /etc/nginx/ssl/mqtt.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        # ... 其他SSL配置
    }
}
```

### 2. Docker Compose配置 (`docker-compose.rabbitmq.yml`)

```yaml
services:
  rabbitmq:
    # RabbitMQ配置...
    
  mqtt-ssl-proxy:
    image: nginx:alpine
    container_name: mqtt-ssl-proxy
    ports:
      - "8883:8883"
    volumes:
      - ./volumes/api/ssl:/etc/nginx/ssl:ro
      - ./volumes/nginx/mqtt-ssl.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - rabbitmq
```

## 使用方法

### 快速启动

```bash
# 一键设置和测试
make mqtt-ssl-setup

# 或分步操作
make mqtt-ssl    # 启动服务
make test-mqtt-ssl  # 运行测试
make mqtt-ssl-down  # 停止服务
```

### 可用命令

| 命令 | 描述 |
|------|------|
| `make mqtt-ssl-setup` | 完整设置和测试（推荐） |
| `make mqtt-ssl` | 启动MQTT SSL代理 |
| `make mqtt-ssl-down` | 停止MQTT SSL代理 |
| `make mqtt-ssl-logs` | 查看代理日志 |
| `make test-mqtt-ssl` | 运行简单测试 |
| `make test-mqtt-ssl-full` | 运行完整测试 |

## 测试结果

成功运行后，您将看到：

```
🧪 MQTT SSL代理测试
==================================================

1. 测试RabbitMQ MQTT服务:
✅ 普通MQTT连接成功

2. 测试Kong SSL代理:
✅ SSL连接成功
   协议版本: TLSv1.3
   加密套件: ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
✅ MQTT连接建立成功

🎉 所有测试通过！MQTT SSL代理配置正确。
```

## 连接参数

- **SSL端口**: 8883
- **协议**: MQTT 3.1.1 over SSL/TLS
- **认证**: 用户名 `admin`, 密码 `admin123`
- **支持的TLS版本**: TLS 1.2, TLS 1.3

## 证书管理

SSL证书自动生成，有效期365天。如需更新证书：

```bash
# 重新生成证书
cd volumes/api/ssl
rm *.crt *.key
make mqtt-ssl-setup
```

## 生产部署注意事项

1. **使用正式SSL证书**: 生产环境应使用Let's Encrypt或商业SSL证书
2. **定期更新证书**: 设置自动化证书更新
3. **监控和日志**: 配置适当的监控和日志收集
4. **防火墙配置**: 确保8883端口在防火墙中开放

## 故障排除

### 常见问题

1. **连接被拒绝**
   ```bash
   docker ps  # 检查容器状态
   make mqtt-ssl-logs  # 查看日志
   ```

2. **SSL握手失败**
   ```bash
   openssl s_client -connect localhost:8883  # 测试SSL连接
   ```

3. **MQTT认证失败**
   - 确认用户名密码: `admin/admin123`
   - 检查RabbitMQ管理界面: http://localhost:15672

## 与原配置的对比

| 方面 | 原Kong配置 | 新NGINX配置 |
|------|------------|-------------|
| 复杂度 | 高（需要初始化脚本） | 低（直接配置） |
| 启动时间 | 慢（需要等待和检查） | 快（直接启动） |
| 维护性 | 复杂 | 简单 |
| 资源占用 | 高 | 低 |
| 稳定性 | 依赖脚本逻辑 | 原生支持 |

## 总结

简化后的MQTT SSL配置具有以下优势：

- ✅ **配置简单**: 去除了复杂的Kong初始化脚本
- ✅ **稳定可靠**: 使用NGINX原生stream模块，无需动态配置
- ✅ **易于维护**: 清晰的配置文件，便于理解和修改
- ✅ **生产就绪**: 支持现代TLS协议和安全配置
- ✅ **完整测试**: 自动化测试确保配置正确

这个配置满足了您的需求：保持简单、生产可用，并且去掉了不必要的复杂性。
