// **User Settings Page (settings.tsx)**
// This file defines the route and page for managing user settings in the application.
// It uses Chakra UI for styling and layout, TanStack React Query for data fetching, and React Router for routing.
// The page provides a tabbed interface for the user to update their profile, change their password, adjust appearance settings, or delete their account.

import {
  Container,
  Heading,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
} from "@chakra-ui/react" // Chakra UI components for layout, styling, and tabs functionality
import { useQueryClient } from "@tanstack/react-query" // TanStack React Query hook for accessing the query cache
import { createFileRoute } from "@tanstack/react-router" // TanStack React Router for route management

import type { UserPublic } from "../../client" // Type for the current user data from the backend
import Appearance from "../../components/UserSettings/Appearance" // Component for updating appearance settings
import ChangePassword from "../../components/UserSettings/ChangePassword" // Component for changing the user's password
import DeleteAccount from "../../components/UserSettings/DeleteAccount" // Component for deleting the user's account
import UserInformation from "../../components/UserSettings/UserInformation" // Component for viewing and editing user information

// Configuration for the tabs on the settings page
const tabsConfig = [
  { title: "My profile", component: UserInformation }, // Tab for user information
  { title: "Password", component: ChangePassword }, // Tab for changing password
  { title: "Appearance", component: Appearance }, // Tab for appearance settings
  { title: "Danger zone", component: DeleteAccount }, // Tab for account deletion (Danger zone)
]

// Define the route for the "/_layout/settings" path
export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings, // The component that will render for this route
})

// Main UserSettings component
function UserSettings() {
  const queryClient = useQueryClient() // Access React Query's cache to get the current user data
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"]) // Fetch the current user from the query cache

  // Modify tabs based on whether the user is a superuser or not
  const finalTabs = currentUser?.is_superuser
    ? tabsConfig.slice(0, 3) // Remove the "Danger zone" tab for non-superusers
    : tabsConfig

  return (
    <Container maxW="full">
      {/* Page heading */}
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        User Settings
      </Heading>

      {/* Tabs for different settings categories */}
      <Tabs variant="enclosed">
        {/* Tab list (top of the tabbed interface) */}
        <TabList>
          {finalTabs.map((tab, index) => (
            <Tab key={index}>{tab.title}</Tab> // Render each tab title
          ))}
        </TabList>

        {/* Tab panels (content for each tab) */}
        <TabPanels>
          {finalTabs.map((tab, index) => (
            <TabPanel key={index}>
              {/* Render the component corresponding to the selected tab */}
              <tab.component />
            </TabPanel>
          ))}
        </TabPanels>
      </Tabs>
    </Container>
  )
}