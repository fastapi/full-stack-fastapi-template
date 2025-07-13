import { Badge, Box, Button, Flex, HStack, Text, VStack } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import { FaUserAstronaut } from "react-icons/fa"
import { FiLogOut, FiUser, FiSettings } from "react-icons/fi"

import useAuth from "@/hooks/useAuth"
import {
  getRoleColor,
  getRoleDisplayName,
  getUserRole,
} from "../../utils/roles"
import { MenuContent, MenuItem, MenuRoot, MenuTrigger } from "../ui/menu"

const UserMenu = () => {
  const { user, logout } = useAuth()
  const userRole = getUserRole(user || null)
  const roleDisplayName = getRoleDisplayName(userRole)
  const roleColor = getRoleColor(userRole)

  const handleLogout = async () => {
    logout()
  }

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  // Custom Avatar Component
  const CustomAvatar = ({ name, size = "sm", ...props }: { name: string; size?: string; [key: string]: any }) => {
    const initials = getInitials(name)
    const sizeMap = {
      sm: { w: "32px", h: "32px", fontSize: "xs" },
      md: { w: "40px", h: "40px", fontSize: "sm" }
    }
    const avatarSize = sizeMap[size as keyof typeof sizeMap] || sizeMap.sm

    return (
      <Box
        w={avatarSize.w}
        h={avatarSize.h}
        borderRadius="full"
        display="flex"
        alignItems="center"
        justifyContent="center"
        fontSize={avatarSize.fontSize}
        fontWeight="600"
        color="white"
        {...props}
      >
        {initials}
      </Box>
    )
  }

  return (
    <>
      {/* Desktop */}
      <Flex>
        <MenuRoot>
          <MenuTrigger asChild>
            <Button 
              data-testid="user-menu" 
              variant="ghost"
              p={3}
              h="auto"
              borderRadius="12px"
              _hover={{ bg: "gray.50" }}
              _active={{ bg: "gray.100" }}
              transition="all 0.2s"
            >
              <HStack gap={3} align="center">
                <CustomAvatar 
                  name={user?.full_name || "User"}
                  bg={`${roleColor}.500`}
                  size="sm"
                />
                <VStack align="start" gap={0} minW="0">
                  <Text 
                    fontSize="sm" 
                    fontWeight="600" 
                    color="gray.800"
                    truncate
                    maxW="120px"
                    lineHeight="1.2"
                  >
                    {user?.full_name || "User"}
                  </Text>
                  <Badge 
                    colorScheme={roleColor} 
                    size="xs" 
                    px={2}
                    py={0.5}
                    borderRadius="full"
                    fontWeight="500"
                    fontSize="10px"
                    letterSpacing="0.025em"
                  >
                    {roleDisplayName}
                  </Badge>
                </VStack>
              </HStack>
            </Button>
          </MenuTrigger>

          <MenuContent 
            minW="200px"
            borderRadius="12px"
            border="1px"
            borderColor="gray.200"
            shadow="lg"
            bg="white"
            p={2}
          >
            {/* User Info Header */}
            <Box p={3} mb={2} bg="gray.50" borderRadius="8px">
              <HStack gap={3}>
                <CustomAvatar 
                  name={user?.full_name || "User"}
                  bg={`${roleColor}.500`}
                  size="sm"
                />
                <VStack align="start" gap={0.5} flex="1" minW="0">
                  <Text 
                    fontSize="sm" 
                    fontWeight="600" 
                    color="gray.800"
                    truncate
                    maxW="140px"
                  >
                    {user?.full_name || "User"}
                  </Text>
                  <Text 
                    fontSize="xs" 
                    color="gray.600"
                    truncate
                    maxW="140px"
                  >
                    {user?.email}
                  </Text>
                  <Badge 
                    colorScheme={roleColor} 
                    size="xs" 
                    px={2}
                    py={0.5}
                    borderRadius="full"
                    fontWeight="500"
                    fontSize="10px"
                    mt={1}
                  >
                    {roleDisplayName}
                  </Badge>
                </VStack>
              </HStack>
            </Box>

            <Link to="/settings">
              <MenuItem
                closeOnSelect
                value="user-settings"
                gap={3}
                py={3}
                px={3}
                borderRadius="8px"
                _hover={{ bg: "gray.50" }}
                style={{ cursor: "pointer" }}
              >
                <FiSettings fontSize="16px" color="#6B7280" />
                <Text fontSize="sm" fontWeight="500" color="gray.700">
                  Settings
                </Text>
              </MenuItem>
            </Link>

            <MenuItem
              value="logout"
              gap={3}
              py={3}
              px={3}
              borderRadius="8px"
              _hover={{ bg: "red.50" }}
              onClick={handleLogout}
              style={{ cursor: "pointer" }}
            >
              <FiLogOut fontSize="16px" color="#EF4444" />
              <Text fontSize="sm" fontWeight="500" color="red.600">
                Sign Out
              </Text>
            </MenuItem>
          </MenuContent>
        </MenuRoot>
      </Flex>
    </>
  )
}

export default UserMenu
