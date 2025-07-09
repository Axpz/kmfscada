# Next.js 文件命名规范

## 目录结构规范

```
src/
├── app/                    # Next.js 13+ App Router
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 首页
│   └── globals.css        # 全局样式
├── components/            # React 组件
│   ├── ui/               # 基础 UI 组件 (kebab-case)
│   └── [feature]/        # 功能组件 (PascalCase)
├── hooks/                # 自定义 Hooks (camelCase)
├── lib/                  # 工具库和配置 (camelCase)
├── types/                # TypeScript 类型定义 (camelCase)
├── contexts/             # React Context (PascalCase)
└── providers/            # React Providers (PascalCase)
```

## 文件命名规则

### 1. React 组件文件
- **功能组件**: 使用 PascalCase
  - ✅ `Dashboard.tsx`
  - ✅ `LoginForm.tsx`
  - ✅ `UserManagement.tsx`
  - ❌ `dashboard.tsx`
  - ❌ `login-form.tsx`

- **UI 组件**: 使用 kebab-case
  - ✅ `button.tsx`
  - ✅ `dropdown-menu.tsx`
  - ✅ `card.tsx`
  - ❌ `Button.tsx`
  - ❌ `DropdownMenu.tsx`

### 2. Hooks 文件
- 使用 camelCase，以 `use` 开头
  - ✅ `useApi.ts`
  - ✅ `useAuth.ts`
  - ✅ `useLocalStorage.ts`
  - ❌ `UseApi.ts`
  - ❌ `use-api.ts`

### 3. 工具和配置文件
- 使用 camelCase
  - ✅ `utils.ts`
  - ✅ `supabase.ts`
  - ✅ `constants.ts`
  - ❌ `Utils.ts`
  - ❌ `utils.tsx`

### 4. 类型定义文件
- 使用 camelCase
  - ✅ `types.ts`
  - ✅ `api.types.ts`
  - ✅ `user.types.ts`
  - ❌ `Types.ts`
  - ❌ `types.tsx`

### 5. Context 和 Provider 文件
- 使用 PascalCase
  - ✅ `AuthContext.tsx`
  - ✅ `QueryProvider.tsx`
  - ✅ `ThemeProvider.tsx`
  - ❌ `authContext.tsx`
  - ❌ `query-provider.tsx`

### 6. Next.js App Router 文件
- 使用 Next.js 约定
  - ✅ `layout.tsx`
  - ✅ `page.tsx`
  - ✅ `loading.tsx`
  - ✅ `error.tsx`
  - ✅ `not-found.tsx`

## 组件命名规则

### 1. 组件名称
- 使用 PascalCase
- 描述性名称
- 避免缩写

```tsx
// ✅ 好的命名
export function UserProfile() { }
export function ProductionDashboard() { }
export function LoginForm() { }

// ❌ 不好的命名
export function UP() { }
export function ProdDash() { }
export function Login() { }
```

### 2. Props 接口命名
- 使用 PascalCase + Props 后缀
- 或者使用 ComponentName + Props

```tsx
// ✅ 好的命名
interface UserProfileProps {
  userId: string;
  onUpdate: (data: UserData) => void;
}

interface LoginFormProps {
  onSubmit: (credentials: Credentials) => void;
}
```

### 3. 类型定义命名
- 使用 PascalCase
- 描述性名称

```tsx
// ✅ 好的命名
interface User {
  id: string;
  name: string;
  email: string;
}

type ApiResponse<T> = {
  data: T;
  status: number;
  message: string;
};
```

## 导入/导出规范

### 1. 默认导出
- 组件文件使用默认导出
- 工具文件使用命名导出

```tsx
// components/Dashboard.tsx
export default function Dashboard() {
  // ...
}

// lib/utils.ts
export function formatDate(date: Date): string {
  // ...
}
```

### 2. 索引文件
- 在目录根目录创建 `index.ts` 文件
- 统一导出该目录下的所有组件

```tsx
// components/index.ts
export { default as Dashboard } from './Dashboard';
export { default as LoginForm } from './LoginForm';
export { default as UserManagement } from './UserManagement';
```

## 文件组织原则

1. **单一职责**: 每个文件只负责一个功能
2. **就近原则**: 相关文件放在同一目录
3. **可扩展性**: 目录结构支持功能扩展
4. **可维护性**: 清晰的命名和结构便于维护

## 迁移指南

1. 重命名文件时保持功能不变
2. 更新所有导入路径
3. 确保 TypeScript 类型正确
4. 运行测试确保功能正常 