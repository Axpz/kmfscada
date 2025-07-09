'use client'

import React, { useState } from 'react'
import { useCreateProductionData, useUpdateProductionData } from '../hooks'
import type { ProductionData } from '../types'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Textarea } from './ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Alert, AlertDescription } from './ui/alert'
import { Loader2, AlertCircle } from 'lucide-react'

interface ProductionFormProps {
  item?: ProductionData
  onSuccess?: () => void
  onCancel?: () => void
}

export default function ProductionForm({ item, onSuccess, onCancel }: ProductionFormProps) {
  const [formData, setFormData] = useState<Omit<ProductionData, 'id' | 'created_at' | 'updated_at'>>({
    value: item?.value || 0,
    unit: item?.unit || '',
    description: item?.description || '',
  })

  const createMutation = useCreateProductionData()
  const updateMutation = useUpdateProductionData()

  const isEditing = !!item
  const isLoading = isEditing ? updateMutation.isPending : createMutation.isPending
  const error = isEditing ? updateMutation.error : createMutation.error

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      if (isEditing && item?.id) {
        await updateMutation.mutateAsync({ id: item.id, data: formData })
      } else {
        await createMutation.mutateAsync(formData)
      }
      onSuccess?.()
    } catch (error) {
      console.error('Error saving production data:', error)
    }
  }

  const handleChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: field === 'value' ? parseFloat(e.target.value) || 0 : e.target.value,
    }))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {isEditing ? 'Edit Production Data' : 'Add Production Data'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="value">Value</Label>
            <Input
              type="number"
              id="value"
              value={formData.value}
              onChange={handleChange('value')}
              step="0.01"
              required
              placeholder="Enter value"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="unit">Unit</Label>
            <Input
              type="text"
              id="unit"
              value={formData.unit}
              onChange={handleChange('unit')}
              required
              placeholder="e.g., kW, °C, mg/L"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={handleChange('description')}
              rows={3}
              required
              placeholder="Describe the production data..."
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Error saving production data: {error.message}
              </AlertDescription>
            </Alert>
          )}

          <div className="flex justify-end space-x-3">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {isEditing ? 'Updating...' : 'Creating...'}
                </>
              ) : (
                isEditing ? 'Update' : 'Create'
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
} 