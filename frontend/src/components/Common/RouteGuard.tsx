import { ReactNode, useEffect } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useAuth, UserRole } from '@/hooks/useAuth'
import { Box, Spinner, Text, VStack, Button, useToast } from '@chakra-ui/react'

interface RouteGuardProps {
  children: ReactNode
  requiredRole?: UserRole | UserRole[]
  fallbackPath?: string
}

export const RouteGuard = ({
  children,
  requiredRole,
  fallbackPath = '/sign-in',
}: RouteGuardProps) => {
  const { isLoaded, isSignedIn, hasRole, role } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    // Solo ejecutar la lógica de redirección cuando la autenticación esté cargada
    if (!isLoaded) return

    // Si el usuario no está autenticado, redirigir a la página de inicio de sesión
    if (!isSignedIn) {
      // Guardar la ruta actual para redirigir después del login
      const currentPath = window.location.pathname
      if (currentPath !== fallbackPath) {
        sessionStorage.setItem('redirectAfterLogin', currentPath)
      }
      navigate({ to: fallbackPath })
      return
    }

    // Si se requiere un rol específico, verificar si el usuario lo tiene
    if (requiredRole && !hasRole(requiredRole)) {
      // Redirigir al dashboard apropiado según el rol del usuario
      const userDashboard = getDashboardByRole(role)
      if (userDashboard) {
        navigate({ to: userDashboard })
        toast({
          title: 'Acceso denegado',
          description: 'No tienes permiso para acceder a esta sección.',
          status: 'warning',
          duration: 3000,
          isClosable: true,
        })
      } else {
        // Si no se puede determinar el dashboard, redirigir al dashboard por defecto
        navigate({ to: '/client-dashboard' })
      }
    }
  }, [isLoaded, isSignedIn, hasRole, requiredRole, role, navigate, fallbackPath, toast])

  // Mostrar spinner mientras se carga la autenticación
  if (!isLoaded) {
    return (
      <VStack h="100vh" justify="center" align="center">
        <Spinner size="xl" color="blue.500" />
        <Text mt={4} color="gray.600">Verificando credenciales...</Text>
      </VStack>
    )
  }

  // Si el usuario no está autenticado, no mostrar nada (ya se está redirigiendo)
  if (!isSignedIn) {
    return null
  }

  // Si se requiere un rol específico y el usuario no lo tiene, mostrar mensaje de error
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <Box p={8} textAlign="center">
        <Text fontSize="2xl" fontWeight="bold" color="red.500" mb={4}>
          Acceso restringido
        </Text>
        <Text fontSize="lg" mb={6}>
          No tienes los permisos necesarios para acceder a esta sección.
        </Text>
        <Button 
          colorScheme="blue" 
          onClick={() => navigate({ to: getDashboardByRole(role) || '/client-dashboard' })}
        >
          Volver al dashboard
        </Button>
      </Box>
    )
  }

  // Si todo está bien, renderizar los hijos
  return <>{children}</>
}

// Función auxiliar para obtener el dashboard según el rol del usuario
function getDashboardByRole(role?: string): string | null {
  switch (role) {
    case 'admin':
    case 'ceo':
    case 'manager':
    case 'hr':
    case 'agent':
    case 'supervisor':
    case 'support':
      return '/admin';
    case 'user':
    case 'client':
    default:
      return '/client-dashboard';
  }
}