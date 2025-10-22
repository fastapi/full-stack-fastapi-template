import { Box, Button, Container, Flex, Heading, Text } from "@chakra-ui/react"
import { Link as RouterLink, createFileRoute } from "@tanstack/react-router"

import { isLoggedIn } from "@/hooks/useAuth"
import { OddsCard } from "@/components/Landing/OddsCard"
import { ColorModeButton } from "@/components/ui/color-mode"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/landing")({
  component: LandingPage,
})

function LandingPage() {
  const loggedIn = isLoggedIn()
  const { showSuccessToast } = useCustomToast()

  const featuredMarket = {
    homeTeam: "Tampines Rovers",
    awayTeam: "Pohang Steelers",
    marketLabel: "Moneyline",
    home: {
      value: "+640",
      book: {
        name: "BC.GAME",
        logoUrl: "https://dummyimage.com/60x18/eeeeee/333333&text=BC.GAME",
      },
    },
    draw: {
      value: "+350",
      book: {
        name: "MOSTBET",
        logoUrl: "https://dummyimage.com/64x18/eeeeee/333333&text=MOSTBET",
      },
    },
    away: {
      value: "-129",
      book: {
        name: "betway",
        logoUrl: "https://dummyimage.com/64x18/eeeeee/333333&text=betway",
      },
    },
  }

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
        <Flex justify="flex-end">
          <ColorModeButton aria-label="Toggle color mode" size="sm" />
        </Flex>
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

      <Flex direction="column" gap={6}>
        <Heading as="h2" size="lg">
          Track markets effortlessly
        </Heading>
        <Text color="fg.muted">
          Explore a unified view of the best odds across your books. Select a side to
          fast-track it into your workflow.
        </Text>
        <OddsCard
          {...featuredMarket}
          onSelect={(market) =>
            showSuccessToast(
              `Selected ${market.toUpperCase()} market from the featured matchup.`,
            )
          }
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
