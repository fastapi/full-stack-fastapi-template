import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react'

// Tipos de roles de usuario
export type UserRole = 'admin' | 'ceo' | 'manager' | 'hr' | 'agent' | 'supervisor' | 'support' | 'user' | 'client'

// Hook principal de autenticación
export function useAuth() {
  const { user, isLoaded, isSignedIn } = useUser()
  const { signOut } = useClerkAuth()

  // Obtener el rol del usuario o 'user' por defecto
  const role = (user?.publicMetadata?.role as UserRole) || 'user'
  
  // Depuración: Mostrar información detallada del usuario
  if (isLoaded && isSignedIn) {
    console.log('=== DEPURACIÓN DE AUTENTICACIÓN ===')
    console.log('Usuario autenticado:', user?.emailAddresses?.[0]?.emailAddress)
    console.log('ID del usuario:', user?.id)
    console.log('Rol del usuario:', role)
    console.log('Metadata pública:', user?.publicMetadata)
    console.log('Metadata privada:', user?.privateMetadata)
    console.log('Email verificado:', user?.emailAddresses?.[0]?.verification?.status)
    console.log('===================================')
    
    // Verificar si es el usuario CEO
    if (user?.emailAddresses?.[0]?.emailAddress === import.meta.env.VITE_CEO_USER) {
      console.log('⚠️  USUARIO CEO DETECTADO - Verificando rol...')
      if (role !== 'ceo') {
        console.warn('⚠️  ATENCIÓN: El usuario CEO no tiene el rol correcto. Rol actual:', role)
      } else {
        console.log('✅ Usuario CEO con rol correcto')
      }
    }
  }
  
  // Verificar si el usuario tiene un rol específico
  const hasRole = (requiredRole: UserRole | UserRole[]): boolean => {
    if (!isLoaded || !isSignedIn) return false
    
    if (Array.isArray(requiredRole)) {
      return requiredRole.includes(role)
    }
    
    return role === requiredRole
  }

  return {
    user,
    isLoaded,
    isSignedIn,
    isLoggedIn: isLoaded && isSignedIn,
    role,
    hasRole,
    logout: signOut,
  }
}

// Función para verificar si está logueado
export function isLoggedIn() {
  const { isLoaded, isSignedIn } = useUser()
  return isLoaded && isSignedIn
}

// Export default también
const useAuthDefault = useAuth
export default useAuthDefault
