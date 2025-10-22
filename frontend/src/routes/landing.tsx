import { Box, Button, Container, Flex, Heading, Text } from "@chakra-ui/react"
import { Link as RouterLink, createFileRoute } from "@tanstack/react-router"

import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/landing")({
  component: LandingPage,
})

function LandingPage() {
  const loggedIn = isLoggedIn()

  return (
    <Container
      maxW="6xl"
      minH="100vh"
      display="flex"
      flexDir="column"
      justifyContent="center"
      gap={16}
      py={12}
    >
      <Flex direction="column" gap={6}>
        <Heading as="h1" size="3xl">
          Seamless Arbitrage Insights
        </Heading>
        <Text fontSize="xl" color="fg.muted" maxW="2xl">
          Track market opportunities, monitor performance, and make decisions
          with confidence. All from a single, intuitive dashboard.
        </Text>
        <Flex gap={4} wrap="wrap">
          <RouterLink to={loggedIn ? "/dashboard" : "/signup"}>
            <Button size="lg" colorScheme="teal">
              {loggedIn ? "Go to Dashboard" : "Get Started"}
            </Button>
          </RouterLink>
          {!loggedIn && (
            <RouterLink to="/login">
              <Button size="lg" variant="outline">
                Log In
              </Button>
            </RouterLink>
          )}
        </Flex>
      </Flex>

      <Flex
        direction={{ base: "column", md: "row" }}
        gap={8}
        align="stretch"
      >
        <Feature
          title="Real-time Monitoring"
          description="Stay updated with live price tracking across your connected exchanges."
        />
        <Feature
          title="Actionable Alerts"
          description="Receive instant notifications when profitable spreads appear."
        />
        <Feature
          title="Collaboration Ready"
          description="Invite your team and share insights to coordinate faster trades."
        />
      </Flex>
    </Container>
  )
}

interface FeatureProps {
  title: string
  description: string
}

function Feature({ title, description }: FeatureProps) {
  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      p={6}
      bg="bg.surface"
      shadow="sm"
    >
      <Heading as="h2" size="md" mb={3}>
        {title}
      </Heading>
      <Text color="fg.muted">{description}</Text>
    </Box>
  )
}

export default LandingPage
