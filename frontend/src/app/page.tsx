'use client'

import React, { useState } from 'react'
import { useAuth } from '../contexts'
import LoginForm from '../components/LoginForm'
import Dashboard from '../components/Dashboard'
import UserManagement from '../components/UserManagement'
import ProductionForm from '../components/ProductionForm'
import ScadaWorkshopDashboard from '../components/ScadaWorkshopDashboard'

type TabType = 'dashboard' | 'users' | 'add-production' | 'workshop'

export default function Home() {
  const { user, loading } = useAuth()
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [showAddForm, setShowAddForm] = useState(false)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <LoginForm />
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'users':
        return <UserManagement />
      case 'add-production':
        return (
          <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <ProductionForm 
              onSuccess={() => {
                setShowAddForm(false)
                setActiveTab('dashboard')
              }}
              onCancel={() => {
                setShowAddForm(false)
                setActiveTab('dashboard')
              }}
            />
          </div>
        )
      case 'workshop':
        return <ScadaWorkshopDashboard />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">SCADA System</h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`${
                    activeTab === 'dashboard'
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab('workshop')}
                  className={`${
                    activeTab === 'workshop'
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
                >
                  车间大屏
                </button>
                <button
                  onClick={() => setActiveTab('users')}
                  className={`${
                    activeTab === 'users'
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
                >
                  Users
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => {
                  setShowAddForm(true)
                  setActiveTab('add-production')
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Add Production Data
              </button>
              <span className="text-gray-700 text-sm">{user.email}</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      {renderTabContent()}
    </div>
  )
} 