import { Box, Container, Flex, Heading, Text } from "@chakra-ui/react"
import { createFileRoute, Link as RouterLink, redirect } from "@tanstack/react-router"
import { FiBriefcase, FiUsers } from "react-icons/fi"

import { Button } from "@/components/ui/button"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/")({
  component: LandingPage,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/dashboard",
      })
    }
  },
})

function LandingPage() {
  return (
    <Flex h="100vh" alignItems="center" justifyContent="center">
      <Container maxW="6xl">
        <Flex direction="column" align="center" gap={8} py={20}>
        {/* Header */}
        <Box textAlign="center" mb={8}>
          <Heading
            size="6xl"
            bgGradient="to-r"
            gradientFrom="blue.400"
            gradientTo="purple.500"
            bgClip="text"
            mb={4}
          >
            Mosaic
          </Heading>
          <Text fontSize="2xl" color="fg.muted">
            Photography Project Management
          </Text>
          <Text fontSize="lg" color="fg.muted" mt={2}>
            Collaborate seamlessly on photography projects
          </Text>
        </Box>

        {/* Login Options */}
        <Flex
          direction={{ base: "column", md: "row" }}
          gap={8}
          w="100%"
          maxW="4xl"
          justify="center"
        >
          {/* Team Member Login Card */}
          <Box
            flex="1"
            p={8}
            borderWidth="2px"
            borderRadius="xl"
            bg="bg.subtle"
            transition="all 0.3s"
            _hover={{
              borderColor: "blue.500",
              transform: "translateY(-4px)",
              boxShadow: "lg",
            }}
          >
            <Flex direction="column" align="center" gap={4}>
              <Box
                p={4}
                bg="blue.subtle"
                borderRadius="full"
              >
                <FiUsers size={48} />
              </Box>
              <Heading size="xl">Team Member</Heading>
              <Text textAlign="center" color="fg.muted">
                Access your organization's projects, manage galleries, and collaborate with your team
              </Text>
              <RouterLink to="/team-login" style={{ width: "100%" }}>
                <Button
                  variant="solid"
                  colorScheme="blue"
                  size="lg"
                  w="100%"
                  mt={4}
                >
                  Team Login
                </Button>
              </RouterLink>
            </Flex>
          </Box>

          {/* Client Login Card */}
          <Box
            flex="1"
            p={8}
            borderWidth="2px"
            borderRadius="xl"
            bg="bg.subtle"
            transition="all 0.3s"
            _hover={{
              borderColor: "purple.500",
              transform: "translateY(-4px)",
              boxShadow: "lg",
            }}
          >
            <Flex direction="column" align="center" gap={4}>
              <Box
                p={4}
                bg="purple.subtle"
                borderRadius="full"
              >
                <FiBriefcase size={48} />
              </Box>
              <Heading size="xl">Client</Heading>
              <Text textAlign="center" color="fg.muted">
                View your projects, review galleries, and communicate with your photography team
              </Text>
              <RouterLink to="/client-login" style={{ width: "100%" }}>
                <Button
                  variant="solid"
                  colorScheme="purple"
                  size="lg"
                  w="100%"
                  mt={4}
                >
                  Client Login
                </Button>
              </RouterLink>
            </Flex>
          </Box>
        </Flex>

        {/* Sign Up Link */}
        <Box mt={8} textAlign="center">
          <Text fontSize="lg">
            Don't have an account?{" "}
            <RouterLink to="/signup" className="main-link">
              Sign Up
            </RouterLink>
          </Text>
        </Box>
        </Flex>
      </Container>
    </Flex>
  )
}
