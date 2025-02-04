import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import { FiHome, FiBriefcase, FiMap, FiSettings, FiUsers } from "react-icons/fi"
import { FaRegLightbulb } from "react-icons/fa6"

import type { UserPublic } from "../../client"

const items = [
  { icon: FiHome, title: "Dashboard", path: "/" },
  { icon: FiBriefcase, title: "Items", path: "/items" },
  { icon: FiMap, title: "Create", path: "/paths" },
  { icon: FaRegLightbulb, title: "Learn", path: "/learn" },
  { icon: FiSettings, title: "User Settings", path: "/settings" },
]

interface SidebarItemsProps {
  onClose?: () => void
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const textColor = useColorModeValue("ui.main", "ui.light")
  const bgActive = useColorModeValue("#F5F2EE", "#4A5568")
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  const finalItems = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
    : items

  return (
    <Box>
      {finalItems.map(({ icon, title, path }) => (
        <Flex
          key={path}
          as={Link}
          to={path}
          align="center"
          gap={3}
          p={3}
          borderRadius="md"
          color={textColor}
          _hover={{
            textDecoration: "none",
            bg: bgActive,
          }}
          onClick={onClose}
        >
          <Icon as={icon} boxSize={5} />
          <Text>{title}</Text>
        </Flex>
      ))}
    </Box>
  )
}

export default SidebarItems
