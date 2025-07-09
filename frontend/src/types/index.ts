// 用户相关类型
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export type UserRole = 'admin' | 'user' | 'operator';

// 认证相关类型
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
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

export type ProductionStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

// API 响应类型
export interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// 表单相关类型
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea';
  required?: boolean;
  options?: { value: string; label: string }[];
  placeholder?: string;
}

// 分页类型
export interface PaginationParams {
  page: number;
  limit: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// 仪表板数据类型
export interface DashboardStats {
  total_users: number;
  total_productions: number;
  today_productions: number;
  pending_productions: number;
}

// 通用类型
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface SelectOption {
  value: string;
  label: string;
} 