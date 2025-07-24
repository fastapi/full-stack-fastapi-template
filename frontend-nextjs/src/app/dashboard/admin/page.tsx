"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Plus, MoreHorizontal, Edit, Trash2, Users, Loader2, AlertCircle, Eye, EyeOff, Shield, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import {
  usersReadUsers,
  usersCreateUser,
  usersUpdateUser,
  usersDeleteUser,
  usersReadUserMe
} from "@/lib/api-client"
import type { UserPublic, UserCreate, UserUpdate } from "@/client/types.gen"

interface AdminState {
  users: UserPublic[]
  totalCount: number
  currentPage: number
  loading: boolean
  error: string | null
  success: string | null
  currentUser: UserPublic | null
}

interface UserFormData {
  email: string
  full_name: string
  password: string
  is_superuser: boolean
}

const PER_PAGE = 5

export default function AdminPage() {
  const [state, setState] = useState<AdminState>({
    users: [],
    totalCount: 0,
    currentPage: 1,
    loading: true,
    error: null,
    success: null,
    currentUser: null
  })
  
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<UserPublic | null>(null)
  const [formData, setFormData] = useState<UserFormData>({ 
    email: "", 
    full_name: "", 
    password: "", 
    is_superuser: false 
  })
  const [formLoading, setFormLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const getAuthToken = () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('No authentication token found')
    }
    return token
  }

  const updateState = (updates: Partial<AdminState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }

  const fetchCurrentUser = async () => {
    try {
      const token = getAuthToken()
      const response = await usersReadUserMe({
        headers: { Authorization: `Bearer ${token}` }
      })
      if (response.data) {
        updateState({ currentUser: response.data })
      }
    } catch (error) {
      console.error('Fetch current user error:', error)
    }
  }

  const fetchUsers = async (page: number = 1) => {
    try {
      updateState({ loading: true, error: null })
      const token = getAuthToken()
      
      const response = await usersReadUsers({
        query: {
          skip: (page - 1) * PER_PAGE,
          limit: PER_PAGE
        },
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data) {
        updateState({
          users: response.data.data || [],
          totalCount: response.data.count || 0,
          currentPage: page,
          loading: false
        })
      }
    } catch (error) {
      console.error('Fetch users error:', error)
      updateState({
        error: error instanceof Error ? error.message : 'Failed to fetch users',
        loading: false
      })
    }
  }

  useEffect(() => {
    fetchCurrentUser()
    fetchUsers()
  }, [])

  const handleCreateUser = async () => {
    if (!formData.email.trim() || !formData.full_name.trim() || !formData.password.trim()) {
      updateState({ error: 'Email, full name, and password are required' })
      return
    }

    if (formData.password.length < 8) {
      updateState({ error: 'Password must be at least 8 characters long' })
      return
    }

    try {
      setFormLoading(true)
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      const userData: UserCreate = {
        email: formData.email,
        full_name: formData.full_name,
        password: formData.password,
        is_superuser: formData.is_superuser
      }

      await usersCreateUser({
        body: userData,
        headers: { Authorization: `Bearer ${token}` }
      })

      updateState({ success: 'User created successfully' })
      setFormData({ email: "", full_name: "", password: "", is_superuser: false })
      setIsAddDialogOpen(false)
      fetchUsers(state.currentPage)
    } catch (error) {
      console.error('Create user error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to create user' })
    } finally {
      setFormLoading(false)
    }
  }

  const handleUpdateUser = async () => {
    if (!editingUser || !formData.email.trim() || !formData.full_name.trim()) {
      updateState({ error: 'Email and full name are required' })
      return
    }

    try {
      setFormLoading(true)
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      const userData: UserUpdate = {
        email: formData.email,
        full_name: formData.full_name,
        is_superuser: formData.is_superuser
      }

      await usersUpdateUser({
        path: { user_id: editingUser.id.toString() },
        body: userData,
        headers: { Authorization: `Bearer ${token}` }
      })

      updateState({ success: 'User updated successfully' })
      setFormData({ email: "", full_name: "", password: "", is_superuser: false })
      setIsEditDialogOpen(false)
      setEditingUser(null)
      fetchUsers(state.currentPage)
    } catch (error) {
      console.error('Update user error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to update user' })
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteUser = async (user: UserPublic) => {
    if (state.currentUser && user.id === state.currentUser.id) {
      updateState({ error: 'You cannot delete your own account from here' })
      return
    }

    if (!confirm(`Are you sure you want to delete user "${user.full_name || user.email}"? This action cannot be undone.`)) {
      return
    }

    try {
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      await usersDeleteUser({
        path: { user_id: user.id.toString() },
        headers: { Authorization: `Bearer ${token}` }
      })

      updateState({ success: 'User deleted successfully' })
      fetchUsers(state.currentPage)
    } catch (error) {
      console.error('Delete user error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to delete user' })
    }
  }

  const openEditDialog = (user: UserPublic) => {
    setEditingUser(user)
    setFormData({ 
      email: user.email, 
      full_name: user.full_name || "", 
      password: "", 
      is_superuser: user.is_superuser || false 
    })
    setIsEditDialogOpen(true)
  }

  const openAddDialog = () => {
    setFormData({ email: "", full_name: "", password: "", is_superuser: false })
    setIsAddDialogOpen(true)
  }

  const totalPages = Math.ceil(state.totalCount / PER_PAGE)

  // Check if current user is superuser
  if (state.currentUser && !state.currentUser.is_superuser) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Access Denied
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            You need administrator privileges to access this page.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Admin Panel</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage users and their permissions across the application.
          </p>
        </div>
        <Button onClick={openAddDialog} className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Add User</span>
        </Button>
      </div>

      {/* Error/Success Messages */}
      {state.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{state.error}</AlertDescription>
        </Alert>
      )}

      {state.success && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{state.success}</AlertDescription>
        </Alert>
      )}

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Users ({state.totalCount})</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {state.loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-20" />
                </div>
              ))}
            </div>
          ) : state.users.length === 0 ? (
            <div className="text-center py-12">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No users found
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Get started by creating your first user.
              </p>
              <Button onClick={openAddDialog}>
                <Plus className="h-4 w-4 mr-2" />
                Add User
              </Button>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {state.users.map((user, index) => (
                    <motion.tr
                      key={user.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border-b"
                    >
                      <TableCell className="font-mono text-sm">{user.id}</TableCell>
                      <TableCell className="font-medium">
                        {user.full_name || (
                          <span className="italic text-gray-400">No name</span>
                        )}
                      </TableCell>
                      <TableCell className="text-gray-600 dark:text-gray-400">
                        {user.email}
                      </TableCell>
                      <TableCell>
                        <Badge variant={user.is_superuser ? "default" : "secondary"}>
                          {user.is_superuser ? (
                            <>
                              <ShieldCheck className="h-3 w-3 mr-1" />
                              Admin
                            </>
                          ) : (
                            <>
                              <Shield className="h-3 w-3 mr-1" />
                              User
                            </>
                          )}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => openEditDialog(user)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              onClick={() => handleDeleteUser(user)}
                              className="text-red-600"
                              disabled={state.currentUser?.id === user.id}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </motion.tr>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center mt-6">
                  <Pagination>
                    <PaginationContent>
                      <PaginationItem>
                        <PaginationPrevious 
                          onClick={() => state.currentPage > 1 && fetchUsers(state.currentPage - 1)}
                          className={state.currentPage <= 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                        />
                      </PaginationItem>
                      {[...Array(totalPages)].map((_, i) => {
                        const page = i + 1
                        if (page === state.currentPage) {
                          return (
                            <PaginationItem key={page}>
                              <PaginationLink isActive>{page}</PaginationLink>
                            </PaginationItem>
                          )
                        }
                        return (
                          <PaginationItem key={page}>
                            <PaginationLink 
                              onClick={() => fetchUsers(page)}
                              className="cursor-pointer"
                            >
                              {page}
                            </PaginationLink>
                          </PaginationItem>
                        )
                      })}
                      <PaginationItem>
                        <PaginationNext 
                          onClick={() => state.currentPage < totalPages && fetchUsers(state.currentPage + 1)}
                          className={state.currentPage >= totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                        />
                      </PaginationItem>
                    </PaginationContent>
                  </Pagination>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Add User Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New User</DialogTitle>
            <DialogDescription>
              Create a new user account with email, name, and permissions.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="add-email">Email Address *</Label>
              <Input
                id="add-email"
                type="email"
                placeholder="Enter user email..."
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-name">Full Name *</Label>
              <Input
                id="add-name"
                placeholder="Enter user full name..."
                value={formData.full_name}
                onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-password">Password *</Label>
              <div className="relative">
                <Input
                  id="add-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter user password..."
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="add-superuser"
                checked={formData.is_superuser}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_superuser: checked }))}
              />
              <Label htmlFor="add-superuser">Administrator privileges</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateUser} disabled={formLoading}>
              {formLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create User'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
            <DialogDescription>
              Update the user's information and permissions.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-email">Email Address *</Label>
              <Input
                id="edit-email"
                type="email"
                placeholder="Enter user email..."
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-name">Full Name *</Label>
              <Input
                id="edit-name"
                placeholder="Enter user full name..."
                value={formData.full_name}
                onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
              />
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="edit-superuser"
                checked={formData.is_superuser}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_superuser: checked }))}
                disabled={state.currentUser?.id === editingUser?.id}
              />
              <Label htmlFor="edit-superuser">
                Administrator privileges
                {state.currentUser?.id === editingUser?.id && (
                  <span className="text-sm text-gray-500 ml-2">(Cannot modify your own role)</span>
                )}
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateUser} disabled={formLoading}>
              {formLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update User'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
