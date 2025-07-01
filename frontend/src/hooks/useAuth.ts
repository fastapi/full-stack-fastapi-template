import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react'

// Hook principal de autenticación
export function useAuth() {
  const { user, isLoaded } = useUser()
  const { signOut } = useClerkAuth()

  return {
    user,
    isLoaded,
    isLoggedIn: isLoaded && !!user,
    logout: signOut,
    role: user?.publicMetadata?.role as string || 'user'
  }
}

// Función para verificar si está logueado
export function isLoggedIn() {
  const { user, isLoaded } = useUser()
  return isLoaded && !!user
}

// Export default también
const useAuthDefault = useAuth
export default useAuthDefault
