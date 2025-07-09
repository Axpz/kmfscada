# SCADA System - Minimal Setup

一个基于 Supabase Auth 和 FastAPI 的轻量级 SCADA 系统，专注于用户认证和基础功能。

## 架构概览

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │     Kong    │    │   FastAPI   │    │   Supabase  │
│   (Next.js) │───▶│  API Gateway│───▶│   Backend   │───▶│    Auth     │
│   Port 3000 │    │  Port 8080  │    │  Port 8000  │    │  Port 9999  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │                   │
                           ▼                   ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                    │   Frontend  │    │   Database  │    │   Database  │
                    │   (Next.js) │    │ (PostgreSQL)│    │ (PostgreSQL)│
                    │  Port 3000  │    │  Port 5432  │    │  Port 5432  │
                    └─────────────┘    └─────────────┘    └─────────────┘
```

## 统一访问架构

**所有服务都通过 Kong API Gateway 访问：**

- **前端访问**: `http://localhost:8080/` → Kong → Frontend (3000)
- **API 访问**: `http://localhost:8080/api/v1/` → Kong → FastAPI (8000)
- **认证访问**: `http://localhost:8080/auth/v1/` → Kong → Supabase Auth (9999)

## 服务说明

### 1. Kong API Gateway (端口 8080)
- **作用**: 统一入口点，处理路由、CORS、认证
- **路由配置**:
  - `/` → Frontend (Next.js)
  - `/api/v1/*` → FastAPI Backend
  - `/auth/v1/*` → Supabase Auth
- **插件**: CORS, Key Auth, ACL

### 2. Frontend (Next.js)
- **端口**: 3000 (内部)
- **访问**: 通过 Kong 在 8080 端口
- **功能**: 用户界面、认证、仪表板
- **技术栈**: Next.js 14, TypeScript, Tailwind CSS

### 3. FastAPI Backend
- **端口**: 8000 (内部)
- **访问**: 通过 Kong 在 `/api/v1/` 路径
- **功能**: 业务逻辑、用户管理、生产数据
- **认证**: 验证 Supabase JWT Token

### 4. Supabase Auth
- **端口**: 9999 (内部)
- **访问**: 通过 Kong 在 `/auth/v1/` 路径
- **功能**: 用户认证、JWT 令牌管理
- **数据库**: 共享 PostgreSQL

### 5. PostgreSQL Database
- **端口**: 5432
- **作用**: 存储用户数据、生产数据
- **共享**: FastAPI 和 Supabase Auth 共用

## 快速开始

### 1. 环境配置
```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量
nano .env
```

### 2. 启动系统
```bash
# 启动所有服务
docker compose -f docker-compose.scada.yml up -d

# 查看日志
docker compose -f docker-compose.scada.yml logs -f

# 停止服务
docker compose -f docker-compose.scada.yml down
```

### 3. 访问系统
- **前端界面**: http://localhost:8080
- **API 文档**: http://localhost:8080/api/v1/docs
- **健康检查**: http://localhost:8080/health

## 环境变量

```bash
# 数据库配置
POSTGRES_PASSWORD=your-super-secret-password
POSTGRES_DB=scada
POSTGRES_USER=postgres

# JWT 配置
JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters-long
JWT_EXPIRY=3600

# Supabase 配置
SUPABASE_URL=http://localhost:8080
SUPABASE_SERVICE_KEY=your-service-role-key
ANON_KEY=your-anon-key

# API 配置
API_URL=http://localhost:8080
CORS_ORIGINS=http://localhost:8080,http://localhost:3000

# 站点配置
SITE_URL=http://localhost:8080
API_EXTERNAL_URL=http://localhost:8080
```

## 认证流程

1. **用户注册/登录**: 前端调用 Supabase Auth (通过 Kong)
2. **获取 JWT**: Supabase Auth 返回 JWT Token
3. **API 调用**: 前端携带 JWT 调用 FastAPI (通过 Kong)
4. **Token 验证**: FastAPI 验证 JWT 并调用 Supabase Admin API
5. **返回数据**: FastAPI 返回业务数据给前端

## 开发说明

### 前端开发
- 所有 API 调用都通过 Kong (8080 端口)
- 使用 Supabase JS SDK 进行认证
- 使用自定义 API 客户端调用业务接口

### 后端开发
- FastAPI 只处理业务逻辑
- 认证通过验证 Supabase JWT Token
- 数据库操作使用 SQLAlchemy

### 数据库
- 使用标准 PostgreSQL
- Supabase Auth 和 FastAPI 共享数据库
- 通过环境变量配置连接

## 优势

1. **统一入口**: 所有服务通过 Kong 访问，简化客户端配置
2. **安全**: Kong 提供统一的认证和授权
3. **可扩展**: 易于添加新服务和路由
4. **轻量级**: 使用标准 PostgreSQL，避免 Supabase 扩展的复杂性
5. **开发友好**: 清晰的 API 文档和类型定义

## 故障排除

### 常见问题

1. **端口冲突**: 确保 8080 端口未被占用
2. **数据库连接**: 检查 PostgreSQL 服务是否正常启动
3. **认证失败**: 验证 JWT_SECRET 配置
4. **CORS 错误**: 检查 CORS_ORIGINS 配置

### 日志查看
```bash
# 查看所有服务日志
docker compose -f docker-compose.scada.yml logs

# 查看特定服务日志
docker compose -f docker-compose.scada.yml logs api
docker compose -f docker-compose.scada.yml logs frontend
docker compose -f docker-compose.scada.yml logs kong
```

### 重置系统
```bash
# 完全重置（删除所有数据）
docker compose -f docker-compose.scada.yml down -v --remove-orphans
docker compose -f docker-compose.scada.yml up -d
```

## 📝 待实现功能

- [ ] Next.js 前端应用
- [ ] MQTT 数据采集
- [ ] 实时数据推送
- [ ] 数据导出功能
- [ ] 移动端适配
- [ ] 数据可视化图表

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## �� 许可证

MIT License 