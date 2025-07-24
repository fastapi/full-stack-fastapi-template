"use client"

import { useState, useEffect } from "react"
import { User, Lock, AlertTriangle, Loader2, AlertCircle, Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  usersReadUserMe,
  usersUpdateUserMe,
  usersUpdatePasswordMe,
  usersDeleteUserMe
} from "@/lib/api-client"
import type { UserPublic, UserUpdate, UpdatePassword } from "@/client/types.gen"

interface UserSettingsState {
  user: UserPublic | null
  loading: boolean
  error: string | null
  success: string | null
}

interface ProfileFormData {
  full_name: string
  email: string
}

interface PasswordFormData {
  current_password: string
  new_password: string
  confirm_password: string
}

export default function SettingsPage() {
  const [state, setState] = useState<UserSettingsState>({
    user: null,
    loading: true,
    error: null,
    success: null
  })
  
  const [profileData, setProfileData] = useState<ProfileFormData>({
    full_name: "",
    email: ""
  })
  
  const [passwordData, setPasswordData] = useState<PasswordFormData>({
    current_password: "",
    new_password: "",
    confirm_password: ""
  })
  
  const [profileLoading, setProfileLoading] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const getAuthToken = () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('No authentication token found')
    }
    return token
  }

  const updateState = (updates: Partial<UserSettingsState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }

  const fetchCurrentUser = async () => {
    try {
      updateState({ loading: true, error: null })
      const token = getAuthToken()
      
      const response = await usersReadUserMe({
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data) {
        updateState({ user: response.data, loading: false })
        setProfileData({
          full_name: response.data.full_name || "",
          email: response.data.email
        })
      }
    } catch (error) {
      console.error('Fetch user error:', error)
      updateState({
        error: error instanceof Error ? error.message : 'Failed to fetch user data',
        loading: false
      })
    }
  }

  useEffect(() => {
    fetchCurrentUser()
  }, [])

  const handleUpdateProfile = async () => {
    if (!profileData.full_name.trim() || !profileData.email.trim()) {
      updateState({ error: 'Full name and email are required' })
      return
    }

    try {
      setProfileLoading(true)
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      const userData: UserUpdate = {
        full_name: profileData.full_name,
        email: profileData.email
      }

      const response = await usersUpdateUserMe({
        body: userData,
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data) {
        updateState({ user: response.data, success: 'Profile updated successfully' })
      }
    } catch (error) {
      console.error('Update profile error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to update profile' })
    } finally {
      setProfileLoading(false)
    }
  }

  const handleUpdatePassword = async () => {
    if (!passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password) {
      updateState({ error: 'All password fields are required' })
      return
    }

    if (passwordData.new_password !== passwordData.confirm_password) {
      updateState({ error: 'New passwords do not match' })
      return
    }

    if (passwordData.new_password.length < 8) {
      updateState({ error: 'New password must be at least 8 characters long' })
      return
    }

    try {
      setPasswordLoading(true)
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      const passwordUpdateData: UpdatePassword = {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      }

      await usersUpdatePasswordMe({
        body: passwordUpdateData,
        headers: { Authorization: `Bearer ${token}` }
      })

      updateState({ success: 'Password updated successfully' })
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: ""
      })
    } catch (error) {
      console.error('Update password error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to update password' })
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    try {
      setDeleteLoading(true)
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      await usersDeleteUserMe({
        headers: { Authorization: `Bearer ${token}` }
      })

      // Clear token and redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    } catch (error) {
      console.error('Delete account error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to delete account' })
      setDeleteLoading(false)
    }
  }

  if (state.loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">User Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your account settings and preferences.
          </p>
        </div>
        <div className="space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">User Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage your account settings and preferences.
        </p>
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

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile" className="flex items-center space-x-2">
            <User className="h-4 w-4" />
            <span>My Profile</span>
          </TabsTrigger>
          <TabsTrigger value="password" className="flex items-center space-x-2">
            <Lock className="h-4 w-4" />
            <span>Password</span>
          </TabsTrigger>
          <TabsTrigger value="danger" className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4" />
            <span>Danger Zone</span>
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="full-name">Full Name *</Label>
                <Input
                  id="full-name"
                  placeholder="Enter your full name..."
                  value={profileData.full_name}
                  onChange={(e) => setProfileData(prev => ({ ...prev, full_name: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address *</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email address..."
                  value={profileData.email}
                  onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                />
              </div>
              <div className="flex justify-end">
                <Button onClick={handleUpdateProfile} disabled={profileLoading}>
                  {profileLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    'Update Profile'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Password Tab */}
        <TabsContent value="password">
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current-password">Current Password *</Label>
                <div className="relative">
                  <Input
                    id="current-password"
                    type={showCurrentPassword ? "text" : "password"}
                    placeholder="Enter your current password..."
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  >
                    {showCurrentPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-password">New Password *</Label>
                <div className="relative">
                  <Input
                    id="new-password"
                    type={showNewPassword ? "text" : "password"}
                    placeholder="Enter your new password..."
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                  >
                    {showNewPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm New Password *</Label>
                <div className="relative">
                  <Input
                    id="confirm-password"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm your new password..."
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div className="flex justify-end">
                <Button onClick={handleUpdatePassword} disabled={passwordLoading}>
                  {passwordLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    'Update Password'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Danger Zone Tab */}
        <TabsContent value="danger">
          <Card className="border-red-200 dark:border-red-800">
            <CardHeader>
              <CardTitle className="text-red-600 dark:text-red-400">Danger Zone</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border border-red-200 dark:border-red-800 p-4">
                <h3 className="text-lg font-medium text-red-600 dark:text-red-400 mb-2">
                  Delete Account
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Once you delete your account, there is no going back. Please be certain.
                </p>
                <Button 
                  variant="destructive" 
                  onClick={() => setIsDeleteDialogOpen(true)}
                >
                  <AlertTriangle className="mr-2 h-4 w-4" />
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Account Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-red-600">Delete Account</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete your account? This action cannot be undone and will permanently remove all your data.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteAccount} disabled={deleteLoading}>
              {deleteLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete Account'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
