import {
  Badge,
  Box,
  Container,
  Flex,
  Grid,
  Heading,
  IconButton,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { FiArrowLeft, FiCalendar, FiImage, FiUser } from "react-icons/fi"

import { GalleriesService } from "@/client"

export const Route = createFileRoute("/_layout/galleries/$galleryId")({
  component: GalleryDetail,
  loader: async ({ params }) => {
    // Pre-fetch gallery data
    return await GalleriesService.readGallery({ id: params.galleryId })
  },
})

function getStatusColor(status: string) {
  switch (status) {
    case "draft":
      return "gray"
    case "processing":
      return "orange"
    case "published":
      return "green"
    default:
      return "gray"
  }
}

function getStatusLabel(status: string) {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

function GalleryDetail() {
  const { galleryId } = Route.useParams()

  // Fetch gallery details
  const { data: gallery, isLoading } = useQuery({
    queryKey: ["gallery", galleryId],
    queryFn: () => GalleriesService.readGallery({ id: galleryId }),
  })

  if (isLoading) {
    return (
      <Container maxW="full" p={6}>
        <Text>Loading gallery...</Text>
      </Container>
    )
  }

  if (!gallery) {
    return (
      <Container maxW="full" p={6}>
        <Text>Gallery not found</Text>
        <Link to="/galleries">
          <Text color="blue.500">← Back to Galleries</Text>
        </Link>
      </Container>
    )
  }

  return (
    <Container maxW="full" p={6}>
      <Stack gap={6}>
        {/* Header with Back Button */}
        <Flex alignItems="center" gap={4}>
          <Link to="/galleries">
            <IconButton variant="ghost" aria-label="Back to galleries">
              <FiArrowLeft />
            </IconButton>
          </Link>
          <Box flex={1}>
            <Flex justifyContent="space-between" alignItems="start">
              <Box>
                <Heading size="2xl" mb={2}>
                  {gallery.name}
                </Heading>
                <Flex gap={4} fontSize="sm" color="fg.muted" alignItems="center">
                  {gallery.photographer && (
                    <Flex alignItems="center" gap={1}>
                      <FiUser />
                      <Text>{gallery.photographer}</Text>
                    </Flex>
                  )}
                  {gallery.date && (
                    <Flex alignItems="center" gap={1}>
                      <FiCalendar />
                      <Text>{gallery.date}</Text>
                    </Flex>
                  )}
                  <Flex alignItems="center" gap={1}>
                    <FiImage />
                    <Text>{gallery.photo_count || 0} photos</Text>
                  </Flex>
                </Flex>
              </Box>
              <Badge size="lg" colorScheme={getStatusColor(gallery.status || "draft")}>
                {getStatusLabel(gallery.status || "draft")}
              </Badge>
            </Flex>
          </Box>
        </Flex>

        {/* Gallery Description */}
        {gallery.description && (
          <Box>
            <Text color="fg.muted">{gallery.description}</Text>
          </Box>
        )}

        {/* Photo Grid - Placeholder for now */}
        <Box>
          <Heading size="lg" mb={4}>
            Photos
          </Heading>
          {gallery.photo_count && gallery.photo_count > 0 ? (
            <Grid
              templateColumns={{
                base: "repeat(2, 1fr)",
                md: "repeat(3, 1fr)",
                lg: "repeat(4, 1fr)",
              }}
              gap={4}
            >
              {/* Placeholder photo grid - you'll need to add photo endpoints */}
              {Array.from({ length: gallery.photo_count }).map((_, idx) => (
                <Box
                  key={idx}
                  h="200px"
                  bg="gray.200"
                  borderRadius="md"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  color="gray.500"
                >
                  <FiImage size={48} />
                </Box>
              ))}
            </Grid>
          ) : (
            <Box
              p={12}
              textAlign="center"
              border="2px dashed"
              borderColor="gray.300"
              borderRadius="md"
            >
              <FiImage size={48} style={{ margin: "0 auto", color: "#CBD5E0" }} />
              <Text mt={4} color="fg.muted">
                No photos in this gallery yet
              </Text>
            </Box>
          )}
        </Box>
      </Stack>
    </Container>
  )
}
