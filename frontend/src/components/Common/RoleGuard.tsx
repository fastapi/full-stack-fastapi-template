import { Box, Heading, Text, VStack } from "@chakra-ui/react"
import type React from "react"
import { FiLock } from "react-icons/fi"

import useAuth from "../../hooks/useAuth"
import {
  getRoleDisplayName,
  getUserRole,
  hasPermission,
} from "../../utils/roles"

interface RoleGuardProps {
  permission: string
  children: React.ReactNode
  fallback?: React.ReactNode
}

/**
 * Component that conditionally renders children based on user permissions
 */
export const RoleGuard: React.FC<RoleGuardProps> = ({
  permission,
  children,
  fallback,
}) => {
  const { user } = useAuth()

  if (!hasPermission(user || null, permission)) {
    if (fallback) {
      return <>{fallback}</>
    }

    const userRole = getUserRole(user || null)

    return (
      <Box p={8} textAlign="center">
        <VStack gap={4}>
          <FiLock size={48} color="#e53e3e" />
          <Heading size="lg" color="red.500">
            Access Denied
          </Heading>
          <Text color="gray.600">
            You don't have permission to access this feature.
          </Text>
          <Text fontSize="sm" color="gray.500">
            Current role: {getRoleDisplayName(userRole)}
          </Text>
          <Text fontSize="sm" color="gray.500">
            Required permission: {permission}
          </Text>
        </VStack>
      </Box>
    )
  }

  return <>{children}</>
}

interface RouteGuardProps {
  route: string
  children: React.ReactNode
}

/**
 * Component that guards entire routes based on user role
 */
export const RouteGuard: React.FC<RouteGuardProps> = ({ route, children }) => {
  const { user } = useAuth()

  // For route guards, we'll use the canAccessRoute function
  // For now, let's implement a simple version
  const canAccess = hasPermission(user || null, getRoutePermission(route))

  if (!canAccess) {
    const userRole = getUserRole(user || null)

    return (
      <Box p={8} textAlign="center">
        <VStack gap={4}>
          <FiLock size={48} color="#e53e3e" />
          <Heading size="lg" color="red.500">
            Access Denied
          </Heading>
          <Text color="gray.600">
            You don't have permission to access this page.
          </Text>
          <Text fontSize="sm" color="gray.500">
            Current role: {getRoleDisplayName(userRole)}
          </Text>
        </VStack>
      </Box>
    )
  }

  return <>{children}</>
}

/**
 * Helper function to map routes to permissions
 */
function getRoutePermission(route: string): string {
  switch (route) {
    case "/admin":
      return "manage_users"
    case "/training":
      return "access_training"
    case "/documents":
      return "access_documents"
    case "/counselor":
      return "access_counselor_queue"
    default:
      return "chat_with_souls"
  }
}
