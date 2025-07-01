import { Box, Flex, Heading, Text } from "@chakra-ui/react"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/signup")({
  component: SignUp,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({ to: "/" })
    }
  },
})

function SignUp() {
  return (
    <Flex justify="center" align="center" h="100vh" bg="gray.50">
      <Box maxW="md" mx="auto" p={8} bg="white" borderRadius="md" shadow="md">
        <Heading size="lg" color="black" textAlign="center" mb={6}>
          Sign Up
        </Heading>
        <Text color="gray.600" textAlign="center">
          Register form coming soon...
        </Text>
      </Box>
    </Flex>
  )
}

export default SignUp
