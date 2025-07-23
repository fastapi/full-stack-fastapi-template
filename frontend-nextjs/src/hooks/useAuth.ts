"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { 
  loginLoginAccessToken, 
  usersReadUserMe, 
  usersRegisterUser,
  loginRecoverPassword,
  loginResetPassword
} from "@/client"
import { getAuthToken, setAuthToken, removeAuthToken } from "@/lib/api"
import type { 
  BodyLoginLoginAccessToken, 
  UserPublic, 
  UserRegister,
  NewPassword 
} from "@/client"

export function useAuth() {
  const queryClient = useQueryClient()
  const router = useRouter()

  // Get current user
  const { data: user, isLoading } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const token = getAuthToken()
      if (!token) return null
      
      try {
        const response = await usersReadUserMe({
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        return response.data
      } catch (error) {
        removeAuthToken()
        return null
      }
    },
    enabled: !!getAuthToken(),
  })

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (credentials: BodyLoginLoginAccessToken) => {
      const response = await loginLoginAccessToken({
        body: credentials
      })
      return response.data
    },
    onSuccess: (data) => {
      if (data?.access_token) {
        setAuthToken(data.access_token)
        queryClient.invalidateQueries({ queryKey: ["currentUser"] })
        router.push("/")
      }
    },
  })

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: async (userData: UserRegister) => {
      const response = await usersRegisterUser({
        body: userData
      })
      return response.data
    },
    onSuccess: () => {
      router.push("/login?message=Registration successful. Please log in.")
    },
  })

  // Logout function
  const logout = () => {
    removeAuthToken()
    queryClient.setQueryData(["currentUser"], null)
    queryClient.clear()
    router.push("/login")
  }

  // Password recovery
  const recoverPasswordMutation = useMutation({
    mutationFn: async (email: string) => {
      const response = await loginRecoverPassword({
        body: { email }
      })
      return response.data
    },
  })

  // Reset password
  const resetPasswordMutation = useMutation({
    mutationFn: async (data: NewPassword & { token: string }) => {
      const response = await loginResetPassword({
        body: {
          token: data.token,
          new_password: data.new_password
        }
      })
      return response.data
    },
    onSuccess: () => {
      router.push("/login?message=Password reset successful. Please log in.")
    },
  })

  return {
    user: user as UserPublic | null,
    isLoading,
    isAuthenticated: !!user,
    login: loginMutation.mutate,
    loginError: loginMutation.error,
    isLoginLoading: loginMutation.isPending,
    register: registerMutation.mutate,
    registerError: registerMutation.error,
    isRegisterLoading: registerMutation.isPending,
    logout,
    recoverPassword: recoverPasswordMutation.mutate,
    recoverPasswordError: recoverPasswordMutation.error,
    isRecoverPasswordLoading: recoverPasswordMutation.isPending,
    resetPassword: resetPasswordMutation.mutate,
    resetPasswordError: resetPasswordMutation.error,
    isResetPasswordLoading: resetPasswordMutation.isPending,
  }
}
