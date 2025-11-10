import { 
  Badge, 
  Box, 
  Card, 
  Container, 
  Flex, 
  Grid, 
  Heading, 
  HStack, 
  Stack, 
  Text,
  Separator,
  IconButton,
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

import { ProjectsService, GalleriesService } from "@/client"
import useAuth from "@/hooks/useAuth"
import { InviteClient } from "@/components/Projects/InviteClient"
import { ClientAccessList } from "@/components/Projects/ClientAccessList"
import { EditProject } from "@/components/Projects/EditProject"
import { DeleteProject } from "@/components/Projects/DeleteProject"

export const Route = createFileRoute("/_layout/projects/$projectId")({
  component: ProjectDetail,
})

function getStatusColor(status: string) {
  switch (status) {
    case "planning": return "blue"
    case "in_progress": return "orange"
    case "review": return "purple"
    case "completed": return "green"
    case "pending": return "gray"
    default: return "gray"
  }
}

function getStatusLabel(status: string) {
  return status.split("_").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ")
}

function ProjectDetail() {
  const { projectId } = Route.useParams()
  const { user: currentUser } = useAuth()
  
  // Fetch project from backend
  const { data: project, isLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => ProjectsService.readProject({ id: projectId }),
  })

  // Fetch galleries for this project
  const { data: galleriesData } = useQuery({
    queryKey: ["projectGalleries", projectId],
    queryFn: () => GalleriesService.readGalleries({ projectId: projectId }),
  })

  if (isLoading) {
    return (
      <Container maxW="full" p={6}>
        <Text>Loading project...</Text>
      </Container>
    )
  }

  if (!project) {
    return (
      <Container maxW="full" p={6}>
        <Text>Project not found</Text>
        <Link to="/">
          <Text color="blue.500">← Back to Dashboard</Text>
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
            <IconButton variant="ghost" aria-label="Back to dashboard">
              <FiArrowLeft />
            </IconButton>
          </Link>
          <Box flex={1}>
            <Flex justifyContent="space-between" alignItems="start">
              <Box>
                <Heading size="2xl" mb={2}>
                  {project.name}
                </Heading>
                <HStack fontSize="sm" color="fg.muted">
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
                <Badge size="lg" colorScheme={getStatusColor(project.status || 'pending')}>
                  {getStatusLabel(project.status || 'pending')}
                </Badge>
              </Flex>
            </Flex>
          </Box>
        </Flex>

        {/* Quick Stats */}
        <Grid templateColumns={{ base: "1fr", md: "repeat(4, 1fr)" }} gap={4}>
          <Card.Root>
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <FiCalendar size={20} />
                <Box>
                  <Text fontSize="xs" color="fg.muted">Deadline</Text>
                  <Text fontWeight="semibold">{project.deadline || "Not set"}</Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>

          <Card.Root>
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <FiImage size={20} />
                <Box>
                  <Text fontSize="xs" color="fg.muted">Gallery Photos</Text>
                  <Text fontWeight="semibold">{projectGallery?.photo_count || 0}</Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>

          <Card.Root>
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <FiMessageSquare size={20} />
                <Box>
                  <Text fontSize="xs" color="fg.muted">Comments</Text>
                  <Text fontWeight="semibold">0</Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>

          <Card.Root>
            <Card.Body>
              <Flex alignItems="center" gap={3}>
                <FiUsers size={20} />
                <Box>
                  <Text fontSize="xs" color="fg.muted">Progress</Text>
                  <Text fontWeight="semibold">{project.progress}%</Text>
                </Box>
              </Flex>
            </Card.Body>
          </Card.Root>
        </Grid>

        <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
          {/* Main Content */}
          <Stack gap={6}>
            {/* Project Details */}
            <Card.Root>
              <Card.Header>
                <Heading size="lg">Project Details</Heading>
              </Card.Header>
              <Card.Body>
                <Stack gap={4}>
                  {project.description && (
                    <>
                      <Box>
                        <Text fontWeight="semibold" mb={2}>Description</Text>
                        <Text>{project.description}</Text>
                      </Box>
                      <Separator />
                    </>
                  )}
                  
                  {project.budget && (
                    <>
                      <Box>
                        <Text fontWeight="semibold" mb={2}>Budget</Text>
                        <Text>{project.budget}</Text>
                      </Box>
                      <Separator />
                    </>
                  )}
                  
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Project Timeline</Text>
                    <Stack gap={2}>
                      {project.start_date && (
                        <Flex alignItems="center" gap={2}>
                          <Text fontSize="sm" color="fg.muted">Start Date:</Text>
                          <Text fontSize="sm">{project.start_date}</Text>
                        </Flex>
                      )}
                      {project.deadline && (
                        <Flex alignItems="center" gap={2}>
                          <Text fontSize="sm" color="fg.muted">Deadline:</Text>
                          <Text fontSize="sm">{project.deadline}</Text>
                        </Flex>
                      )}
                    </Stack>
                  </Box>

                  <Separator />

                  <Box>
                    <Text fontWeight="semibold" mb={2}>Gallery</Text>
                    {projectGallery ? (
                      <Flex alignItems="center" gap={2}>
                        <FiImage size={14} />
                        <Text fontSize="sm">{projectGallery.name}</Text>
                        <Badge size="sm" colorScheme="blue">{projectGallery.photo_count || 0} photos</Badge>
                      </Flex>
                    ) : (
                      <Text fontSize="sm" color="fg.muted">No gallery yet</Text>
                    )}
                  </Box>
                </Stack>
              </Card.Body>
            </Card.Root>

            {/* Timeline / Milestones */}
            <Card.Root>
              <Card.Header>
                <Heading size="lg">Project Progress</Heading>
              </Card.Header>
              <Card.Body>
                <Stack gap={4}>
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Status</Text>
                    <Badge size="lg" colorScheme={getStatusColor(project.status || 'pending')}>
                      {getStatusLabel(project.status || 'pending')}
                    </Badge>
                  </Box>
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Completion</Text>
                    <Flex alignItems="center" gap={3}>
                      <Box flex={1} h="8px" bg="bg.muted" borderRadius="full" overflow="hidden">
                        <Box
                          h="100%"
                          w={`${project.progress || 0}%`}
                          bg={(project.progress || 0) === 100 ? "green.500" : (project.progress || 0) >= 50 ? "blue.500" : "orange.500"}
                          transition="width 0.3s"
                        />
                      </Box>
                      <Text fontWeight="semibold">{project.progress || 0}%</Text>
                    </Flex>
                  </Box>
                </Stack>
              </Card.Body>
            </Card.Root>
          </Stack>

          {/* Sidebar */}
          <Stack gap={6}>
            {/* Project Info */}
            <Card.Root>
              <Card.Header>
                <Heading size="lg">Project Info</Heading>
              </Card.Header>
              <Card.Body>
                <Stack gap={3}>
                  <Box>
                    <Text fontSize="xs" color="fg.muted" mb={1}>Created</Text>
                    <Text fontSize="sm">{new Date(project.created_at).toLocaleDateString()}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="xs" color="fg.muted" mb={1}>Last Updated</Text>
                    <Text fontSize="sm">{new Date(project.updated_at).toLocaleDateString()}</Text>
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
            <Card.Root>
              <Card.Header>
                <Heading size="lg">Quick Actions</Heading>
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
                        borderRadius="md"
                        cursor="pointer"
                        _hover={{ bg: "bg.subtle" }}
                      >
                        <Flex alignItems="center" gap={2}>
                          <FiImage />
                          <Text fontSize="sm">View Gallery</Text>
                        </Flex>
                      </Box>
                    </Link>
                  ) : (
                    <Box 
                      p={3} 
                      borderWidth="1px" 
                      borderRadius="md"
                      opacity={0.5}
                    >
                      <Flex alignItems="center" gap={2}>
                        <FiImage />
                        <Text fontSize="sm">No Gallery Yet</Text>
                      </Flex>
                    </Box>
                  )}
                  <Box 
                    p={3} 
                    borderWidth="1px" 
                    borderRadius="md"
                    cursor="pointer"
                    _hover={{ bg: "bg.subtle" }}
                  >
                    <Flex alignItems="center" gap={2}>
                      <FiMessageSquare />
                      <Text fontSize="sm">Add Comment</Text>
                    </Flex>
                  </Box>
                  {currentUser?.user_type === "team_member" && (
                    <Box 
                      p={3} 
                      borderWidth="1px" 
                      borderRadius="md"
                      cursor="pointer"
                      _hover={{ bg: "bg.subtle" }}
                    >
                      <Flex alignItems="center" gap={2}>
                        <FiUsers />
                        <Text fontSize="sm">Manage Team</Text>
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
