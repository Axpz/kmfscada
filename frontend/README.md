# SCADA Frontend

基于 Next.js 13+ App Router 的工业监控和数据采集系统前端。

## 项目结构

```
src/
├── app/                    # Next.js 13+ App Router
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 首页
│   └── globals.css        # 全局样式
├── components/            # React 组件
│   ├── ui/               # 基础 UI 组件 (kebab-case)
│   │   ├── alert.tsx
│   │   ├── avatar.tsx
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── logo.tsx
│   │   ├── sheet.tsx
│   │   ├── table.tsx
│   │   └── textarea.tsx
│   ├── Dashboard.tsx      # 仪表板组件 (PascalCase)
│   ├── LoginForm.tsx      # 登录表单组件
│   ├── ProductionForm.tsx # 生产表单组件
│   ├── UserManagement.tsx # 用户管理组件
│   └── index.ts           # 组件统一导出
├── hooks/                 # 自定义 Hooks (camelCase)
│   ├── useApi.ts         # API 相关 hooks
│   ├── useAuth.ts        # 认证相关 hooks
│   └── index.ts          # Hooks 统一导出
├── lib/                   # 工具库和配置 (camelCase)
│   ├── supabase.ts       # Supabase 配置
│   ├── utils.ts          # 工具函数
│   └── index.ts          # 工具统一导出
├── types/                 # TypeScript 类型定义 (camelCase)
│   └── index.ts          # 统一类型定义
├── contexts/              # React Context (PascalCase)
│   ├── AuthContext.tsx   # 认证上下文
│   └── index.ts          # Context 统一导出
└── providers/             # React Providers (PascalCase)
    ├── QueryProvider.tsx # React Query 提供者
    └── index.ts          # Provider 统一导出
```

## 文件命名规范

### 1. React 组件文件
- **功能组件**: 使用 PascalCase
  - ✅ `Dashboard.tsx`
  - ✅ `LoginForm.tsx`
  - ✅ `UserManagement.tsx`

- **UI 组件**: 使用 kebab-case
  - ✅ `button.tsx`
  - ✅ `dropdown-menu.tsx`
  - ✅ `card.tsx`

### 2. Hooks 文件
- 使用 camelCase，以 `use` 开头
  - ✅ `useApi.ts`
  - ✅ `useAuth.ts`

### 3. 工具和配置文件
- 使用 camelCase
  - ✅ `utils.ts`
  - ✅ `supabase.ts`

### 4. 类型定义文件
- 使用 camelCase
  - ✅ `types.ts`
  - ✅ `index.ts`

### 5. Context 和 Provider 文件
- 使用 PascalCase
  - ✅ `AuthContext.tsx`
  - ✅ `QueryProvider.tsx`

## 导入规范

### 1. 相对路径导入
使用相对路径导入，避免使用 `@/` 别名：

```tsx
// ✅ 正确的导入方式
import { useAuth } from '../contexts'
import { useApi } from '../hooks'
import { Button } from './ui/button'

// ❌ 避免使用别名
import { useAuth } from '@/contexts/AuthContext'
import { useApi } from '@/hooks/useApi'
```

### 2. 索引文件导入
通过索引文件统一导入：

```tsx
// ✅ 使用索引文件导入
import { Dashboard, LoginForm } from '../components'
import { useAuth, useApi } from '../hooks'
import { supabase, utils } from '../lib'
```

## 类型定义

所有类型定义集中在 `src/types/index.ts` 中：

```tsx
// 用户相关类型
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

// 生产相关类型
export interface ProductionData {
  id?: string;
  value: number;
  unit: string;
  description: string;
  created_at?: string;
  updated_at?: string;
}

// API 响应类型
export interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
  success: boolean;
}
```

## 开发指南

### 1. 添加新组件
1. 在 `src/components/` 目录下创建新文件
2. 使用 PascalCase 命名
3. 在 `src/components/index.ts` 中导出

### 2. 添加新 Hook
1. 在 `src/hooks/` 目录下创建新文件
2. 使用 camelCase 命名，以 `use` 开头
3. 在 `src/hooks/index.ts` 中导出

### 3. 添加新类型
1. 在 `src/types/index.ts` 中添加类型定义
2. 使用 PascalCase 命名接口和类型

### 4. 添加新 UI 组件
1. 在 `src/components/ui/` 目录下创建新文件
2. 使用 kebab-case 命名
3. 在 `src/components/index.ts` 中导出

## 技术栈

- **框架**: Next.js 13+ (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: React Query + Context API
- **认证**: Supabase Auth
- **UI 组件**: 自定义组件库
- **图标**: Lucide React

## 运行项目

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 启动生产版本
npm start
```

## 环境变量

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
``` 