import { Box, Flex, Icon, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink } from "@tanstack/react-router"
import { FiBriefcase, FiFolder, FiHome, FiImage, FiSettings, FiUsers } from "react-icons/fi"
import type { IconType } from "react-icons/lib"

import type { UserPublic } from "@/client"

const items = [
  { icon: FiHome, title: "Dashboard", path: "/dashboard" },
  { icon: FiFolder, title: "Projects", path: "/projects", requiresOrg: true },
  { icon: FiImage, title: "Galleries", path: "/galleries", requiresOrg: true },
  { icon: FiBriefcase, title: "Organization", path: "/organization", requiresOrg: true, teamOnly: true },
  { icon: FiSettings, title: "User Settings", path: "/settings" },
]

interface SidebarItemsProps {
  onClose?: () => void
}

interface Item {
  icon: IconType
  title: string
  path: string
  requiresOrg?: boolean
  teamOnly?: boolean
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  // Check if user has organization (clients always have access, team members need org)
  const hasOrganization = currentUser?.user_type === "client" || currentUser?.organization_id

  // Filter items based on user status
  let finalItems: Item[] = items.filter(item => {
    // Hide items that require org if user doesn't have one
    if (item.requiresOrg && !hasOrganization) return false
    // Hide team-only items from clients
    if (item.teamOnly && currentUser?.user_type !== "team_member") return false
    return true
  })

  // Add admin page for superusers
  if (currentUser?.is_superuser) {
    finalItems = [...finalItems, { icon: FiUsers, title: "Admin", path: "/admin" }]
  }

  const listItems = finalItems.map(({ icon, title, path }) => (
    <RouterLink key={title} to={path} onClick={onClose}>
      <Flex
        gap={4}
        px={4}
        py={2}
        _hover={{
          background: "gray.subtle",
        }}
        alignItems="center"
        fontSize="sm"
      >
        <Icon as={icon} alignSelf="center" />
        <Text ml={2}>{title}</Text>
      </Flex>
    </RouterLink>
  ))

  return (
    <>
      <Text fontSize="xs" px={4} py={2} fontWeight="bold">
        Menu
      </Text>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems
