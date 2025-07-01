import { Box, Flex, Heading, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/recover-password")({
  component: RecoverPassword,
})

function RecoverPassword() {
  return (
    <Flex justify="center" align="center" h="100vh" bg="gray.50">
      <Box maxW="md" mx="auto" p={8} bg="white" borderRadius="md" shadow="md">
        <Heading size="lg" color="black" textAlign="center" mb={6}>
          Recover Password
        </Heading>
        <Text color="gray.600" textAlign="center">
          Password recovery form coming soon...
        </Text>
      </Box>
    </Flex>
  )
}

export default RecoverPassword
