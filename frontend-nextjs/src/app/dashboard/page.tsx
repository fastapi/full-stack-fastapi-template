"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Users, Package, Settings, Activity, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import { usersReadUsers, usersReadUserMe, itemsReadItems, utilsHealthCheck } from "@/lib/api-client"
import type { UserPublic, ItemPublic } from "@/lib/api-client"

interface DashboardData {
  users: UserPublic[]
  items: ItemPublic[]
  currentUser: UserPublic | null
  systemHealth: boolean
}

interface DashboardState {
  data: DashboardData | null
  loading: boolean
  error: string | null
}

export default function DashboardPage() {
  const [state, setState] = useState<DashboardState>({
    data: null,
    loading: true,
    error: null
  })

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }))
        
        // Get auth token from localStorage
        const token = localStorage.getItem('access_token')
        if (!token) {
          throw new Error('No authentication token found')
        }

        // Fetch data in parallel
        const [usersResponse, itemsResponse, currentUserResponse, healthResponse] = await Promise.allSettled([
          usersReadUsers({
            headers: { Authorization: `Bearer ${token}` }
          }),
          itemsReadItems({
            headers: { Authorization: `Bearer ${token}` }
          }),
          usersReadUserMe({
            headers: { Authorization: `Bearer ${token}` }
          }),
          utilsHealthCheck()
        ])

        const data: DashboardData = {
          users: usersResponse.status === 'fulfilled' ? usersResponse.value.data?.data || [] : [],
          items: itemsResponse.status === 'fulfilled' ? itemsResponse.value.data?.data || [] : [],
          currentUser: currentUserResponse.status === 'fulfilled' ? currentUserResponse.value.data || null : null,
          systemHealth: healthResponse.status === 'fulfilled'
        }

        setState({ data, loading: false, error: null })
      } catch (error) {
        console.error('Dashboard data fetch error:', error)
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to load dashboard data'
        })
      }
    }

    fetchDashboardData()
  }, [])

  const { data, loading, error } = state

  if (error) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          {data?.currentUser ? `Welcome back, ${data.currentUser.full_name || data.currentUser.email}!` : 'Welcome back!'} Here's what's happening with your application.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Users */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Users</CardTitle>
              <Users className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {data?.users.length || 0}
                </div>
              )}
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Registered users
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Total Items */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Items</CardTitle>
              <Package className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {data?.items.length || 0}
                </div>
              )}
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Items in database
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Active User */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">Current User</CardTitle>
              <Activity className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <div className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                  {data?.currentUser?.full_name || data?.currentUser?.email || 'Unknown'}
                </div>
              )}
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Logged in user
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* System Health */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">System Health</CardTitle>
              <Settings className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="flex items-center space-x-2">
                  {data?.systemHealth ? (
                    <CheckCircle className="h-6 w-6 text-green-500" />
                  ) : (
                    <XCircle className="h-6 w-6 text-red-500" />
                  )}
                  <span className="text-lg font-semibold text-gray-900 dark:text-white">
                    {data?.systemHealth ? 'Healthy' : 'Issues'}
                  </span>
                </div>
              )}
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                API status
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity and System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Users */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Recent Users</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="flex items-center space-x-3">
                      <Skeleton className="h-8 w-8 rounded-full" />
                      <div className="space-y-1 flex-1">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                      <Skeleton className="h-3 w-16" />
                    </div>
                  ))}
                </div>
              ) : data?.users.length ? (
                <div className="space-y-4">
                  {data.users.slice(0, 5).map((user) => (
                    <div key={user.id} className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-teal-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-sm font-medium">
                          {(user.full_name || user.email).charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {user.full_name || user.email}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          {user.email}
                        </p>
                      </div>
                      <Badge variant={user.is_active ? "default" : "secondary"}>
                        {user.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  ))}
                  {data.users.length === 0 && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                      No users found
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                  No users found
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Items */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Package className="h-5 w-5" />
                <span>Recent Items</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="flex items-center space-x-3">
                      <Skeleton className="h-8 w-8 rounded" />
                      <div className="space-y-1 flex-1">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-48" />
                      </div>
                      <Skeleton className="h-3 w-16" />
                    </div>
                  ))}
                </div>
              ) : data?.items.length ? (
                <div className="space-y-4">
                  {data.items.slice(0, 5).map((item) => (
                    <div key={item.id} className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
                        <Package className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {item.title}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          {item.description || 'No description'}
                        </p>
                      </div>
                      <div className="text-xs text-gray-400">
                        ID: {item.id}
                      </div>
                    </div>
                  ))}
                  {data.items.length === 0 && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                      No items found
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                  No items found
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>System Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Skeleton className="h-3 w-3 rounded-full" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                    <div className="text-right">
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-3 w-12 mt-1" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {data?.systemHealth ? (
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    ) : (
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    )}
                    <span className="text-sm font-medium text-gray-900 dark:text-white">API Server</span>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm ${data?.systemHealth ? 'text-green-600' : 'text-red-600'}`}>
                      {data?.systemHealth ? 'Online' : 'Offline'}
                    </div>
                    <div className="text-xs text-gray-400">
                      {data?.systemHealth ? 'Responding' : 'Not responding'}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Authentication</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-green-600">Active</div>
                    <div className="text-xs text-gray-400">Token valid</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Data Loading</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-blue-600">Complete</div>
                    <div className="text-xs text-gray-400">
                      {data?.users.length || 0} users, {data?.items.length || 0} items
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
