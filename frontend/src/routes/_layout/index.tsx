import { Box, Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "../../hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl">
            Привет, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Добро пожаловать обратно, приятно видеть вас снова!</Text>
        </Box>
      </Container>
    </>
  )
}
