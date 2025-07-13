import { Box, Container, Heading, Icon, Tabs, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FiLock, FiMoon, FiSettings, FiTrash2, FiUser } from "react-icons/fi"

import Appearance from "@/components/UserSettings/Appearance"
import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import RAGConfiguration from "@/components/UserSettings/RAGConfiguration"
import UserInformation from "@/components/UserSettings/UserInformation"
import useAuth from "@/hooks/useAuth"
import { getUserRole, UserRole } from "@/utils/roles"

const tabsConfig = [
  {
    value: "my-profile",
    title: "My profile",
    component: UserInformation,
    icon: FiUser,
    description: "Manage your personal information and email settings",
  },
  {
    value: "password",
    title: "Password",
    component: ChangePassword,
    icon: FiLock,
    description: "Update your password and security preferences",
  },
  {
    value: "rag-config",
    title: "RAG Settings",
    component: RAGConfiguration,
    icon: FiSettings,
    description: "Configure search and document processing settings",
    requiredRole: [UserRole.ADMIN, UserRole.TRAINER], // Only admin and trainer can see this
  },
  {
    value: "appearance",
    title: "Appearance",
    component: Appearance,
    icon: FiMoon,
    description: "Customize the look and feel of your interface",
  },
  {
    value: "danger-zone",
    title: "Danger zone",
    component: DeleteAccount,
    icon: FiTrash2,
    description: "Delete your account and associated data",
  },
]

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
})

function UserSettings() {
  const { user: currentUser } = useAuth()
  
  if (!currentUser) {
    return null
  }

  const userRole = getUserRole(currentUser)
  
  // Filter tabs based on user role
  const getFilteredTabs = () => {
    return tabsConfig.filter(tab => {
      // If tab has requiredRole, check if user has the required role
      if (tab.requiredRole) {
        return tab.requiredRole.includes(userRole) || currentUser.is_superuser
      }
      return true
    })
  }

  const finalTabs = getFilteredTabs()

  return (
    <Container maxW="4xl" py={8}>
      <Box mb={8}>
        <Heading size="lg" mb={2}>
          User Settings
        </Heading>
        <Text color="gray.500">
          Manage your account preferences and settings
        </Text>
      </Box>

      <Box bg="colors.card" rounded="lg" shadow="sm" overflow="hidden">
        <Tabs.Root defaultValue="my-profile">
          <Tabs.List
            bg="colors.background"
            borderBottom="1px"
            borderColor="colors.border"
            px={4}
          >
            {finalTabs.map((tab) => (
              <Tabs.Trigger
                key={tab.value}
                value={tab.value}
                px={4}
                py={3}
                gap={2}
                _selected={{
                  color: "teal.500",
                  borderBottom: "2px",
                  borderColor: "teal.500",
                }}
              >
                <Icon as={tab.icon} />
                {tab.title}
              </Tabs.Trigger>
            ))}
          </Tabs.List>

          <Box p={6}>
            {finalTabs.map((tab) => (
              <Tabs.Content key={tab.value} value={tab.value}>
                <Box mb={6}>
                  <Heading size="md" mb={2}>
                    {tab.title}
                  </Heading>
                  <Text color="gray.500" mb={6}>
                    {tab.description}
                  </Text>
                </Box>
                <tab.component />
              </Tabs.Content>
            ))}
          </Box>
        </Tabs.Root>
      </Box>
    </Container>
  )
}
