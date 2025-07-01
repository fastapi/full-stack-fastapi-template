import { Box, Flex, Heading, Text } from "@chakra-ui/react"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({ to: "/" })
    }
  },
})

function Login() {
  return (
    <Flex justify="center" align="center" h="100vh" bg="gray.50">
      <Box maxW="md" mx="auto" p={8} bg="white" borderRadius="md" shadow="md">
        <Heading size="lg" color="black" textAlign="center" mb={6}>
          Login
        </Heading>
        <Text color="gray.600" textAlign="center">
          Login form coming soon...
        </Text>
      </Box>
    </Flex>
  )
}

export default Login
