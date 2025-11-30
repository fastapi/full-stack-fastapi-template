import { Box, Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"
// import DragonCurve from "@/components/Dashboard/DragonCurve"
import CoralGrowth from "@/components/Dashboard/CoralGrowth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <Container maxW="full">
      <Box pt={12} m={4}>
        <Text fontSize="2xl" truncate maxW="sm">
          Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
        </Text>
        <Text>Welcome back, nice to see you again!</Text>
      </Box>
      <Box m={4}>
        <CoralGrowth />
        {/* <DragonCurve /> */}
      </Box>
    </Container>
  )
}
