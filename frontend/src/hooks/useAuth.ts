import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState, useEffect } from "react"

import {
  type Body_login_login_access_token as AccessToken,
  type ApiError,
  LoginService,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { handleError } from "@/utils"
import { getUserRole, UserRole } from "@/utils/roles"

const TOKEN_KEY = "access_token"
const TOKEN_TIMESTAMP_KEY = "token_timestamp"

const isLoggedIn = () => {
  return localStorage.getItem(TOKEN_KEY) !== null
}

const isTokenExpired = (user: UserPublic | null) => {
  const token = localStorage.getItem(TOKEN_KEY)
  const timestamp = localStorage.getItem(TOKEN_TIMESTAMP_KEY)
  
  if (!token || !timestamp) {
    return true
  }
  
  const tokenAge = Date.now() - parseInt(timestamp)
  const userRole = getUserRole(user)
  
  // Role-based session timeouts (in milliseconds)
  const sessionTimeouts = {
    [UserRole.ADMIN]: 8 * 60 * 60 * 1000,      // 8 hours for admins
    [UserRole.COUNSELOR]: 6 * 60 * 60 * 1000,  // 6 hours for counselors
    [UserRole.TRAINER]: 4 * 60 * 60 * 1000,    // 4 hours for trainers
    [UserRole.USER]: 2 * 60 * 60 * 1000,       // 2 hours for regular users
  }
  
  const timeout = sessionTimeouts[userRole] || sessionTimeouts[UserRole.USER]
  return tokenAge > timeout
}

const setToken = (token: string) => {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(TOKEN_TIMESTAMP_KEY, Date.now().toString())
}

const clearToken = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TOKEN_TIMESTAMP_KEY)
}

const useAuth = () => {
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const { data: user, isError, error: userError } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    enabled: isLoggedIn(),
    retry: (failureCount, error) => {
      // Don't retry on 401/403 errors (authentication/authorization issues)
      if (error?.message?.includes('401') || error?.message?.includes('403')) {
        return false
      }
      return failureCount < 3
    },
    refetchOnWindowFocus: true,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes to validate session
  })

  // Auto-logout on token expiration or authentication errors
  useEffect(() => {
    if (isLoggedIn() && (isTokenExpired(user || null) || isError)) {
      logout()
    }
  }, [user, isError, userError])

  // Session activity tracking
  useEffect(() => {
    if (!isLoggedIn()) return

    const updateActivity = () => {
      if (user && !isTokenExpired(user || null)) {
        // Update timestamp on user activity
        localStorage.setItem(TOKEN_TIMESTAMP_KEY, Date.now().toString())
      }
    }

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
    events.forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true })
    })

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity)
      })
    }
  }, [user])

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),

    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const login = async (data: AccessToken) => {
    const response = await LoginService.loginAccessToken({
      formData: data,
    })
    setToken(response.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      // Invalidate and refetch user data
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: "/" })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const logout = () => {
    clearToken()
    // Clear user data from cache
    queryClient.removeQueries({ queryKey: ["currentUser"] })
    // Clear all cached data to prevent cross-user contamination
    queryClient.clear()
    navigate({ to: "/login" })
  }

  // Force logout function for admin use
  const forceLogout = (reason?: string) => {
    if (reason) {
      setError(reason)
    }
    logout()
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    forceLogout,
    user,
    error,
    resetError: () => setError(null),
    isTokenExpired: () => isTokenExpired(user || null),
  }
}

export { isLoggedIn }
export default useAuth
