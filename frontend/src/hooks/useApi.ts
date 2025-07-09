import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

// Import types from types module
import type { ProductionData, User } from '../types'

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
})

// Add auth interceptor
apiClient.interceptors.request.use(async (config) => {
  // Get session from Supabase
  const { data: { session } } = await import('../lib').then(m => m.supabase.auth.getSession())
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

export function useProductionData() {
  return useQuery({
    queryKey: ['production-data'],
    queryFn: async () => {
      const response = await apiClient.get('/production')
      return response.data
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await apiClient.get('/users')
      return response.data
    },
  })
}

export function useCreateProductionData() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: Omit<ProductionData, 'id' | 'created_at' | 'updated_at'>) => {
      const response = await apiClient.post('/production', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['production-data'] })
    },
  })
}

export function useUpdateProductionData() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Omit<ProductionData, 'id' | 'created_at' | 'updated_at'> }) => {
      const response = await apiClient.put(`/production/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['production-data'] })
    },
  })
} 