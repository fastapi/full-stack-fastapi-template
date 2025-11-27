import {
  Badge,
  Box,
  Card,
  Container,
  EmptyState,
  Flex,
  Grid,
  Heading,
  Stack,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { FiCalendar, FiImage, FiUser } from "react-icons/fi"

import { GalleriesService, OpenAPI } from "@/client"
import type { GalleryPublic } from "@/client"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/galleries/")({
  component: GalleriesList,
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

// Component to fetch and display first photo for a gallery
function GalleryCard({ gallery }: { gallery: GalleryPublic }) {
  // Fetch first photo for this gallery
  const { data: photosData } = useQuery({
    queryKey: ["galleryFirstPhoto", gallery.id],
    queryFn: async () => {
      const res = await fetch(`${OpenAPI.BASE}/api/v1/galleries/${gallery.id}/photos?skip=0&limit=1`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`,
        },
      })
      if (!res.ok) return null
      const data = await res.json() as { data: { id: string; filename: string; url: string }[]; count: number }
      if (data.data && data.data.length > 0) {
        const photo = data.data[0]
        // Convert relative URL to absolute URL
        const photoUrl = photo.url.startsWith("http") ? photo.url : `${OpenAPI.BASE}${photo.url}`
        return photoUrl
      }
      return null
    },
    enabled: (gallery.photo_count ?? 0) > 0, // Only fetch if gallery has photos
  })

  const coverImageUrl = photosData || gallery.cover_image_url

  return (
    <Link
      to="/galleries/$galleryId"
      params={{ galleryId: gallery.id }}
      style={{ textDecoration: "none", color: "inherit" }}
    >
      <Card.Root
        overflow="hidden"
        transition="all 0.2s"
        _hover={{
          transform: "translateY(-4px)",
          boxShadow: "lg",
          cursor: "pointer",
        }}
      >
        {/* Gallery Cover Image */}
        <Box
          h="200px"
          bg="gray.200"
          backgroundImage={coverImageUrl ? `url(${coverImageUrl})` : undefined}
          backgroundSize="cover"
          backgroundPosition="center"
          position="relative"
        >
          <Box
            position="absolute"
            top={2}
            right={2}
            bg="blackAlpha.700"
            px={2}
            py={1}
            borderRadius="md"
          >
            <Flex alignItems="center" gap={1}>
              <FiImage color="white" size={14} />
              <Text fontSize="sm" fontWeight="semibold" color="white">
                {gallery.photo_count}
              </Text>
            </Flex>
          </Box>
          <Badge
            position="absolute"
            top={2}
            left={2}
            colorScheme={getStatusColor(gallery.status || 'pending')}
          >
            {getStatusLabel(gallery.status || 'pending')}
          </Badge>
        </Box>

        {/* Gallery Info */}
        <Card.Body>
          <Stack gap={2}>
            <Heading size="md" mb={1}>
              {gallery.name}
            </Heading>
            <Flex
              justifyContent="space-between"
              alignItems="center"
              pt={2}
              fontSize="xs"
              color="fg.muted"
            >
              {gallery.photographer && (
                <Flex alignItems="center" gap={1}>
                  <FiUser size={12} />
                  <Text>{gallery.photographer}</Text>
                </Flex>
              )}
              {gallery.date && (
                <Flex alignItems="center" gap={1}>
                  <FiCalendar size={12} />
                  <Text>{gallery.date}</Text>
                </Flex>
              )}
            </Flex>
          </Stack>
        </Card.Body>
      </Card.Root>
    </Link>
  )
}

function GalleriesList() {
  const { user: currentUser } = useAuth()
  const { data, isLoading } = useQuery({
    queryKey: ["galleries"],
    queryFn: () => GalleriesService.readGalleries({ skip: 0, limit: 100 }),
  })

  const galleries = data?.data ?? []

  if (isLoading) {
    return (
      <Container maxW="full" p={6}>
        <Text>Loading galleries...</Text>
      </Container>
    )
  }

  if (galleries.length === 0) {
    const isClient = currentUser?.user_type === "client"
    return (
      <Container maxW="full" p={6}>
        <Heading size="2xl" mb={6}>
          Galleries
        </Heading>
        <EmptyState.Root>
          <EmptyState.Content>
            <EmptyState.Indicator>
              <FiImage size={48} />
            </EmptyState.Indicator>
            <VStack textAlign="center">
              <EmptyState.Title>No galleries yet</EmptyState.Title>
              <EmptyState.Description>
                {isClient
                  ? "You don't have any galleries yet. Please wait for your team to add you to a project."
                  : "Galleries will appear here as you work on projects"}
              </EmptyState.Description>
            </VStack>
          </EmptyState.Content>
        </EmptyState.Root>
      </Container>
    )
  }

  return (
    <Container maxW="full" p={6}>
      <Stack gap={6}>
        {/* Header */}
        <Box>
          <Heading size="2xl" mb={2}>
            Galleries
          </Heading>
          <Text color="fg.muted">Browse all photo galleries from your projects</Text>
        </Box>

        {/* Gallery Grid */}
        <Grid
          templateColumns={{
            base: "1fr",
            md: "repeat(2, 1fr)",
            lg: "repeat(3, 1fr)",
          }}
          gap={6}
        >
          {galleries.map((gallery: GalleryPublic) => (
            <GalleryCard key={gallery.id} gallery={gallery} />
          ))}
        </Grid>
      </Stack>
    </Container>
  )
}
