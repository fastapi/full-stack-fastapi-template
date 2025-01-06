import { Box, Flex, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { FiBriefcase, FiHome, FiSettings, FiUsers } from "react-icons/fi"

import { RouterLink } from "@/components/ui/router-link"

import type { UserPublic } from "@/client"
import { ReactIcon } from "@/components/ui/icon"
import type { IconType } from "react-icons/lib"

interface SidebarItemProps {
  icon: IconType
  title: string
  path: string
}
const items: SidebarItemProps[] = [
  { icon: FiHome, title: "Dashboard", path: "/" },
  { icon: FiBriefcase, title: "Items", path: "/items" },
  { icon: FiSettings, title: "User Settings", path: "/settings" },
]

interface SidebarItemsProps {
  onClose?: () => void
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  const finalItems: SidebarItemProps[] = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
    : items

  const listItems = finalItems.map(({ icon, title, path }) => (
    <RouterLink to={path} key={title} asChild>
      <Flex w="100%" p={2} onClick={onClose}>
        <ReactIcon icon={icon} alignSelf="center" />
        <Text ml={2}>{title}</Text>
      </Flex>
    </RouterLink>
  ))

  return (
    <>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems
