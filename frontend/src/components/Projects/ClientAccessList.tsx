import { Box, Card, Flex, Heading, Stack, Text } from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { FiTrash2, FiUser } from "react-icons/fi"
import { Button } from "@/components/ui/button"
import useCustomToast from "@/hooks/useCustomToast"

interface ClientAccessListProps {
  projectId: string
  isTeamMember: boolean
}

export function ClientAccessList({
  projectId,
  isTeamMember,
}: ClientAccessListProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Fetch project access list (now returns array with user data)
  const { data: accessList, isLoading } = useQuery({
    queryKey: ["projectAccess", projectId],
    queryFn: async () => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(
        `${baseUrl}/api/v1/projects/${projectId}/access`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        },
      )
      if (!response.ok) {
        throw new Error("Failed to fetch access list")
      }
      const data = await response.json()
      // Backend now returns array directly
      return Array.isArray(data) ? data : []
    },
  })

  const revokeMutation = useMutation({
    mutationFn: async (userId: string) => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(
        `${baseUrl}/api/v1/projects/${projectId}/access/${userId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        },
      )
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to revoke access")
      }
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Access revoked successfully")
      queryClient.invalidateQueries({ queryKey: ["projectAccess", projectId] })
    },
    onError: (error: Error) => {
      showErrorToast(error.message)
    },
  })

  if (isLoading) {
    return <Text color="#64748B">Loading...</Text>
  }

  if (!accessList || !Array.isArray(accessList) || accessList.length === 0) {
    return (
      <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
        <Card.Header>
          <Heading size="md" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Invited Clients</Heading>
        </Card.Header>
        <Card.Body>
          <Text color="#64748B">No clients invited yet</Text>
        </Card.Body>
      </Card.Root>
    )
  }

  return (
    <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
      <Card.Header>
        <Heading size="md" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Invited Clients</Heading>
      </Card.Header>
      <Card.Body>
        <Stack gap={3}>
          {accessList.map((access: any) => (
            <Flex
              key={access.id}
              p={3}
              borderWidth="1px"
              borderColor="#E2E8F0"
              borderRadius="md"
              bg="white"
              justifyContent="space-between"
              alignItems="center"
            >
              <Flex alignItems="center" gap={2}>
                <Box p={2} bg="#FED7AA" borderRadius="full">
                  <FiUser color="#EA580C" />
                </Box>
                <Box>
                  <Text fontWeight="semibold" fontSize="sm" color="#1E3A8A">
                    {access.user?.full_name || "No name"}
                  </Text>
                  <Text fontSize="xs" color="#64748B">
                    {access.user?.email}
                  </Text>
                  <Text fontSize="xs" color="#64748B">
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