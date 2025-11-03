import { Box, Card, Flex, Heading, Stack, Text } from "@chakra-ui/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { FiTrash2, FiUser } from "react-icons/fi"
import { Button } from "@/components/ui/button"
import useCustomToast from "@/hooks/useCustomToast"

interface ClientAccessListProps {
  projectId: string
  isTeamMember: boolean
}

export function ClientAccessList({ projectId, isTeamMember }: ClientAccessListProps) {
  const showToast = useCustomToast()
  const queryClient = useQueryClient()

  // Fetch project access list
  const { data: accessData, isLoading } = useQuery({
    queryKey: ["projectAccess", projectId],
    queryFn: async () => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, '')
      const response = await fetch(
        `${baseUrl}/api/v1/projects/${projectId}/access`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      )
      if (!response.ok) {
        throw new Error("Failed to fetch access list")
      }
      return response.json()
    },
  })

  const revokeMutation = useMutation({
    mutationFn: async (userId: string) => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, '')
      const response = await fetch(
        `${baseUrl}/api/v1/projects/${projectId}/access/${userId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      )
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to revoke access")
      }
      return response.json()
    },
    onSuccess: () => {
      showToast("Success", "Access revoked successfully", "success")
      queryClient.invalidateQueries({ queryKey: ["projectAccess", projectId] })
    },
    onError: (error: Error) => {
      showToast("Error", error.message, "error")
    },
  })

  if (isLoading) {
    return <Text>Loading...</Text>
  }

  const accessList = accessData?.data || []

  if (accessList.length === 0) {
    return (
      <Card.Root>
        <Card.Header>
          <Heading size="md">Invited Clients</Heading>
        </Card.Header>
        <Card.Body>
          <Text color="fg.muted">No clients invited yet</Text>
        </Card.Body>
      </Card.Root>
    )
  }

  return (
    <Card.Root>
      <Card.Header>
        <Heading size="md">Invited Clients</Heading>
      </Card.Header>
      <Card.Body>
        <Stack gap={3}>
          {accessList.map((access: any) => (
            <Flex
              key={access.id}
              p={3}
              borderWidth="1px"
              borderRadius="md"
              justifyContent="space-between"
              alignItems="center"
            >
              <Flex alignItems="center" gap={2}>
                <Box
                  p={2}
                  bg="purple.subtle"
                  borderRadius="full"
                >
                  <FiUser />
                </Box>
                <Box>
                  <Text fontWeight="semibold" fontSize="sm">
                    User ID: {access.user_id.substring(0, 8)}...
                  </Text>
                  <Text fontSize="xs" color="fg.muted">
                    Role: {access.role}
                  </Text>
                </Box>
              </Flex>
              {isTeamMember && (
                <Button
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                  onClick={() => revokeMutation.mutate(access.user_id)}
                  loading={revokeMutation.isPending}
                >
                  <FiTrash2 />
                  Revoke
                </Button>
              )}
            </Flex>
          ))}
        </Stack>
      </Card.Body>
    </Card.Root>
  )
}

