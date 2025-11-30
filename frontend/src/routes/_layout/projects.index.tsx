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
    return <Text>Loading projects...</Text>
  }

  if (projects.length === 0) {
    const isClient = currentUser?.user_type === "client"
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiFolder size={48} />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>No projects yet</EmptyState.Title>
            <EmptyState.Description>
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
    <Table.Root size={{ base: "sm", md: "md" }}>
      <Table.Header>
        <Table.Row>
          <Table.ColumnHeader>Project Name</Table.ColumnHeader>
          <Table.ColumnHeader>Client</Table.ColumnHeader>
          <Table.ColumnHeader>Status</Table.ColumnHeader>
          <Table.ColumnHeader>Deadline</Table.ColumnHeader>
          <Table.ColumnHeader>Progress</Table.ColumnHeader>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {projects.map((project: ProjectPublic) => (
          <Table.Row
            key={project.id}
            opacity={isPlaceholderData ? 0.5 : 1}
            _hover={{ bg: "bg.subtle", cursor: "pointer" }}
          >
            <Table.Cell>
              <Link
                to="/projects/$projectId"
                params={{ projectId: project.id }}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <Text fontWeight="semibold">{project.name}</Text>
              </Link>
            </Table.Cell>
            <Table.Cell>
              <Text fontSize="sm" color="fg.muted">
                {project.client_name}
              </Text>
            </Table.Cell>
            <Table.Cell>
              <Badge colorScheme={getStatusColor(project.status || "pending")}>
                {getStatusLabel(project.status || "pending")}
              </Badge>
            </Table.Cell>
            <Table.Cell>
              {project.deadline ? (
                <Flex alignItems="center" gap={1}>
                  <FiCalendar size={14} />
                  <Text fontSize="sm">{project.deadline}</Text>
                </Flex>
              ) : (
                <Text fontSize="sm" color="fg.muted">
                  —
                </Text>
              )}
            </Table.Cell>
            <Table.Cell>
              <Flex alignItems="center" gap={2}>
                <Box
                  w="100px"
                  h="6px"
                  bg="bg.muted"
                  borderRadius="full"
                  overflow="hidden"
                >
                  <Box
                    h="100%"
                    w={`${project.progress || 0}%`}
                    bg={
                      (project.progress || 0) === 100
                        ? "green.500"
                        : (project.progress || 0) >= 50
                          ? "blue.500"
                          : "orange.500"
                    }
                    transition="width 0.3s"
                  />
                </Box>
                <Text fontSize="sm" fontWeight="semibold">
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
  return (
    <Container maxW="full" p={6}>
      <Stack gap={6}>
        {/* Header */}
        <Flex justifyContent="space-between" alignItems="center">
          <Box>
            <Heading size="2xl" mb={2}>
              Projects
            </Heading>
            <Text color="fg.muted">Manage all your photography projects</Text>
          </Box>
          <CreateProject />
        </Flex>

        {/* Projects Table */}
        <Card.Root>
          <Card.Body p={0}>
            <ProjectsTable />
          </Card.Body>
        </Card.Root>
      </Stack>
    </Container>
  )
}
