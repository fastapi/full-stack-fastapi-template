import {
  Badge,
  Box,
  Card,
  Container,
  EmptyState,
  Flex,
  Heading,
  Stack,
  Table,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { FiCalendar, FiFolder } from "react-icons/fi"
import { z } from "zod"

import { type ProjectPublic, ProjectsService } from "@/client"
import { CreateProject } from "@/components/Projects/CreateProject"
import useAuth from "@/hooks/useAuth"

const projectsSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 10

function getProjectsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      ProjectsService.readProjects({
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["projects", { page }],
  }
}

export const Route = createFileRoute("/_layout/projects/")({
  component: Projects,
  validateSearch: (search) => projectsSearchSchema.parse(search),
  head: () => ({
    meta: [
      {
        title: 'Projects',
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

function ProjectsTable() {
  const { page } = Route.useSearch()
  const { user: currentUser } = useAuth()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getProjectsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const projects = data?.data ?? []

  if (isLoading) {
    return <Text color="#64748B">Loading projects...</Text>
  }

  if (projects.length === 0) {
    const isClient = currentUser?.user_type === "client"
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiFolder size={48} color="#64748B" />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title color="#1E3A8A">No projects yet</EmptyState.Title>
            <EmptyState.Description color="#64748B">
              {isClient
                ? "You don't have any projects yet. Please wait for your team to add you to a project."
                : "Create your first project to get started"}
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <Table.Root size={{ base: "sm", md: "md" }} bg = "white">
      <Table.Header>
        <Table.Row bg="#F8FAFC">
          <Table.ColumnHeader color="#1E3A8A" fontWeight="600">Project Name</Table.ColumnHeader>
          <Table.ColumnHeader color="#1E3A8A" fontWeight="600">Client</Table.ColumnHeader>
          <Table.ColumnHeader color="#1E3A8A" fontWeight="600">Status</Table.ColumnHeader>
          <Table.ColumnHeader color="#1E3A8A" fontWeight="600">Deadline</Table.ColumnHeader>
          <Table.ColumnHeader color="#1E3A8A" fontWeight="600">Progress</Table.ColumnHeader>
        </Table.Row>
      </Table.Header>
      <Table.Body bg = "white">
        {projects.map((project: ProjectPublic) => (
          <Table.Row
            key={project.id}
            opacity={isPlaceholderData ? 0.5 : 1}
            _hover={{ bg: "white", cursor: "pointer" }}
            borderBottomWidth="1px"
            borderBottomColor="#E2E8F0"
          >
            <Table.Cell bg = "white">
              <Link
                to="/projects/$projectId"
                params={{ projectId: project.id }}
                style={{ textDecoration: "none" }}
              >
                <Text fontWeight="semibold" color="#1E3A8A" _hover={{ textDecoration: "underline" }}>
                  {project.name}
                </Text>
              </Link>
            </Table.Cell>
            <Table.Cell bg = "white">
              <Text fontSize="sm" color="#64748B">
                {project.client_name}
              </Text>
            </Table.Cell>
            <Table.Cell bg = "white">
              <Badge colorScheme={getStatusColor(project.status || "pending")}>
                {getStatusLabel(project.status || "pending")}
              </Badge>
            </Table.Cell>
            <Table.Cell bg = "white">
              {project.deadline ? (
                <Flex alignItems="center" gap={1}>
                  <FiCalendar size={14} color="#64748B" />
                  <Text fontSize="sm" color="#1E293B">{project.deadline}</Text>
                </Flex>
              ) : (
                <Text fontSize="sm" color="#64748B">
                  —
                </Text>
              )}
            </Table.Cell>
            <Table.Cell bg = "white">
              <Flex alignItems="center" gap={2}>
                <Box
                  w="100px"
                  h="6px"
                  bg="#E2E8F0"
                  borderRadius="full"
                  overflow="hidden"
                >
                  <Box
                    h="100%"
                    w={`${project.progress || 0}%`}
                    bg={
                      (project.progress || 0) === 100
                        ? "#10B981"
                        : (project.progress || 0) >= 50
                          ? "#1E40AF"
                          : "#F59E0B"
                    }
                    transition="width 0.3s"
                  />
                </Box>
                <Text fontSize="sm" fontWeight="semibold" color="#1E293B">
                  {project.progress || 0}%
                </Text>
              </Flex>
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  )
}

function Projects() {
  const { user: currentUser } = useAuth()
  const isTeamMember = currentUser?.user_type === "team_member"
  const hasOrgId = Boolean(currentUser?.organization_id)

  return (
    <Container maxW="full" p={6}>
      <Stack gap={6}>
        {/* Header */}
        <Flex justifyContent="space-between" alignItems="center">
          <Box>
            <Heading size="2xl" mb={2} color="#1E3A8A" fontFamily="'Poppins', sans-serif">
              Projects
            </Heading>
            <Text color="#64748B">Manage all your photography projects</Text>
          </Box>
          {isTeamMember && hasOrgId && <CreateProject />}
        </Flex>

        {/* Projects Table */}
        <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
          <Card.Body p={0}>
            <ProjectsTable />
          </Card.Body>
        </Card.Root>
      </Stack>
    </Container>
  )
}