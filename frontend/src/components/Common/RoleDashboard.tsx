import { ReactNode } from 'react'
import { Box, Flex, Heading, Text } from '@chakra-ui/react'
import { useAuth } from '@/hooks/useAuth'
import UserMenu from './UserMenu'

interface RoleDashboardProps {
  children: ReactNode
  title: string
  description?: string
}

export const RoleDashboard = ({
  children,
  title,
  description,
}: RoleDashboardProps) => {
  const { user, role } = useAuth()

  return (
    <Box maxW="7xl" mx="auto" px={6}>
      <Flex direction="column" gap={6}>
        {/* Header with UserMenu */}
        <Flex justify="space-between" align="center" pt={4}>
          <Box>
            <Heading size="lg" color="text">
              {title}
            </Heading>
            {description && (
              <Text mt={2} color="text.muted">
                {description}
              </Text>
            )}
            <Text mt={1} fontSize="sm" color="text.subtle">
              {user?.emailAddresses[0]?.emailAddress} • {role?.toUpperCase()}
            </Text>
          </Box>
          
          {/* User Menu in top right */}
          <UserMenu />
        </Flex>

        <Box
          bg="bg.surface"
          borderRadius="lg"
          p={6}
          shadow="base"
          border="1px"
          borderColor="border"
        >
          {children}
        </Box>
      </Flex>
    </Box>
  )
} 
