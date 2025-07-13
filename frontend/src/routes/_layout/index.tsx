import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  Grid,
  Heading,
  Icon,
  SimpleGrid,
  Text,
  VStack,
  HStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import {
  FiCpu,
  FiMessageSquare,
  FiPlus,
  FiUsers,
  FiActivity,
  FiTrendingUp,
  FiShield,
  FiClock,
  FiBarChart,
} from "react-icons/fi"

import { AiSoulsService, ChatService, CounselorService, UtilsService, type AISoulEntityWithUserInteraction } from "@/client"
import { Skeleton } from "@/components/ui/skeleton"
import useAuth from "@/hooks/useAuth"
import { getUserRole, hasPermission, UserRole } from "@/utils/roles"

interface DashboardAnalytics {
  totalChatMessages: number
  totalTrainingMessages: number
  recentActivity: number
  pendingReviews: number
  urgentCases: number
  highPriorityCases: number
  totalUsers: number
  activeAiSouls: number
}

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()

  const userRole = getUserRole(currentUser || null)
  const isAdmin = hasPermission(currentUser || null, "manage_users")
  const isCounselor = hasPermission(currentUser || null, "access_counselor_queue")
  const isTrainer = hasPermission(currentUser || null, "access_training")

  // Fetch AI Souls
  const { data: aiSouls, isLoading: isLoadingAiSouls } = useQuery<AISoulEntityWithUserInteraction[]>({
    queryKey: ["ai-souls"],
    queryFn: () => AiSoulsService.getAiSouls(),
  })

  // Fetch Analytics Data (only for admins/counselors)
  const { data: systemHealth, isLoading: isLoadingSystemHealth } = useQuery({
    queryKey: ["system-health"],
    queryFn: () => UtilsService.getSystemHealth(),
    enabled: isAdmin,
  })

  // Fetch Counselor Queue (for counselors)
  const { data: counselorQueue, isLoading: isLoadingCounselorQueue } = useQuery({
    queryKey: ["counselor-queue"],
    queryFn: () => CounselorService.getCounselorQueue(),
    enabled: isCounselor,
  })

  // Redirect regular users to AI souls page
  useEffect(() => {
    if (currentUser && userRole === UserRole.USER) {
      navigate({ to: "/ai-souls", replace: true })
    }
  }, [currentUser, userRole, navigate])

  // Don't render dashboard for regular users (after all hooks are called)
  if (currentUser && userRole === UserRole.USER) {
    return null
  }

  // Calculate analytics with loading states
  const analytics: DashboardAnalytics = {
    totalChatMessages: (systemHealth as any)?.database_stats?.total_chat_messages || 0,
    totalTrainingMessages: (systemHealth as any)?.database_stats?.total_training_messages || 0,
    recentActivity: (systemHealth as any)?.database_stats?.recent_activity || 0,
    pendingReviews: (counselorQueue as any)?.total_count || 0,
    urgentCases: (counselorQueue as any)?.urgent_count || 0,
    highPriorityCases: (counselorQueue as any)?.high_priority_count || 0,
    totalUsers: (systemHealth as any)?.database_stats?.total_users || 0,
    activeAiSouls: aiSouls?.filter((s) => s.is_active).length || 0,
  }

  // Calculate total conversations (not total messages)
  // 1 conversation = 1 user message + 1 AI response pair
  const totalConversations = Math.ceil((analytics.totalChatMessages + analytics.totalTrainingMessages) / 2)
  const hasAiSouls = (aiSouls?.length || 0) > 0

  return (
    <Container maxW="8xl" py={8} px={{ base: 4, md: 8 }} fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">
      <VStack align="stretch" gap={8} w="100%" px={8} pb={8} maxW="100%" overflow="hidden">
        {/* Welcome Section */}
        <Box
          p={8}
          bg="linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)"
          borderRadius="xl"
          border="1px"
          borderColor="blue.200"
        >
          <Flex justify="space-between" align="center" wrap="wrap" gap={4}>
            <VStack align="start" gap={3}>
              <Heading size="2xl" color="blue.800" fontWeight="700" letterSpacing="-0.025em">
                Welcome back, {currentUser?.full_name || "User"}!
              </Heading>
              <Text color="blue.700" fontSize="lg" fontWeight="400" lineHeight="1.6">
                {hasAiSouls 
                  ? "Manage your AI Soul Entities, track interactions, and monitor performance."
                  : "Get started by creating your first AI Soul Entity to begin your journey."
                }
              </Text>
              <HStack>
                <Badge colorScheme="blue" px={3} py={1} borderRadius="full" fontWeight="600">
                  {userRole.charAt(0).toUpperCase() + userRole.slice(1)} Account
                </Badge>
                {hasAiSouls && (
                  <Badge colorScheme="green" px={3} py={1} borderRadius="full" fontWeight="600">
                    {aiSouls?.length} AI Soul{(aiSouls?.length || 0) > 1 ? 's' : ''}
                  </Badge>
                )}
              </HStack>
            </VStack>
          </Flex>
        </Box>

        {/* Core Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={6}>
          <Box
            p={6}
            bg="white"
            shadow="lg"
            rounded="xl"
            border="1px"
            borderColor="blue.100"
            _hover={{ shadow: "xl", borderColor: "blue.200", transform: "translateY(-2px)" }}
            transition="all 0.3s ease"
          >
            <VStack align="start" gap={2}>
              <Text color="gray.600" fontSize="sm" fontWeight="600" letterSpacing="0.025em">AI Souls</Text>
              {isLoadingAiSouls ? (
                <Skeleton height="40px" width="60px" />
              ) : (
                <Heading size="2xl" color="blue.600" fontWeight="700">
                  {aiSouls?.length || 0}
                </Heading>
              )}
              <Text color="gray.500" fontSize="sm" fontWeight="500">
                {analytics.activeAiSouls} active
              </Text>
            </VStack>
          </Box>

          <Box
            p={6}
            bg="white"
            shadow="lg"
            rounded="xl"
            border="1px"
            borderColor="green.100"
            _hover={{ shadow: "xl", borderColor: "green.200", transform: "translateY(-2px)" }}
            transition="all 0.3s ease"
          >
            <VStack align="start" gap={2}>
              <Text color="gray.600" fontSize="sm" fontWeight="600" letterSpacing="0.025em">Total Conversations</Text>
              {isAdmin && isLoadingSystemHealth ? (
                <Skeleton height="40px" width="80px" />
              ) : (
                <Heading size="2xl" color="green.600" fontWeight="700">
                  {totalConversations.toLocaleString()}
                </Heading>
              )}
              <Text color="gray.500" fontSize="sm" fontWeight="500">
                {Math.ceil(analytics.recentActivity / 2)} in last hour
              </Text>
            </VStack>
          </Box>

          {isCounselor && (
            <Box
              p={6}
              bg="white"
              shadow="lg"
              rounded="xl"
              border="1px"
              borderColor="orange.100"
              _hover={{ shadow: "xl", borderColor: "orange.200", transform: "translateY(-2px)" }}
              transition="all 0.3s ease"
            >
              <VStack align="start" gap={2}>
                <Text color="gray.600" fontSize="sm" fontWeight="600" letterSpacing="0.025em">Pending Reviews</Text>
                {isLoadingCounselorQueue ? (
                  <Skeleton height="40px" width="40px" />
                ) : (
                  <Heading size="2xl" color="orange.600" fontWeight="700">
                    {analytics.pendingReviews}
                  </Heading>
                )}
                <Text color="gray.500" fontSize="sm" fontWeight="500">
                  {analytics.urgentCases} urgent
                </Text>
              </VStack>
            </Box>
          )}

          {isAdmin && (
            <Box
              p={6}
              bg="white"
              shadow="lg"
              rounded="xl"
              border="1px"
              borderColor="purple.100"
              _hover={{ shadow: "xl", borderColor: "purple.200", transform: "translateY(-2px)" }}
              transition="all 0.3s ease"
            >
              <VStack align="start" gap={2}>
                <Text color="gray.600" fontSize="sm" fontWeight="600" letterSpacing="0.025em">Total Users</Text>
                {isLoadingSystemHealth ? (
                  <Skeleton height="40px" width="40px" />
                ) : (
                  <Heading size="2xl" color="purple.600" fontWeight="700">
                    {analytics.totalUsers}
                  </Heading>
                )}
                <Text color="gray.500" fontSize="sm" fontWeight="500">
                  Platform users
                </Text>
              </VStack>
            </Box>
          )}
        </SimpleGrid>

        {/* Detailed Analytics (Admin/Counselor only) */}
        {(isAdmin || isCounselor) && (
          <SimpleGrid columns={{ base: 1, lg: 2 }} gap={6}>
            <Box
              bg="white"
              shadow="lg"
              rounded="xl"
              p={6}
              border="1px"
              borderColor="gray.100"
            >
              <Heading size="md" mb={4} color="gray.700" fontWeight="600">
                <Icon as={FiBarChart} mr={2} />
                Activity Breakdown
              </Heading>
              <VStack align="stretch" gap={4}>
                <Flex justify="space-between" align="center">
                  <HStack>
                    <Icon as={FiMessageSquare} color="blue.500" />
                    <Text fontWeight="500">Chat Messages</Text>
                  </HStack>
                  {isLoadingSystemHealth ? (
                    <Skeleton height="20px" width="60px" />
                  ) : (
                    <Text fontWeight="700" color="blue.600">
                      {analytics.totalChatMessages.toLocaleString()}
                    </Text>
                  )}
                </Flex>
                <Flex justify="space-between" align="center">
                  <HStack>
                    <Icon as={FiTrendingUp} color="green.500" />
                    <Text fontWeight="500">Training Messages</Text>
                  </HStack>
                  {isLoadingSystemHealth ? (
                    <Skeleton height="20px" width="60px" />
                  ) : (
                    <Text fontWeight="700" color="green.600">
                      {analytics.totalTrainingMessages.toLocaleString()}
                    </Text>
                  )}
                </Flex>
                <Flex justify="space-between" align="center">
                  <HStack>
                    <Icon as={FiActivity} color="orange.500" />
                    <Text fontWeight="500">Recent Activity</Text>
                  </HStack>
                  {isLoadingSystemHealth ? (
                    <Skeleton height="20px" width="80px" />
                  ) : (
                    <Text fontWeight="700" color="orange.600">
                      {analytics.recentActivity} msgs/hour
                    </Text>
                  )}
                </Flex>
              </VStack>
            </Box>

            {isCounselor && (
              <Box
                bg="white"
                shadow="lg"
                rounded="xl"
                p={6}
                border="1px"
                borderColor="gray.100"
              >
                <Heading size="md" mb={4} color="gray.700" fontWeight="600">
                  <Icon as={FiShield} mr={2} />
                  Safety Overview
                </Heading>
                <VStack align="stretch" gap={4}>
                  <Flex justify="space-between" align="center">
                    <HStack>
                      <Icon as={FiClock} color="red.500" />
                      <Text fontWeight="500">Urgent Cases</Text>
                    </HStack>
                    {isLoadingCounselorQueue ? (
                      <Skeleton height="24px" width="40px" />
                    ) : (
                      <Badge colorScheme="red" fontSize="md" px={3} py={1} fontWeight="600">
                        {analytics.urgentCases}
                      </Badge>
                    )}
                  </Flex>
                  <Flex justify="space-between" align="center">
                    <HStack>
                      <Icon as={FiClock} color="orange.500" />
                      <Text fontWeight="500">High Priority</Text>
                    </HStack>
                    {isLoadingCounselorQueue ? (
                      <Skeleton height="24px" width="40px" />
                    ) : (
                      <Badge colorScheme="orange" fontSize="md" px={3} py={1} fontWeight="600">
                        {analytics.highPriorityCases}
                      </Badge>
                    )}
                  </Flex>
                  <Flex justify="space-between" align="center">
                    <HStack>
                      <Icon as={FiUsers} color="blue.500" />
                      <Text fontWeight="500">Total Pending</Text>
                    </HStack>
                    {isLoadingCounselorQueue ? (
                      <Skeleton height="24px" width="40px" />
                    ) : (
                      <Badge colorScheme="blue" fontSize="md" px={3} py={1} fontWeight="600">
                        {analytics.pendingReviews}
                      </Badge>
                    )}
                  </Flex>
                </VStack>
              </Box>
            )}
          </SimpleGrid>
        )}

        {/* Quick Actions */}
        <Box
          bg="white"
          shadow="lg"
          rounded="xl"
          p={8}
          border="1px"
          borderColor="gray.100"
        >
          <Heading size="xl" mb={8} color="gray.700" fontWeight="600">
            Quick Actions
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={6}>
            {hasPermission(currentUser || null, "create_souls") && (
            <Button
              bg="#437057"
              color="white"
              _hover={{ bg: "#2F5249", transform: "translateY(-2px)" }}
              size="lg"
              height="140px"
              borderRadius="16px"
              flexDirection="column"
              gap={3}
              fontWeight="600"
              transition="all 0.3s ease"
              shadow="md"
              _active={{ transform: "translateY(0)" }}
              onClick={() => navigate({ to: "/create-soul" })}
            >
              <Icon as={FiPlus} boxSize={8} />
              <Text fontSize="lg">Create New</Text>
              <Text fontSize="sm" fontWeight="400" opacity="0.9">
                AI Soul Entity
              </Text>
            </Button>
            )}

            <Button
              variant="outline"
              borderColor="#437057"
              color="#437057"
              _hover={{ bg: "#437057", color: "white", transform: "translateY(-2px)" }}
              onClick={() => navigate({ to: "/ai-souls" })}
              size="lg"
              height="140px"
              borderRadius="16px"
              flexDirection="column"
              gap={3}
              fontWeight="600"
              transition="all 0.3s ease"
              shadow="md"
              _active={{ transform: "translateY(0)" }}
            >
              <Icon as={FiCpu} boxSize={8} />
              <Text fontSize="lg">Manage</Text>
              <Text fontSize="sm" fontWeight="400">
                AI Souls
              </Text>
            </Button>

            {isCounselor && (
              <Button
                variant="outline"
                borderColor="#e53e3e"
                color="#e53e3e"
                _hover={{ bg: "#e53e3e", color: "white", transform: "translateY(-2px)" }}
                onClick={() => navigate({ to: "/counselor" })}
                size="lg"
                height="140px"
                borderRadius="16px"
                flexDirection="column"
                gap={3}
                fontWeight="600"
                transition="all 0.3s ease"
                shadow="md"
                _active={{ transform: "translateY(0)" }}
              >
                <Icon as={FiShield} boxSize={8} />
                <Text fontSize="lg">Counselor</Text>
                <Text fontSize="sm" fontWeight="400">
                  Review Queue
                </Text>
              </Button>
            )}

            {isAdmin && (
              <Button
                variant="outline"
                onClick={() => navigate({ to: "/admin" })}
                size="lg"
                height="140px"
                flexDirection="column"
                gap={3}
                borderColor="#6b46c1"
                color="#6b46c1"
                _hover={{ bg: "#6b46c1", color: "white", transform: "translateY(-2px)" }}
                borderRadius="16px"
                fontWeight="600"
                transition="all 0.3s ease"
                shadow="md"
                _active={{ transform: "translateY(0)" }}
              >
                <Icon as={FiUsers} boxSize={8} />
                <Text fontSize="lg">Admin</Text>
                <Text fontSize="sm" fontWeight="400">
                  Dashboard
                </Text>
              </Button>
            )}
          </SimpleGrid>
        </Box>

        {/* Recent AI Souls */}
        {hasAiSouls && (
          <Box
            bg="white"
            shadow="lg"
            rounded="xl"
            p={6}
            border="1px"
            borderColor="gray.100"
          >
            <Flex justify="space-between" align="center" mb={6}>
              <Heading size="md" color="gray.700" fontWeight="600">
                Your AI Souls
              </Heading>
              <Button
                variant="ghost"
                color="#437057"
                onClick={() => navigate({ to: "/ai-souls" })}
                fontWeight="500"
              >
                View All
              </Button>
            </Flex>
            <SimpleGrid columns={{ base: 1, md: 2, xl: 3 }} gap={4}>
              {aiSouls?.slice(0, 6).map((soul) => (
                <Box 
                  key={soul.id}
                  p={5}
                  border="1px solid"
                  borderColor="gray.200"
                  borderRadius="12px"
                  _hover={{ borderColor: "#437057", shadow: "md", transform: "translateY(-1px)" }}
                  transition="all 0.3s ease"
                >
                  <VStack align="start" gap={3}>
                    <Flex justify="space-between" align="start" width="100%">
                      <Text fontWeight="600" truncate fontSize="lg">{soul.name}</Text>
                      <Badge colorScheme={soul.is_active ? "green" : "gray"} size="sm" fontWeight="500">
                        {soul.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </Flex>
                    <Box>
                      <Text fontSize="sm" color="gray.600" lineClamp={2} lineHeight="1.5">
                        {soul.description || soul.specializations}
                      </Text>
                    </Box>
                    <HStack justify="space-between" width="100%">
                      <Text fontSize="sm" color="gray.500" fontWeight="500">
                        {Math.ceil((soul.interaction_count || 0) / 2)} conversations
                      </Text>
                      <Button
                        size="sm"
                        color="#437057"
                        _hover={{ bg: "#437057", color: "white" }}
                        variant="ghost"
                        fontWeight="500"
                        borderRadius="8px"
                        onClick={() =>
                          navigate({
                            to: "/chat",
                            search: { soul: soul.id },
                          })
                        }
                      >
                        Chat
                      </Button>
                    </HStack>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </Box>
        )}
      </VStack>
    </Container>
  )
}

export default Dashboard
