import { Box, Flex, Heading, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/reset-password")({
  component: ResetPassword,
})

function ResetPassword() {
  return (
    <Flex justify="center" align="center" h="100vh" bg="gray.50">
      <Box maxW="md" mx="auto" p={8} bg="white" borderRadius="md" shadow="md">
        <Heading size="lg" color="black" textAlign="center" mb={6}>
          Reset Password
        </Heading>
        <Text color="gray.600" textAlign="center">
          Reset password form coming soon...
        </Text>
      </Box>
    </Flex>
  )
}

export default ResetPassword
