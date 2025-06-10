import { ReactNode } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useAuth, UserRole } from '@/hooks/useAuth'
import { Box, Spinner, Text, VStack } from '@chakra-ui/react'

interface RouteGuardProps {
  children: ReactNode
  requiredRole?: UserRole | UserRole[]
  fallbackPath?: string
}

export const RouteGuard = ({
  children,
  requiredRole,
  fallbackPath = '/login',
}: RouteGuardProps) => {
  const { isAuthenticated, loading, checkRole } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return (
      <VStack h="100vh" justify="center" align="center">
        <Spinner size="xl" color="primary.black" />
        <Text>Verificando acceso...</Text>
      </VStack>
    )
  }

  if (!isAuthenticated) {
    navigate({ to: fallbackPath })
    return null
  }

  if (requiredRole && !checkRole(requiredRole)) {
    return (
      <Box p={8}>
        <Text fontSize="xl" fontWeight="bold" color="red.500">
          Acceso denegado
        </Text>
        <Text mt={2}>
          No tienes los permisos necesarios para acceder a esta página.
        </Text>
      </Box>
    )
  }

  return <>{children}</>
} 