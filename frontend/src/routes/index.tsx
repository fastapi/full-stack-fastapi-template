import { Box, Container, Flex, Heading, Text } from "@chakra-ui/react"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
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
  head: () => ({
    meta: [
      {
        title: 'Mosaic',
      },
    ],
  })
})

function LandingPage() {
  return (
    <Flex h="100vh" alignItems="center" justifyContent="center" bg="#F8FAFC">
      <Container maxW="6xl">
        <Flex direction="column" align="center" gap={8} py={20}>
          {/* Header */}
          <Box textAlign="center" mb={8}>
            <Heading
              size="6xl"
              color="#1E3A8A"
              mb={4}
              fontFamily="'Poppins', sans-serif"
              fontWeight="700"
            >
              MOSAIC
            </Heading>
            <Text fontSize="2xl" color="#64748B" fontWeight="500">
              Photography Project Management
            </Text>
            <Text fontSize="lg" color="#64748B" mt={2}>
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
              borderColor="#E2E8F0"
              borderRadius="xl"
              bg="white"
              transition="all 0.3s"
              _hover={{
                borderColor: "#1E3A8A",
                transform: "translateY(-4px)",
                boxShadow: "0 8px 16px rgba(30, 58, 138, 0.15)",
              }}
            >
              <Flex direction="column" align="center" gap={4}>
                <Box 
                  p={4} 
                  bg="linear-gradient(135deg, #1E3A8A, #3B82F6)" 
                  borderRadius="full"
                  color="white"
                >
                  <FiUsers size={48} />
                </Box>
                <Heading 
                  size="xl" 
                  color="#1E3A8A"
                  fontFamily="'Poppins', sans-serif"
                >
                  Team Member
                </Heading>
                <Text textAlign="center" color="#64748B">
                  Access your organization's projects, manage galleries, and
                  collaborate with your team
                </Text>
                <RouterLink to="/team-login" style={{ width: "100%" }}>
                  <Button
                    size="lg"
                    w="100%"
                    mt={4}
                    bg="#1E3A8A"
                    color="white"
                    fontWeight="600"
                    _hover={{ bg: "#1E40AF" }}
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
              borderColor="#E2E8F0"
              borderRadius="xl"
              bg="white"
              transition="all 0.3s"
              _hover={{
                borderColor: "#F59E0B",
                transform: "translateY(-4px)",
                boxShadow: "0 8px 16px rgba(245, 158, 11, 0.15)",
              }}
            >
              <Flex direction="column" align="center" gap={4}>
                <Box 
                  p={4} 
                  bg="linear-gradient(135deg, #F59E0B, #FBBF24)" 
                  borderRadius="full"
                  color="#1E3A8A"
                >
                  <FiBriefcase size={48} />
                </Box>
                <Heading 
                  size="xl" 
                  color="#1E3A8A"
                  fontFamily="'Poppins', sans-serif"
                >
                  Client
                </Heading>
                <Text textAlign="center" color="#64748B">
                  View your projects, review galleries, and communicate with
                  your photography team
                </Text>
                <RouterLink to="/client-login" style={{ width: "100%" }}>
                  <Button
                    size="lg"
                    w="100%"
                    mt={4}
                    bg="#F59E0B"
                    color="#1E3A8A"
                    fontWeight="600"
                    _hover={{ bg: "#D97706" }}
                  >
                    Client Login
                  </Button>
                </RouterLink>
              </Flex>
            </Box>
          </Flex>

          {/* Sign Up Link */}
          <Box mt={8} textAlign="center">
            <Text fontSize="lg" color="#64748B">
              Don't have an account?{" "}
              <RouterLink 
                to="/signup" 
                style={{ 
                  color: "#1E3A8A", 
                  fontWeight: "600",
                  textDecoration: "underline"
                }}
              >
                Sign Up
              </RouterLink>
            </Text>
          </Box>
        </Flex>
      </Container>
    </Flex>
  )
}