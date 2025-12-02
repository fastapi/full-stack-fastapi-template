import { Card, Flex, Grid, Heading, Text } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { FiCheckCircle, FiClock, FiAlertCircle } from "react-icons/fi"

export function GalleryStatusWidget() {
  const { data: galleriesData, isLoading } = useQuery({
    queryKey: ["allGalleries"],
    queryFn: async () => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/galleries/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) return { data: [], count: 0 }
      return response.json()
    },
  })

  const galleries = galleriesData?.data || []

  const pendingReview = galleries.filter((g: any) => g.status === "pending_review").length
  const approved = galleries.filter((g: any) => g.status === "approved").length
  const changesRequested = galleries.filter((g: any) => g.status === "changes_requested").length

  if (isLoading) {
    return (
      <Card.Root bg="white" borderColor="#E2E8F0">
        <Card.Header>
          <Heading size="lg" color="#1E3A8A">Gallery Status</Heading>
        </Card.Header>
        <Card.Body>
          <Text color="#64748B">Loading...</Text>
        </Card.Body>
      </Card.Root>
    )
  }

  return (
    <Card.Root bg="white" borderColor="#E2E8F0">
      <Card.Header>
        <Heading size="lg" color="#1E3A8A">Gallery Status</Heading>
      </Card.Header>
      <Card.Body>
        <Grid templateColumns="repeat(3, 1fr)" gap={4}>
          <Flex direction="column" align="center" p={3} borderRadius="md" bg="linear-gradient(135deg, #DBEAFE, #BFDBFE)">
            <FiClock size={24} color="#1E40AF" />
            <Text fontSize="2xl" fontWeight="bold" mt={2} color="#1E40AF">
              {pendingReview}
            </Text>
            <Text fontSize="xs" color="#1E40AF" textAlign="center">
              Pending Review
            </Text>
          </Flex>

          <Flex direction="column" align="center" p={3} borderRadius="md" bg="linear-gradient(135deg, #D1FAE5, #A7F3D0)">
            <FiCheckCircle size={24} color="#059669" />
            <Text fontSize="2xl" fontWeight="bold" mt={2} color="#059669">
              {approved}
            </Text>
            <Text fontSize="xs" color="#059669" textAlign="center">
              Approved
            </Text>
          </Flex>

          <Flex direction="column" align="center" p={3} borderRadius="md" bg="linear-gradient(135deg, #FED7AA, #FDBA74)">
            <FiAlertCircle size={24} color="#EA580C" />
            <Text fontSize="2xl" fontWeight="bold" mt={2} color="#EA580C">
              {changesRequested}
            </Text>
            <Text fontSize="xs" color="#EA580C" textAlign="center">
              Changes Needed
            </Text>
          </Flex>
        </Grid>
      </Card.Body>
    </Card.Root>
  )
}