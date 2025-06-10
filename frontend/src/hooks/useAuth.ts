import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useNhostClient } from '@nhost/nextjs'

export type UserRole = 'ceo' | 'manager' | 'supervisor' | 'hr' | 'support' | 'agent'

interface UseAuthReturn {
  isAuthenticated: boolean
  user: any | null
  role: UserRole | null
  loading: boolean
  error: Error | null
  signOut: () => Promise<void>
  checkRole: (requiredRole: UserRole | UserRole[]) => boolean
}

export const useAuth = (): UseAuthReturn => {
  const nhost = useNhostClient()
  const navigate = useNavigate()
  const [user, setUser] = useState<any | null>(null)
  const [role, setRole] = useState<UserRole | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const session = await nhost.auth.getSession()
        if (session) {
          setUser(session.user)
          // Obtener el rol del usuario desde los metadatos
          const userRole = session.user?.metadata?.role as UserRole
          setRole(userRole)
        }
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()

    // Suscribirse a cambios en la autenticación
    const { data: authListener } = nhost.auth.onAuthStateChanged((event, session) => {
      if (event === 'SIGNED_IN' && session) {
        setUser(session.user)
        const userRole = session.user?.metadata?.role as UserRole
        setRole(userRole)
      } else if (event === 'SIGNED_OUT') {
        setUser(null)
        setRole(null)
      }
    })

    return () => {
      authListener?.unsubscribe()
    }
  }, [nhost])

  const signOut = useCallback(async () => {
    try {
      await nhost.auth.signOut()
      navigate({ to: '/login' })
    } catch (err) {
      setError(err as Error)
    }
  }, [nhost, navigate])

  const checkRole = useCallback(
    (requiredRole: UserRole | UserRole[]): boolean => {
      if (!role) return false
      if (Array.isArray(requiredRole)) {
        return requiredRole.includes(role)
      }
      return role === requiredRole
    },
    [role]
  )

  return {
    isAuthenticated: !!user,
    user,
    role,
    loading,
    error,
    signOut,
    checkRole,
  }
}
