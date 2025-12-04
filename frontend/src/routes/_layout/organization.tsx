import {
  Badge,
  Box,
  Card,
  Container,
  Flex,
  Grid,
  Heading,
  HStack,
  Input,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { FiBriefcase, FiTrash2, FiUserPlus, FiUsers } from "react-icons/fi"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"

import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/organization")({
  component: OrganizationPage,
  head: () => ({
    meta: [
      {
        title: 'Organization',
      },
    ],
})
})

function OrganizationPage() {
  const { user: currentUser } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [inviteEmail, setInviteEmail] = useState("")
  const [orgName, setOrgName] = useState("")

  const hasOrgId =
    currentUser &&
    "organization_id" in currentUser &&
    currentUser.organization_id

  // Fetch organization members
  const { data: membersData } = useQuery({
    queryKey: ["orgMembers"],
    queryFn: async () => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(
        `${baseUrl}/api/v1/users/organization-members`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        },
      )
      if (!response.ok) return { data: [], count: 0 }
      return response.json()
    },
    enabled: Boolean(hasOrgId),
  })

  // Fetch email invitations
  const { data: invitations } = useQuery({
    queryKey: ["invitations"],
    queryFn: async () => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      try {
        const response = await fetch(`${baseUrl}/api/v1/invitations/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        })
        if (!response.ok) return { data: [], count: 0 }
        return response.json()
      } catch (error) {
        console.error("Failed to fetch invitations:", error)
        return { data: [], count: 0 }
      }
    },
    enabled: Boolean(hasOrgId),
    retry: false,
  })

  // Send email invitation
  const inviteMutation = useMutation({
    mutationFn: async (email: string) => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/invitations/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to send invitation")
      }
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Invitation sent successfully")
      queryClient.invalidateQueries({ queryKey: ["invitations"] })
      setInviteEmail("")
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to send invitation")
    },
  })

  // Remove member mutation
  const removeMemberMutation = useMutation({
    mutationFn: async (userId: string) => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/users/${userId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) throw new Error("Failed to remove member")
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Member removed from organization")
      queryClient.invalidateQueries({ queryKey: ["orgMembers"] })
    },
    onError: () => {
      showErrorToast("Failed to remove member")
    },
  })

  // Create organization mutation
  const createOrgMutation = useMutation({
    mutationFn: async (name: string) => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/organizations/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          description: `Organization for ${currentUser?.full_name || currentUser?.email}`,
        }),
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

  const handleInvite = () => {
    if (inviteEmail?.includes("@")) {
      inviteMutation.mutate(inviteEmail)
    }
  }

  const handleCreateOrg = () => {
    if (orgName && orgName.trim().length > 0) {
      createOrgMutation.mutate(orgName)
    }
  }

  // Show create organization form if user has no org
  if (currentUser && !hasOrgId) {
    return (
      <Container maxW="md" centerContent py={20}>
        <Card.Root w="full" bg="white" borderColor="#E2E8F0" borderWidth="1px">
          <Card.Header textAlign="center">
            <Flex justifyContent="center" mb={4}>
              <Box p={4} bg="#DBEAFE" borderRadius="full">
                <FiBriefcase size={48} color="#1E40AF" />
              </Box>
            </Flex>
            <Heading size="xl" mb={2} color="#1E3A8A" fontFamily="'Poppins', sans-serif">
              Create Your Organization
            </Heading>
            <Text color="#64748B">
              You need to create an organization before you can invite team
              members.
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

  return (
    <Container maxW="full" p={6}>
      <Stack gap={6}>
        <Box>
          <Heading size="2xl" mb={2} color="#1E3A8A" fontFamily="'Poppins', sans-serif">
            Organization Management
          </Heading>
          <Text color="#64748B">Manage your team members and invitations</Text>
        </Box>

        {/* Invite by Email */}
        <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
          <Card.Header>
            <Heading size="lg" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Authorize Email</Heading>
            <Text fontSize="sm" color="#64748B">
              Pre-authorize an email to join your organization. When they sign
              up, they'll be automatically added.
            </Text>
          </Card.Header>
          <Card.Body>
            <Flex gap={3}>
              <Field flex={1}>
                <Input
                  placeholder="colleague@example.com"
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                />
              </Field>
              <Button
                colorScheme="blue"
                onClick={handleInvite}
                loading={inviteMutation.isPending}
                disabled={!inviteEmail || !inviteEmail.includes("@")}
              >
                <FiUserPlus />
                Authorize Email
              </Button>
            </Flex>
          </Card.Body>
        </Card.Root>

        <Grid templateColumns={{ base: "1fr", lg: "repeat(2, 1fr)" }} gap={6}>
          {/* Current Members */}
          <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
            <Card.Header>
              <Flex justifyContent="space-between" alignItems="center">
                <Box>
                  <Heading size="lg" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Team Members</Heading>
                  <Text fontSize="sm" color="#64748B">
                    {membersData?.count || 0} member(s)
                  </Text>
                </Box>
                <FiUsers size={24} color="#1E40AF" />
              </Flex>
            </Card.Header>
            <Card.Body>
              {!membersData?.data || membersData.data.length === 0 ? (
                <Text color="#64748B">No team members yet</Text>
              ) : (
                <Stack gap={3}>
                  {membersData.data.map((member: any) => (
                    <Flex
                      key={member.id}
                      justifyContent="space-between"
                      alignItems="center"
                      p={3}
                      borderWidth="1px"
                      borderColor="#E2E8F0"
                      borderRadius="md"
                      bg="white"
                    >
                      <Box>
                        <HStack>
                          <Text fontWeight="semibold" color="#1E3A8A">
                            {member.full_name || member.email}
                          </Text>
                          {member.is_superuser && (
                            <Badge colorScheme="purple">Admin</Badge>
                          )}
                          {member.id === currentUser?.id && (
                            <Badge colorScheme="blue">You</Badge>
                          )}
                        </HStack>
                        <Text fontSize="sm" color="#64748B">
                          {member.email}
                        </Text>
                      </Box>
                      {member.id !== currentUser?.id && (
                        <Button
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => removeMemberMutation.mutate(member.id)}
                        >
                          <FiTrash2 />
                        </Button>
                      )}
                    </Flex>
                  ))}
                </Stack>
              )}
            </Card.Body>
          </Card.Root>

          {/* Email Invitations */}
          <Card.Root bg="white" borderColor="#E2E8F0" borderWidth="1px">
            <Card.Header>
              <Heading size="lg" color="#1E3A8A" fontFamily="'Poppins', sans-serif">Authorized Emails</Heading>
              <Text fontSize="sm" color="#64748B">
                Pre-authorized emails that can join
              </Text>
            </Card.Header>
            <Card.Body>
              {!invitations?.data || invitations.data.length === 0 ? (
                <Text color="#64748B">No authorized emails</Text>
              ) : (
                <Stack gap={3}>
                  {invitations.data.map((inv: any) => (
                    <Flex
                      key={inv.id}
                      justifyContent="space-between"
                      alignItems="center"
                      p={3}
                      borderWidth="1px"
                      borderColor="#E2E8F0"
                      borderRadius="md"
                      bg="white"
                    >
                      <Box>
                        <Text fontWeight="semibold" color="#1E3A8A">{inv.email}</Text>
                        <Text fontSize="sm" color="#64748B">
                          Added {new Date(inv.created_at).toLocaleDateString()}
                        </Text>
                      </Box>
                      <Badge colorScheme="green">Authorized</Badge>
                    </Flex>
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