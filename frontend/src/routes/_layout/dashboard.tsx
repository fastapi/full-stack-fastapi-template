import { Badge, Box, Card, Container, Flex, Grid, Heading, HStack, Stack, Text } from "@chakra-ui/react"
import { Button } from "@/components/ui/button"
import { createFileRoute, Link } from "@tanstack/react-router"
import { FiCalendar, FiCheckCircle, FiClock, FiFolder, FiUsers, FiBriefcase } from "react-icons/fi"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

import useAuth from "@/hooks/useAuth"
import { ProjectsService, type ProjectPublic } from "@/client"
import { CreateProject } from "@/components/Projects/CreateProject"
import useCustomToast from "@/hooks/useCustomToast"
import { Input } from "@chakra-ui/react"
import { Field } from "@/components/ui/field"

export const Route = createFileRoute("/_layout/dashboard")({
  component: Dashboard,
})

// Helper to calculate days until deadline
function getDaysUntil(dateString: string): number {
  const deadline = new Date(dateString)
  const today = new Date()
  const diffTime = deadline.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

function StatCard({ icon: Icon, label, value, colorScheme }: { icon: any; label: string; value: number; colorScheme: string }) {
  return (
    <Card.Root>
      <Card.Body>
        <Flex alignItems="center" gap={4}>
          <Box p={3} bg={`${colorScheme}.subtle`} borderRadius="lg">
            <Icon size={24} />
          </Box>
          <Box>
            <Text fontSize="2xl" fontWeight="bold">
              {value}
            </Text>
            <Text fontSize="sm" color="fg.muted">
              {label}
            </Text>
          </Box>
        </Flex>
      </Card.Body>
    </Card.Root>
  )
}

function getStatusColor(status: string) {
  switch (status) {
    case "planning":
      return "blue"
    case "in_progress":
      return "orange"
    case "review":
      return "purple"
    case "completed":
      return "green"
    default:
      return "gray"
  }
}

function getStatusLabel(status: string) {
  return status.split("_").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ")
}

function Dashboard() {
  const { user: currentUser } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [orgName, setOrgName] = useState("")
  
  // Check if team member has organization
  const hasOrganization = Boolean(currentUser?.user_type === "client" || currentUser?.organization_id)
  const hasOrgId = currentUser && 'organization_id' in currentUser && currentUser.organization_id

  // Create organization mutation (must be before any returns)
  const createOrgMutation = useMutation({
    mutationFn: async (name: string) => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/organizations/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, description: `Organization for ${currentUser?.full_name || currentUser?.email}` }),
      })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to create organization")
      }
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Organization created successfully!")
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      setOrgName("")
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to create organization")
    },
  })

  // Fetch dashboard stats (only for team members with organization)
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboardStats"],
    queryFn: () => ProjectsService.readDashboardStats(),
    enabled: Boolean(currentUser?.user_type === "team_member" && hasOrgId),
  })

  // Fetch recent projects (only if has organization)
  const { data: projectsData, isLoading: projectsLoading } = useQuery({
    queryKey: ["recentProjects"],
    queryFn: () => ProjectsService.readProjects({ skip: 0, limit: 5 }),
    enabled: hasOrganization,
  })

  const recentProjects = projectsData?.data?.slice(0, 3) || []
  
  // Get projects with upcoming deadlines (within 2 weeks, not completed)
  type DeadlineItem = {
    id: string
    project: string
    date: string
    daysLeft: number
  }

  const upcomingDeadlines = (projectsData?.data || [])
    .filter((p: ProjectPublic) => p.deadline && p.status !== "completed")
    .map((p: ProjectPublic): DeadlineItem => ({
      id: p.id,
      project: p.name,
      date: p.deadline!,
      daysLeft: getDaysUntil(p.deadline!),
    }))
    .filter((d: DeadlineItem) => d.daysLeft >= 0 && d.daysLeft <= 14)
    .sort((a: DeadlineItem, b: DeadlineItem) => a.daysLeft - b.daysLeft)
    .slice(0, 3)

  const handleCreateOrg = () => {
    if (orgName && orgName.trim().length > 0) {
      createOrgMutation.mutate(orgName)
    }
  }

  const isLoading = statsLoading || projectsLoading

  if (isLoading) {
    return (
      <Container maxW="full" p={6}>
        <Text>Loading...</Text>
      </Container>
    )
  }

  // Show create organization form for team members without organization
  if (currentUser?.user_type === "team_member" && !hasOrgId) {
    return (
      <Container maxW="md" centerContent py={20}>
        <Card.Root w="full">
          <Card.Header textAlign="center">
            <Flex justifyContent="center" mb={4}>
              <FiBriefcase size={48} />
            </Flex>
            <Heading size="xl" mb={2}>
              Create Your Organization
            </Heading>
            <Text color="fg.muted">
              You need to create an organization before you can manage projects and invite team members.
            </Text>
          </Card.Header>
          <Card.Body>
            <Stack gap={4}>
              <Field label="Organization Name" required>
                <Input
                  placeholder="My Studio"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleCreateOrg()}
                />
              </Field>
              <Button
                colorScheme="blue"
                w="full"
                onClick={handleCreateOrg}
                loading={createOrgMutation.isPending}
                disabled={!orgName || orgName.trim().length === 0}
              >
                <FiBriefcase />
                Create Organization
              </Button>
            </Stack>
          </Card.Body>
        </Card.Root>
      </Container>
    )
  }

  // Show message for clients with no projects
  if (currentUser?.user_type === "client" && (!projectsData?.data || projectsData.data.length === 0)) {
    return (
      <Container maxW="md" centerContent py={20}>
        <Card.Root w="full">
          <Card.Header textAlign="center">
            <Flex justifyContent="center" mb={4}>
              <FiFolder size={48} />
            </Flex>
            <Heading size="xl" mb={2}>
              Welcome!
            </Heading>
            <Text color="fg.muted" fontSize="lg">
              You don't have any projects yet. Please wait for your team to add you to a project.
            </Text>
          </Card.Header>
        </Card.Root>
      </Container>
    )
  }
  
  return (
    <Container maxW="full" p={6}>
      <Stack gap={6}>
        {/* Welcome Section */}
        <Flex justifyContent="space-between" alignItems="start">
          <Box>
            <Heading size="2xl" mb={2}>
              Welcome back, {currentUser?.full_name || currentUser?.email?.split('@')[0]}! 👋
            </Heading>
            <Text color="fg.muted">Here's what's happening with your projects today.</Text>
          </Box>
          {currentUser?.user_type === "team_member" && currentUser?.organization_id && (
            <CreateProject />
          )}
        </Flex>

        {/* Stats Cards - Only for team members */}
        {currentUser?.user_type === "team_member" && (
          <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(4, 1fr)" }} gap={4}>
            <StatCard icon={FiFolder} label="Active Projects" value={stats?.active_projects || 0} colorScheme="blue" />
            <StatCard icon={FiClock} label="Upcoming Deadlines" value={stats?.upcoming_deadlines || 0} colorScheme="orange" />
            <StatCard icon={FiUsers} label="Team Members" value={stats?.team_members || 0} colorScheme="purple" />
            <StatCard icon={FiCheckCircle} label="Completed This Month" value={stats?.completed_this_month || 0} colorScheme="green" />
          </Grid>
        )}

        <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
          {/* Recent Projects */}
          <Card.Root>
            <Card.Header>
              <Heading size="lg">Recent Projects</Heading>
            </Card.Header>
            <Card.Body>
              {recentProjects.length === 0 ? (
                <Text color="fg.muted">No projects yet. Create your first project!</Text>
              ) : (
                <Stack gap={4}>
                  {recentProjects.map((project: ProjectPublic) => (
                    <Link
                      key={project.id}
                      to="/projects/$projectId"
                      params={{ projectId: project.id }}
                      style={{ textDecoration: "none", color: "inherit" }}
                    >
                      <Box
                        p={4}
                        borderWidth="1px"
                        borderRadius="md"
                        transition="all 0.2s"
                        _hover={{ 
                          bg: "bg.subtle", 
                          cursor: "pointer",
                          transform: "translateY(-2px)",
                          boxShadow: "md"
                        }}
                      >
                        <Flex justifyContent="space-between" alignItems="start" mb={2}>
                          <Box flex={1}>
                            <Heading size="sm" mb={1}>
                              {project.name}
                            </Heading>
                            <Text fontSize="sm" color="fg.muted">
                              Client: {project.client_name}
                            </Text>
                          </Box>
                          <Badge colorScheme={getStatusColor(project.status || 'pending')}>
                            {getStatusLabel(project.status || 'pending')}
                          </Badge>
                        </Flex>
                        {project.deadline && (
                          <HStack mt={3} fontSize="sm" color="fg.muted">
                            <Flex alignItems="center" gap={1}>
                              <FiCalendar />
                              <Text>{project.deadline}</Text>
                            </Flex>
                          </HStack>
                        )}
                      </Box>
                    </Link>
                  ))}
                </Stack>
              )}
            </Card.Body>
          </Card.Root>

          {/* Upcoming Deadlines */}
          <Card.Root>
            <Card.Header>
              <Heading size="lg">Upcoming Deadlines</Heading>
            </Card.Header>
            <Card.Body>
              {upcomingDeadlines.length === 0 ? (
                <Text color="fg.muted">No upcoming deadlines in the next 2 weeks.</Text>
              ) : (
                <Stack gap={3}>
                  {upcomingDeadlines.map((deadline: DeadlineItem) => (
                    <Box key={deadline.id} p={3} borderWidth="1px" borderRadius="md">
                      <Text fontWeight="semibold" fontSize="sm" mb={1}>
                        {deadline.project}
                      </Text>
                      <Flex justifyContent="space-between" alignItems="center">
                        <Text fontSize="xs" color="fg.muted">
                          {deadline.date}
                        </Text>
                        <Badge colorScheme={deadline.daysLeft <= 5 ? "red" : "blue"} fontSize="xs">
                          {deadline.daysLeft} days left
                        </Badge>
                      </Flex>
                    </Box>
                  ))}
                </Stack>
              )}
            </Card.Body>
          </Card.Root>
        </Grid>
      </Stack>
    </Container>
  )
}
