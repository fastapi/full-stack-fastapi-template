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
      <Card.Root>
        <Card.Header>
          <Heading size="lg">Gallery Status</Heading>
        </Card.Header>
        <Card.Body>
          <Text color="fg.muted">Loading...</Text>
        </Card.Body>
      </Card.Root>
    )
  }

  return (
    <Card.Root>
      <Card.Header>
        <Heading size="lg">Gallery Status</Heading>
      </Card.Header>
      <Card.Body>
        <Grid templateColumns="repeat(3, 1fr)" gap={4}>
          <Flex direction="column" align="center" p={3} borderRadius="md" bg="blue.200">
            <FiClock size={24} color="#2C5282" />
            <Text fontSize="2xl" fontWeight="bold" mt={2} color="blue.800">
              {pendingReview}
            </Text>
            <Text fontSize="xs" color="blue.700" textAlign="center">
              Pending Review
            </Text>
          </Flex>

          <Flex direction="column" align="center" p={3} borderRadius="md" bg="green.200">
            <FiCheckCircle size={24} color="#276749" />
            <Text fontSize="2xl" fontWeight="bold" mt={2} color="green.800">
              {approved}
            </Text>
            <Text fontSize="xs" color="green.700" textAlign="center">
              Approved
            </Text>
          </Flex>

          <Flex direction="column" align="center" p={3} borderRadius="md" bg="orange.200">
            <FiAlertCircle size={24} color="#9C4221" />
            <Text fontSize="2xl" fontWeight="bold" mt={2} color="orange.800">
              {changesRequested}
            </Text>
            <Text fontSize="xs" color="orange.700" textAlign="center">
              Changes Needed
            </Text>
          </Flex>
        </Grid>
      </Card.Body>
    </Card.Root>
  )
}