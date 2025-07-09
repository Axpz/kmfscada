'use client'

import React from 'react'
import { useAuth } from '../contexts'
import { useProductionData } from '../hooks'
import type { ProductionData } from '../types'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Logo } from './ui/logo'
import { Loader2, LogOut, Activity, CheckCircle, Clock, AlertCircle, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const { user, signOut } = useAuth()
  const { 
    data: productionDataResponse, 
    isLoading, 
    error 
  } = useProductionData()

  const productionData: ProductionData[] = productionDataResponse?.data || []
  const errorMessage = error?.message || productionDataResponse?.error

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h1 className="text-2xl font-bold mb-2">Not Authenticated</h1>
              <p className="text-muted-foreground">Please sign in to access the dashboard.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center gap-4">
              <Logo variant="full" size="lg" />
              <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-muted-foreground">Welcome back, {user.email}</p>
              </div>
            </div>
            <Button
              onClick={handleSignOut}
              variant="outline"
              className="text-destructive hover:text-destructive"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Production</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{productionData.length}</div>
              <p className="text-xs text-muted-foreground">
                Total production entries
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Lines</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {productionData.filter(item => item.value > 0).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Lines with positive values
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Last Update</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {productionData.length > 0
                  ? (() => {
                      const first = productionData[0];
                      const dateStr = first?.updated_at ?? first?.created_at;
                      return dateStr ? new Date(dateStr).toLocaleTimeString() : 'N/A';
                    })()
                  : 'N/A'
                }
              </div>
              <p className="text-xs text-muted-foreground">
                Most recent data update
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Production Data Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Production Data
            </CardTitle>
            <p className="text-sm text-muted-foreground">Real-time production monitoring data</p>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                <p className="mt-2 text-sm text-muted-foreground">Loading production data...</p>
              </div>
            ) : errorMessage ? (
              <div className="flex flex-col items-center justify-center py-8">
                <AlertCircle className="h-8 w-8 text-destructive" />
                <p className="mt-2 text-sm text-muted-foreground">{errorMessage}</p>
              </div>
            ) : productionData.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8">
                <TrendingUp className="h-8 w-8 text-muted-foreground" />
                <p className="mt-2 text-sm text-muted-foreground">No production data available</p>
              </div>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead>
                      <TableHead>Value</TableHead>
                      <TableHead>Unit</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Updated</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {productionData.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.id}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{item.value}</span>
                            <Badge variant={item.value > 0 ? "default" : "secondary"}>
                              {item.value > 0 ? "Active" : "Inactive"}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>{item.unit}</TableCell>
                        <TableCell className="max-w-xs truncate">{item.description}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {(() => {
                              const dateStr = item.updated_at ?? item.created_at;
                              const dateObj = dateStr ? new Date(dateStr) : undefined;
                              return <>
                                <p>{dateObj ? dateObj.toLocaleDateString() : 'N/A'}</p>
                                <p className="text-xs text-muted-foreground">{dateObj ? dateObj.toLocaleTimeString() : 'N/A'}</p>
                              </>;
                            })()}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={item.value > 0 ? "default" : "secondary"}>
                            {item.value > 0 ? "Online" : "Offline"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  )
} 