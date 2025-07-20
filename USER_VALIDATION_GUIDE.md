# 用户验证模型使用指南

## 概述

本项目已经实现了完整的用户数据验证系统，所有涉及用户名、密码和邮箱的 API 端点都使用了 Pydantic 验证模型。

## 验证规则

### 用户名 (Username)
- **长度**: 3-20 个字符
- **字符**: 只能包含字母、数字和下划线 (a-z, A-Z, 0-9, _)
- **可选**: 在大部分场景下是可选的

### 密码 (Password)
- **最小长度**: 6 个字符
- **复杂度**: 必须包含字母和数字
- **示例**: `abc123`, `password1`, `myPass2024`

### 邮箱 (Email)
- **格式**: 使用 `EmailStr` 自动验证标准邮箱格式
- **示例**: `user@example.com`, `test.email@domain.org`

### 角色 (Role)
- **允许值**: `user`, `admin`, `superuser`
- **默认值**: `user`

## 验证模型

### 1. UserSignupValidator
用于用户注册端点 `/auth/signup`
```python
{
    "email": "user@example.com",      # 必填
    "password": "mypass123",          # 必填
    "username": "myusername",         # 可选
    "full_name": "My Full Name"       # 可选
}
```

### 2. UserSigninValidator
用于用户登录端点 `/auth/signin`
```python
{
    "email": "user@example.com",      # 必填
    "password": "mypass123"           # 必填
}
```

### 3. UserCreateValidator
用于管理员创建用户端点 `/users/` (POST)
```python
{
    "email": "user@example.com",      # 必填
    "password": "mypass123",          # 必填
    "username": "myusername",         # 可选
    "full_name": "My Full Name",      # 可选
    "role": "user"                    # 可选，默认 "user"
}
```

### 4. UserUpdateValidator
用于管理员更新用户端点 `/users/{user_id}` (PUT)
```python
{
    "username": "newusername",        # 可选
    "password": "newpass123",         # 可选
    "full_name": "New Full Name",     # 可选
    "role": "admin"                   # 可选
}
```

### 5. UserProfileUpdateValidator
用于用户更新个人资料端点 `/auth/profile` (PUT)
```python
{
    "username": "newusername",        # 可选
    "full_name": "New Full Name"      # 可选
}
```

### 6. RefreshTokenValidator
用于刷新令牌端点 `/auth/refresh` (POST)
```python
{
    "refresh_token": "your_refresh_token_here"  # 必填
}
```

## 代码优化特点

### 1. 消除重复代码
使用 `UserValidatorMixin` 混入类提取公共验证逻辑：
- `validate_username()`: 用户名验证
- `validate_password()`: 密码验证  
- `validate_role()`: 角色验证

### 2. 灵活的验证
- 支持必填和可选字段
- 密码验证支持 `required` 参数控制是否必填
- 所有验证都有清晰的错误消息

### 3. 类型安全
- 使用 Pydantic 提供完整的类型检查
- 自动生成 OpenAPI 文档
- IDE 智能提示支持

## 错误处理

当验证失败时，API 会返回 422 状态码和详细的错误信息：

```json
{
    "detail": [
        {
            "loc": ["body", "username"],
            "msg": "Username must be between 3 and 20 characters",
            "type": "value_error"
        }
    ]
}
```

## 测试

运行测试脚本验证所有验证逻辑：
```bash
python test_user_validation.py
```

## 最佳实践

1. **前端验证**: 在前端也实现相同的验证规则，提供更好的用户体验
2. **错误处理**: 捕获 `ValidationError` 并提供用户友好的错误消息
3. **安全性**: 密码验证只是基础要求，生产环境建议使用更强的密码策略
4. **扩展性**: 需要新的验证规则时，优先在 `UserValidatorMixin` 中添加公共方法

## 相关文件

- `app/schemas/user.py` - 用户验证模型定义
- `app/api/v1/endpoints/auth.py` - 认证相关端点
- `app/api/v1/endpoints/users.py` - 用户管理端点
- `test_user_validation.py` - 验证逻辑测试脚本