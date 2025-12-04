import {
  Badge,
  Box,
  Card,
  Container,
  Flex,
  Grid,
  Heading,
  HStack,
  IconButton,
  Separator,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import {
  FiArrowLeft,
  FiCalendar,
  FiImage,
  FiMessageSquare,
  FiUsers,
} from "react-icons/fi"

import { GalleriesService, ProjectsService } from "@/client"
import { AddComment } from "@/components/Projects/AddComment"
import { ClientAccessList } from "@/components/Projects/ClientAccessList"
import { CommentsList } from "@/components/Projects/CommentsList"
import { DeleteProject } from "@/components/Projects/DeleteProject"
import { EditProject } from "@/components/Projects/EditProject"
import { InviteClient } from "@/components/Projects/InviteClient"
import { ProjectTimeline } from "@/components/Projects/ProjectTimeline"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/projects/$projectId")({
  component: ProjectDetail,
  head: () => ({
    meta: [
      {
        title: 'Loading project details...',
      },
    ],
})
})

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
    case "pending":
      return "gray"
    default:
      return "gray"
  }
}

function getStatusLabel(status: string) {
  return status
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

function ProjectDetail() {
  const { projectId } = Route.useParams()
  const { user: currentUser } = useAuth()

  // Fetch project from backend
  const { data: project, isLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => ProjectsService.readProject({ id: projectId }),
  })

  // Set page title when project data is loaded
    if (project) {
      document.title = `${project.name}`
    }
  
  // Fetch galleries for this project
  const { data: galleriesData } = useQuery({
    queryKey: ["projectGalleries", projectId],
    queryFn: () => GalleriesService.readGalleries({ projectId: projectId }),
  })

  // Fetch comments for this project
  const { data: commentsData } = useQuery({
    queryKey: ["projectComments", projectId],
    queryFn: async () => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/comments/${projectId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) return { data: [], count: 0 }
      return response.json()
    },
  })

  if (isLoading) {
    return (
      <Container maxW="full" p={6}>
        <Text color="#64748B">Loading project...</Text>
      </Container>
    )
  }

  if (!project) {
    return (
      <Container maxW="full" p={6}>
        <Text color="#64748B">Project not found</Text>
        <Link to="/">
          <Text color="#1E3A8A" _hover={{ textDecoration: "underline" }}>← Back to Dashboard</Text>
        </Link>
      </Container>
    )
  }

  const galleries = galleriesData?.data || []

  // Get the project's gallery (should only be one per project)
  const projectGallery = galleries.length > 0 ? galleries[0] : null

  return (
    <Container maxW="full" p={6}>
      <Stack gap={6}>
        {/* Header with Back Button */}
        <Flex alignItems="center" gap={4}>
          <Link to="/">
            <IconButton variant="ghost" aria-label="Back to dashboard" color="#1E3A8A">
              <FiArrowLeft />
            </IconButton>
          </Link>
          <Box flex={1}>
            <Flex justifyContent="space-between" alignItems="start">
              <Box>
                <Heading size="2xl" mb={2} color="#1E3A8A" fontFamily="'Poppins', sans-serif">
                  {project.name}
                </Heading>
                <HStack fontSize="sm" color="#64748B">
                  <Text>Client: {project.client_name}</Text>
                  {project.client_email && (
                    <>
                      <Text>•</Text>
                      <Text>{project.client_email}</Text>
                    </>
                  )}
                </HStack>
              </Box>
              <Flex alignItems="center" gap={3}>
                {currentUser?.user_type === "team_member" && (
                  <>
                    <EditProject project={project} />
                    <DeleteProject project={project} />
                    <InviteClient projectId={projectId} />
                  </>
                )}
                <Badge
                  size="lg"
                  colorScheme={getStatusColor(project.status || "pending")}
                >
                  {getStatusLabel(project.status || "pending")}
                </Badge>
              </Flex>
            </Flex>
          </Box>
        </Flex>

        {/* Quick Stats */}
        <Grid templateColumns={{ base: "1fr", md: "repeat(4, 1fr)" }} gap={4}>
          <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <Box p={2} bg="#DBEAFE" borderRadius="md">
                  <FiCalendar size={20} color="#1E40AF" />
                </Box>
                <Box>
                  <Text fontSize="xs" color="#64748B" fontWeight="500">
                    Deadline
                  </Text>
                  <Text fontWeight="semibold" color="#1E3A8A">
                    {project.deadline || "Not set"}
                  </Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>

          <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <Box p={2} bg="#DBEAFE" borderRadius="md">
                  <FiImage size={20} color="#1E40AF" />
                </Box>
                <Box>
                  <Text fontSize="xs" color="#64748B" fontWeight="500">
                    Gallery Photos
                  </Text>
                  <Text fontWeight="semibold" color="#1E3A8A">
                    {projectGallery?.photo_count || 0}
                  </Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>

          <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <Box p={2} bg="#DBEAFE" borderRadius="md">
                  <FiMessageSquare size={20} color="#1E40AF" />
                </Box>
                <Box>
                  <Text fontSize="xs" color="#64748B" fontWeight="500">
                    Comments
                  </Text>
                  <Text fontWeight="semibold" color="#1E3A8A">{commentsData?.count || 0}</Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>

          <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <Box p={2} bg="#DBEAFE" borderRadius="md">
                  <FiUsers size={20} color="#1E40AF" />
                </Box>
                <Box>
                  <Text fontSize="xs" color="#64748B" fontWeight="500">
                    Progress
                  </Text>
                  <Text fontWeight="semibold" color="#1E3A8A">{project.progress}%</Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>
        </Grid>

        <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
          {/* Main Content */}
          <Stack gap={6}>
            {/* Project Details */}
            <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
              <Card.Header>
                <Heading size="lg" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Project Details</Heading>
              </Card.Header>
              <Card.Body>
                <Stack gap={4}>
                  {project.description && (
                    <>
                      <Box>
                        <Text fontWeight="semibold" mb={2} color="#1E3A8A">
                          Description
                        </Text>
                        <Text color="#1E293B">{project.description}</Text>
                      </Box>
                      <Separator borderColor="#E2E8F0" />
                    </>
                  )}

                  {project.budget && (
                    <>
                      <Box>
                        <Text fontWeight="semibold" mb={2} color="#1E3A8A">
                          Budget
                        </Text>
                        <Text color="#1E293B">{project.budget}</Text>
                      </Box>
                      <Separator borderColor="#E2E8F0" />
                    </>
                  )}

                  <Box>
                    <Text fontWeight="semibold" mb={2} color="#1E3A8A">
                      Project Timeline
                    </Text>
                    <Stack gap={2}>
                      {project.start_date && (
                        <Flex alignItems="center" gap={2}>
                          <Text fontSize="sm" color="#64748B">
                            Start Date:
                          </Text>
                          <Text fontSize="sm" color="#1E293B">{project.start_date}</Text>
                        </Flex>
                      )}
                      {project.deadline && (
                        <Flex alignItems="center" gap={2}>
                          <Text fontSize="sm" color="#64748B">
                            Deadline:
                          </Text>
                          <Text fontSize="sm" color="#1E293B">{project.deadline}</Text>
                        </Flex>
                      )}
                    </Stack>
                  </Box>

                  <Separator borderColor="#E2E8F0" />

                  <Box>
                    <Text fontWeight="semibold" mb={2} color="#1E3A8A">
                      Gallery
                    </Text>
                    {projectGallery ? (
                      <Flex alignItems="center" gap={2}>
                        <FiImage size={14} color="#1E40AF" />
                        <Text fontSize="sm" color="#1E293B">{projectGallery.name}</Text>
                        <Badge size="sm" colorScheme="blue">
                          {projectGallery.photo_count || 0} photos
                        </Badge>
                      </Flex>
                    ) : (
                      <Text fontSize="sm" color="#64748B">
                        No gallery yet
                      </Text>
                    )}
                  </Box>
                </Stack>
              </Card.Body>
            </Card.Root>

            {/* Timeline / Milestones */}
            <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
              <Card.Body>
                <ProjectTimeline project={project} />
              </Card.Body>
            </Card.Root>

            {/* Comments Section */}
            <CommentsList projectId={projectId} />
          </Stack>

          {/* Sidebar */}
          <Stack gap={6}>
            {/* Project Info */}
            <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
              <Card.Header>
                <Heading size="lg" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Project Info</Heading>
              </Card.Header>
              <Card.Body>
                <Stack gap={3}>
                  <Box>
                    <Text fontSize="xs" color="#64748B" mb={1} fontWeight="500">
                      Created
                    </Text>
                    <Text fontSize="sm" color="#1E293B">
                      {new Date(project.created_at).toLocaleDateString()}
                    </Text>
                  </Box>
                  <Box>
                    <Text fontSize="xs" color="#64748B" mb={1} fontWeight="500">
                      Last Updated
                    </Text>
                    <Text fontSize="sm" color="#1E293B">
                      {new Date(project.updated_at).toLocaleDateString()}
                    </Text>
                  </Box>
                </Stack>
              </Card.Body>
            </Card.Root>

            {/* Client Access List */}
            <ClientAccessList
              projectId={projectId}
              isTeamMember={currentUser?.user_type === "team_member"}
            />

            {/* Quick Actions */}
            <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
              <Card.Header>
                <Heading size="lg" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Quick Actions</Heading>
              </Card.Header>
              <Card.Body>
                <Stack gap={2}>
                  {projectGallery ? (
                    <Link
                      to="/galleries/$galleryId"
                      params={{ galleryId: projectGallery.id }}
                      style={{ textDecoration: "none", color: "inherit" }}
                    >
                      <Box
                        p={3}
                        borderWidth="1px"
                        borderColor="#E2E8F0"
                        borderRadius="md"
                        cursor="pointer"
                        bg="white"
                        _hover={{ bg: "#F8FAFC", borderColor: "#1E3A8A" }}
                        transition="all 0.2s"
                      >
                        <Flex alignItems="center" gap={2}>
                          <FiImage color="#1E40AF" />
                          <Text fontSize="sm" color="#1E293B">View Gallery</Text>
                        </Flex>
                      </Box>
                    </Link>
                  ) : (
                    <Box
                      p={3}
                      borderWidth="1px"
                      borderColor="#E2E8F0"
                      borderRadius="md"
                      opacity={0.5}
                      bg="white"
                    >
                      <Flex alignItems="center" gap={2}>
                        <FiImage color="#64748B" />
                        <Text fontSize="sm" color="#64748B">No Gallery Yet</Text>
                      </Flex>
                    </Box>
                  )}
                  <Box borderWidth="1px" borderColor="#E2E8F0" borderRadius="md" bg="white">
                    <AddComment projectId={projectId} />
                  </Box>
                  {currentUser?.user_type === "team_member" && (
                    <Box
                      p={3}
                      borderWidth="1px"
                      borderColor="#E2E8F0"
                      borderRadius="md"
                      cursor="pointer"
                      bg="white"
                      _hover={{ bg: "#F8FAFC", borderColor: "#1E3A8A" }}
                      transition="all 0.2s"
                    >
                      <Flex alignItems="center" gap={2}>
                        <FiUsers color="#1E40AF" />
                        <Text fontSize="sm" color="#1E293B">Manage Team</Text>
                      </Flex>
                    </Box>
                  )}
                </Stack>
              </Card.Body>
            </Card.Root>
          </Stack>
        </Grid>
      </Stack>
    </Container>
  )
}