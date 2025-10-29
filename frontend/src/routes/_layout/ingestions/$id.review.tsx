import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Spinner,
  Text,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { z } from "zod"
import { IngestionsService } from "@/client"
import { PDFViewer } from "@/components/Ingestions/PDFViewer"

// Search params validation schema
const reviewSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/ingestions/$id/review")({
  component: PDFReviewPage,
  validateSearch: (search) => reviewSearchSchema.parse(search),
})

function getIngestionQueryOptions({ id }: { id: string }) {
  return {
    queryFn: () => IngestionsService.getIngestion({ id }),
    queryKey: ["ingestion", id],
    staleTime: 5 * 60 * 1000, // 5 minutes (presigned URLs valid for 7 days)
    refetchOnWindowFocus: false, // Don't refetch on window focus for presigned URLs
  }
}

function PDFReviewPage() {
  const { id } = Route.useParams()
  const { page = 1 } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })

  const { data: ingestion, isLoading, error } = useQuery(
    getIngestionQueryOptions({ id }),
  )

  /**
   * Handle page change - update URL query param using replaceState
   * (replaceState for high-frequency updates, no history entry per page)
   */
  const handlePageChange = (newPage: number) => {
    // Validate page number
    if (ingestion && (newPage < 1 || newPage > (ingestion.page_count || 1))) {
      return // Ignore invalid page numbers
    }

    // Update URL with new page number using replaceState (no history entry)
    const url = new URL(window.location.href)
    url.searchParams.set("page", String(newPage))
    window.history.replaceState(null, "", url.toString())
  }

  /**
   * Navigate back to ingestions list
   */
  const handleBackToList = () => {
    navigate({ to: "/ingestions" })
  }

  // Loading state
  if (isLoading) {
    return (
      <Container maxW="full" py={8} textAlign="center">
        <Spinner size="xl" />
        <Text mt={4}>Loading extraction...</Text>
      </Container>
    )
  }

  // Error states
  if (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error"
    const is404 = errorMessage.includes("404") || errorMessage.includes("not found")
    const is403 = errorMessage.includes("403") || errorMessage.includes("permission")

    if (is404) {
      return (
        <Container maxW="full" py={8}>
          <Box bg="yellow.50" p={6} borderRadius="md" borderWidth="1px" borderColor="yellow.200">
            <Heading size="md" color="yellow.800" mb={2}>
              Extraction Not Found
            </Heading>
            <Text color="yellow.700" mb={4}>
              The extraction you're looking for doesn't exist or has been deleted.
            </Text>
            <Button onClick={handleBackToList} colorPalette="yellow">
              Go to Ingestions List
            </Button>
          </Box>
        </Container>
      )
    }

    if (is403) {
      return (
        <Container maxW="full" py={8}>
          <Box bg="red.50" p={6} borderRadius="md" borderWidth="1px" borderColor="red.200">
            <Heading size="md" color="red.800" mb={2}>
              Permission Denied
            </Heading>
            <Text color="red.700" mb={4}>
              You don't have permission to view this extraction.
            </Text>
            <Button onClick={handleBackToList} colorPalette="red">
              Go to Ingestions List
            </Button>
          </Box>
        </Container>
      )
    }

    // Network or other errors
    return (
      <Container maxW="full" py={8}>
        <Box bg="orange.50" p={6} borderRadius="md" borderWidth="1px" borderColor="orange.200">
          <Heading size="md" color="orange.800" mb={2}>
            Failed to Load
          </Heading>
          <Text color="orange.700" mb={4}>
            Failed to load the extraction. Please check your connection and try again.
          </Text>
          <Text fontSize="sm" color="orange.600" mb={4}>
            Error: {errorMessage}
          </Text>
          <Flex gap={3}>
            <Button
              onClick={() => window.location.reload()}
              colorPalette="orange"
            >
              Retry
            </Button>
            <Button onClick={handleBackToList} variant="outline">
              Go to Ingestions List
            </Button>
          </Flex>
        </Box>
      </Container>
    )
  }

  // Missing extraction data
  if (!ingestion) {
    return (
      <Container maxW="full" py={8}>
        <Box bg="red.50" p={4} borderRadius="md">
          <Text color="red.600">No extraction data available.</Text>
        </Box>
      </Container>
    )
  }

  // Check for presigned URL
  if (!ingestion.presigned_url) {
    return (
      <Container maxW="full" py={8}>
        <Box bg="red.50" p={6} borderRadius="md" borderWidth="1px" borderColor="red.200">
          <Heading size="md" color="red.800" mb={2}>
            PDF Not Available
          </Heading>
          <Text color="red.700" mb={4}>
            The PDF file is not available for this extraction.
          </Text>
          <Button onClick={handleBackToList} colorPalette="red">
            Go to Ingestions List
          </Button>
        </Box>
      </Container>
    )
  }

  // Success - render PDF viewer
  return (
    <Container maxW="full" h="100vh" p={0}>
      {/* Header with filename and back navigation */}
      <Flex
        p={4}
        borderBottom="1px"
        borderColor="gray.200"
        align="center"
        gap={4}
        bg="white"
      >
        <Button onClick={handleBackToList} variant="ghost" size="sm">
          ← Back to List
        </Button>
        <Heading size="sm" flex={1}>
          {ingestion.filename || "Untitled PDF"}
        </Heading>
        <Text fontSize="sm" color="gray.600">
          {ingestion.page_count || 0} {ingestion.page_count === 1 ? "page" : "pages"}
        </Text>
      </Flex>

      {/* PDF Viewer */}
      <Box h="calc(100vh - 73px)" overflow="auto" bg="gray.50" p={4}>
        <PDFViewer
          presignedUrl={ingestion.presigned_url}
          defaultPage={page}
          onPageChange={handlePageChange}
          onError={(err) => {
            console.error("PDF Viewer Error:", err)
          }}
        />
      </Box>
    </Container>
  )
}
