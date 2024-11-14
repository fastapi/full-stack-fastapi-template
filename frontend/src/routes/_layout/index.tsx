// **Dashboard Page (index.tsx)**
// This file sets up the dashboard route at the root of the "/_layout" path.
// It uses Chakra UI for layout and styling, and a custom `useAuth` hook to fetch the current user's data.
// The dashboard displays a personalized greeting based on the user's full name or email.
// The map and model selection section is added for the geospatial components.

import { Box, Container, Text } from "@chakra-ui/react" // Chakra UI components for layout and text styling
import { createFileRoute } from "@tanstack/react-router" // React Router to define the file route
import useAuth from "../../hooks/useAuth" // Custom hook for accessing the current user's authentication data
import MainContent from "../../components/Geospatial/MapApp" // Import the MainContent component from your MapApp.tsx

// Define the route for the dashboard, which renders the Dashboard component
export const Route = createFileRoute("/_layout/")({
  component: Dashboard, // The component to render for this route
})

// The Dashboard component displays a personalized greeting for the logged-in user
// and includes the map, model selection, and parameter menus for the geospatial features.
function Dashboard() {
  const { user: currentUser } = useAuth() // Using custom hook to access current user data

  return (
    <>
      <Container maxW="full"> 
        {/* Dashboard Greeting Section */}
        <Box pt={12} m={4}>
          <Text fontSize="2xl">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Welcome back, nice to see you again!</Text> {/* A welcome message */}
        </Box>

        {/* Map and Model Selection Section */}
        <Box pt={8} m={4}>
          {/* MainContent handles the map and model selection logic */}
          {/* Updated: Removed onCloseScenario prop */}
          <MainContent />
        </Box>
      </Container>
    </>
  )
}
