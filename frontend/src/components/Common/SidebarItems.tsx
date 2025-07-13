import { Box, Flex, Icon, Text, Badge } from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"
import {
  FiCpu,
  FiHome,
  FiSettings,
  FiUsers,
  FiShield,
} from "react-icons/fi"
import type { IconType } from "react-icons/lib"

import useAuth from "../../hooks/useAuth"
import {
  getRoleDisplayName,
  getUserRole,
  hasPermission,
  UserRole,
} from "../../utils/roles"

// Core navigation items for admin, counselor, and trainer
const coreItems = [
  {
    icon: FiHome,
    title: "Dashboard",
    path: "/",
    permission: "chat_with_souls",
    roles: [UserRole.ADMIN, UserRole.COUNSELOR, UserRole.TRAINER], // Exclude regular users
  },
  {
    icon: FiCpu,
    title: "AI Souls",
    path: "/ai-souls",
    permission: "chat_with_souls",
    roles: [], // Available to all users
  },
]

// Content management items (temporarily hidden)
const contentItems: Item[] = [
  // {
  //   icon: FiUpload,
  //   title: "Documents",
  //   path: "/documents",
  //   permission: "access_documents",
  //   roles: [],
  // },
]

// Counselor items
const counselorItems = [
  {
    icon: FiShield,
    title: "Counselor Dashboard",
    path: "/counselor",
    permission: "access_counselor_queue",
    roles: [UserRole.COUNSELOR, UserRole.ADMIN],
  },
]

// Admin-only items (Advanced RAG temporarily hidden)
const adminItems: Item[] = [
  { icon: FiUsers, title: "Admin", path: "/admin", permission: "manage_users", roles: [UserRole.ADMIN] },
  // {
  //   icon: FiDatabase,
  //   title: "Advanced RAG",
  //   path: "/advanced-rag",
  //   permission: "admin",
  //   roles: [UserRole.ADMIN],
  // },
]

// Settings (always last)
const settingsItems = [
  {
    icon: FiSettings,
    title: "Settings",
    path: "/settings",
    permission: "chat_with_souls",
    roles: [], // Available to all users
  },
]

interface Item {
  icon: IconType
  title: string
  path: string
  permission: string
  roles?: UserRole[] // If empty, available to all roles
}

interface SidebarItemsProps {
  onClose?: () => void
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const { user } = useAuth()

  // Get all items that the user has permission to access
  const getAccessibleItems = (): Item[] => {
    let items: Item[] = []
    
    if (user) {
      const userRole = getUserRole(user)
      
      // Filter core items based on user role
      const filteredCoreItems = coreItems.filter(item => 
        item.roles.length === 0 || item.roles.includes(userRole)
      )
      
      if (userRole === UserRole.ADMIN || user.is_superuser) {
        items = [...filteredCoreItems, ...contentItems, ...counselorItems, ...adminItems, ...settingsItems]
      } else if (userRole === UserRole.COUNSELOR) {
        items = [...filteredCoreItems, ...counselorItems, ...settingsItems]
      } else if (userRole === UserRole.TRAINER) {
        items = [...filteredCoreItems, ...contentItems, ...settingsItems]
      } else {
        // Regular users only get filtered core items + settings
        items = [...filteredCoreItems, ...settingsItems]
      }
    }
    
    // Filter by permissions as a backup, but for admin users, show all items
    if (user?.is_superuser) {
      return items // Skip permission filtering for superusers
    }
    
    return items.filter((item) =>
      hasPermission(user || null, item.permission),
    )
  }

  const finalItems = getAccessibleItems()
  const userRole = getUserRole(user || null)
  const isNonAdminUser = userRole === UserRole.USER

  const getRoleSpecificMessage = () => {
    switch (userRole) {
      case UserRole.ADMIN:
        return "Full system access"
      case UserRole.COUNSELOR:
        return "Review & safety monitoring"
      case UserRole.TRAINER:
        return "AI training & development"
      case UserRole.USER:
        return "Chat with AI companions"
      default:
        return "Limited access"
    }
  }

  const listItems = finalItems.map(({ icon, title, path }) => (
    <RouterLink key={title} to={path} onClick={onClose}>
      <Flex
        gap={4}
        px={isNonAdminUser ? 6 : 4}
        py={isNonAdminUser ? 4 : 2}
        _hover={{
          background: "gray.100",
          _dark: {
            background: "gray.700",
          },
        }}
        alignItems="center"
        fontSize={isNonAdminUser ? "md" : "sm"}
        fontWeight={isNonAdminUser ? "medium" : "normal"}
        borderRadius="md"
        mx={2}
        transition="all 0.2s"
        minH={isNonAdminUser ? "50px" : "36px"}
      >
        <Icon 
          as={icon} 
          alignSelf="center" 
          color="teal.500" 
          boxSize={isNonAdminUser ? "20px" : "16px"}
        />
        <Text ml={2}>{title}</Text>
      </Flex>
    </RouterLink>
  ))

  return (
    <>
      <Text 
        fontSize="xs" 
        px={isNonAdminUser ? 6 : 4} 
        py={isNonAdminUser ? 4 : 2} 
        fontWeight="bold" 
        color="gray.500"
      >
        Navigation
      </Text>
      <Box>{listItems}</Box>
      
      {user && (
        <Box 
          mt='auto'
          px={isNonAdminUser ? 6 : 4} 
          pb={isNonAdminUser ? 6 : 4} 
          borderTop="1px" 
          mb={6}
          borderColor="gray.200" 
          pt={isNonAdminUser ? 6 : 4}
        >
          <Text 
            fontSize="xs" 
            py={1} 
            fontWeight="bold" 
            color="gray.500"
          >
            Current User
          </Text>
          <Text 
            fontSize={isNonAdminUser ? "md" : "sm"} 
            fontWeight="medium" 
            color="gray.700" 
            mb={2}
          >
            {user.full_name || user.email}
          </Text>
          <Flex gap={2} mb={2} flexWrap="wrap">
            <Badge 
              colorScheme="teal" 
              size={isNonAdminUser ? "md" : "sm"}
              px={isNonAdminUser ? 3 : 2}
              py={isNonAdminUser ? 1 : 0.5}
            >
              {getRoleDisplayName(userRole)}
            </Badge>
            {user.is_superuser && (
              <Badge 
                colorScheme="red" 
                size={isNonAdminUser ? "md" : "sm"}
                px={isNonAdminUser ? 3 : 2}
                py={isNonAdminUser ? 1 : 0.5}
              >
                Superuser
              </Badge>
            )}
          </Flex>
          <Text 
            fontSize="xs" 
            color="gray.500"
          >
            {getRoleSpecificMessage()}
          </Text>
        </Box>
      )}
    </>
  )
}

export default SidebarItems
