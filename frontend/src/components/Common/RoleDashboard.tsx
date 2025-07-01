import { ReactNode } from 'react'
import { Box,  Flex, Heading, Text } from '@chakra-ui/react'
import { useAuth } from '@/hooks/useAuth'

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
        <Box>
          <Heading size="lg" color="primary.black">
            {title}
          </Heading>
          {description && (
            <Text mt={2} color="ui.text.secondary">
              {description}
            </Text>
          )}
          <Text mt={1} fontSize="sm" color="ui.text.light">
            {user?.email} • {role?.toUpperCase()}
          </Text>
        </Box>

        <Box
          bg="white"
          borderRadius="lg"
          p={6}
          shadow="base"
          border="1px"
          borderColor="ui.border"
        >
          {children}
        </Box>
      </Flex>
    </Box>
  )
} 
