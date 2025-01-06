import { RouterLink } from "@/components/ui/router-link"
import { Button, Container, Text } from "@chakra-ui/react"

const ErrorView = () => {
  return (
    <>
      <Container
        h="100vh"
        alignItems="stretch"
        justifyContent="center"
        textAlign="center"
        maxW="sm"
        centerContent
      >
        <Text fontSize="8xl" fontWeight="bold" lineHeight="1" mb={4}>
          500
        </Text>
        <Text fontSize="md">Oops!</Text>
        <Text fontSize="md">Something went wrong..</Text>
        <RouterLink to="/" asChild>
          <Button variant="outline" mt={4} asChild>
            Go back
          </Button>
        </RouterLink>
      </Container>
    </>
  )
}

export default ErrorView
