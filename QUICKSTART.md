# KMF SCADA - 快速启动指南

## 项目概述

这是一个基于FastAPI的SCADA系统后端，采用最佳实践架构设计，包含：

- **FastAPI**: 现代、快速的Web框架
- **SQLAlchemy**: ORM和数据库工具
- **Alembic**: 数据库迁移
- **Pydantic**: 数据验证
- **Pytest**: 测试框架
- **PostgreSQL**: 数据库

## 快速开始

### 1. 环境准备

确保你的系统已安装：
- Python 3.12+
- PostgreSQL
- Docker (可选)

### 2. 克隆项目

```bash
git clone <repository-url>
cd kmfscada
```

### 3. 设置环境变量

```bash
cp env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

### 4. 安装依赖

```bash
# 检查Python版本
python scripts/check_python_version.py

# 使用 pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 或使用 make (会自动检查Python版本)
make install
```

### 5. 数据库设置

```bash
# 初始化数据库
make db-init

# 或使用 Alembic 迁移
alembic upgrade head
```

### 6. 启动开发服务器

```bash
# 使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用 make
make dev
```

### 7. 访问应用

- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 使用Docker

### 使用Docker Compose (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用Docker

```bash
# 构建镜像
make docker-build

# 运行容器
make docker-run
```

## 开发工作流

### 代码质量

```bash
# 格式化代码
make format

# 代码检查
make lint

# 运行测试
make test

# 测试覆盖率
make test-cov
```

### 数据库操作

```bash
# 创建迁移
make db-migrate message="描述变更"

# 应用迁移
make db-upgrade

# 回滚迁移
make db-downgrade

# 创建超级用户
make superuser
```

### 清理

```bash
# 清理缓存文件
make clean
```

## API使用示例

### 1. 用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 3. 获取用户信息

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 创建生产数据

```bash
curl -X POST "http://localhost:8000/api/v1/production/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "生产线1",
    "description": "主要生产线",
    "value": 100.5,
    "unit": "kg"
  }'
```

## 项目结构

```
kmfscada/
├── app/                    # 应用主目录
│   ├── api/               # API路由层
│   ├── core/              # 核心配置
│   ├── crud/              # CRUD操作层
│   ├── db/                # 数据库相关
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模式
│   └── services/          # 业务逻辑层
├── tests/                 # 测试目录
├── alembic/               # 数据库迁移
├── scripts/               # 脚本目录
└── docs/                  # 文档
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查PostgreSQL服务是否运行
   - 验证数据库连接字符串
   - 确保数据库用户权限正确

2. **依赖安装失败**
   - 使用虚拟环境
   - 更新pip: `pip install --upgrade pip`
   - 检查Python版本兼容性

3. **测试失败**
   - 确保测试数据库配置正确
   - 检查测试环境变量设置

### 获取帮助

- 查看API文档: http://localhost:8000/docs
- 查看项目README.md
- 检查日志文件

## 下一步

1. 阅读完整的README.md了解详细文档
2. 查看API文档了解所有可用端点
3. 运行测试确保一切正常
4. 开始开发新功能！

---

**注意**: 这是一个开发版本，生产环境部署前请确保：
- 更改默认密码和密钥
- 配置适当的安全设置
- 设置日志记录
- 配置备份策略 