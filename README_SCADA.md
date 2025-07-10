# SCADA System - Supabase Auth & Database Integration

这是一个基于 Supabase 的认证和数据库系统，为您的 SCADA 应用提供用户认证和数据库功能。

## 系统架构

### 核心服务

1. **PostgreSQL Database** - 主数据库，支持 Supabase 扩展
2. **Kong API Gateway** - API 网关，处理认证路由
3. **GoTrue Auth** - 用户认证服务

## 快速开始

### 1. 环境配置

```bash
# 复制环境变量文件
cp env.scada.example .env

# 编辑环境变量
nano .env
```

### 2. 启动系统

```bash
# 启动所有服务
docker compose -f docker-compose.scada.yml up -d

# 查看服务状态
docker compose -f docker-compose.scada.yml ps

# 查看日志
docker compose -f docker-compose.scada.yml logs -f
```

### 3. 访问服务

- **API 网关**: http://localhost:8080
- **数据库**: localhost:5432
- **认证服务**: http://localhost:8080/auth/v1/*

## 环境变量说明

### 必需配置

```bash
# 数据库配置
POSTGRES_PASSWORD=your-super-secret-password
JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters-long

# Supabase 密钥
ANON_KEY=your-anon-key
SERVICE_ROLE_KEY=your-service-role-key
```

### 可选配置

```bash
# 认证配置
DISABLE_SIGNUP=false
ENABLE_EMAIL_SIGNUP=true
ENABLE_EMAIL_AUTOCONFIRM=true

# 邮件配置 (可选)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## 服务说明

### 数据库 (PostgreSQL)

- **容器名**: `scada-db`
- **端口**: 5432
- **特点**: 支持 Supabase 扩展，包含认证、实时、存储等功能

### API 网关 (Kong)

- **容器名**: `scada-kong`
- **端口**: 8080 (HTTP), 8443 (HTTPS)
- **功能**: 路由、认证、限流、CORS

### 认证服务 (GoTrue)

- **容器名**: `scada-auth`
- **端口**: 9999 (内部)
- **功能**: 用户注册、登录、JWT 令牌管理

## API 端点

### 认证端点

```
POST /auth/v1/signup          # 用户注册
POST /auth/v1/token           # 用户登录
POST /auth/v1/logout          # 用户登出
GET  /auth/v1/user            # 获取用户信息
POST /auth/v1/user            # 更新用户信息
POST /auth/v1/recover         # 密码恢复
POST /auth/v1/verify          # 邮箱验证
```

### 数据库连接

```bash
# 连接字符串
postgresql://postgres:your-password@localhost:5432/scada
```

## 集成指南

### 前端集成

```javascript
// 使用 Supabase JavaScript 客户端
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'http://localhost:8080',
  'your-anon-key'
)

// 用户注册
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password'
})

// 用户登录
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})
```

### 后端集成

```python
# 使用 Supabase Python 客户端
from supabase import create_client

supabase = create_client(
    'http://localhost:8080',
    'your-service-role-key'
)

# 验证 JWT 令牌
user = supabase.auth.get_user(token)
```

## 数据库管理

### 创建表

```sql
-- 创建用户表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建 RLS 策略
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);
```

### 数据库迁移

```bash
# 使用 Alembic 进行数据库迁移
alembic revision --autogenerate -m "Add users table"
alembic upgrade head
```

## 安全配置

### JWT 配置

```bash
# 生成安全的 JWT 密钥
openssl rand -base64 32

# 设置环境变量
JWT_SECRET=your-generated-secret
JWT_EXPIRY=3600
```

### 数据库安全

```sql
-- 创建只读用户
CREATE USER readonly WITH PASSWORD 'readonly-password';
GRANT CONNECT ON DATABASE scada TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

## 故障排除

### 常见问题

1. **认证服务启动失败**
   ```bash
   # 检查日志
   docker logs scada-auth
   
   # 检查数据库连接
   docker exec -it scada-db pg_isready -U postgres
   ```

2. **JWT 验证失败**
   ```bash
   # 检查 JWT 配置
   docker exec -it scada-auth env | grep GOTRUE_JWT
   
   # 验证密钥长度
   echo $JWT_SECRET | wc -c
   ```

3. **数据库连接问题**
   ```bash
   # 检查数据库状态
   docker exec -it scada-db psql -U postgres -c "SELECT version();"
   
   # 检查用户权限
   docker exec -it scada-db psql -U postgres -c "\du"
   ```

### 重置系统

```bash
# 停止所有服务
docker compose -f docker-compose.scada.yml down

# 删除所有数据
docker compose -f docker-compose.scada.yml down -v --remove-orphans

# 重新启动
docker compose -f docker-compose.scada.yml up -d
```

## 最佳实践

1. **环境隔离**: 使用不同的环境变量文件
2. **版本控制**: 固定 Docker 镜像版本
3. **健康检查**: 所有服务都配置了健康检查
4. **备份策略**: 定期备份数据库
5. **监控**: 监控认证服务的性能和错误

## 许可证

本项目基于 MIT 许可证开源。 