import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  Grid,
  Heading,
  IconButton,
  Input,
  Stack,
  Text,
  useDisclosure,
} from "@chakra-ui/react"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DialogRoot,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogBody,
  DialogFooter,
} from "@/components/ui/dialog"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { FiArrowLeft, FiCalendar, FiImage, FiUser } from "react-icons/fi"

import { GalleriesService, ProjectsService, OpenAPI } from "@/client"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import React, { useRef, useState } from "react"

export const Route = createFileRoute("/_layout/galleries/$galleryId")({
  component: GalleryDetail,
  loader: async ({ params }: { params: { galleryId: string } }) => {
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
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [selected, setSelected] = useState<Record<string, boolean>>({})
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const {
    open: isConfirmAllOpen,
    onOpen: onConfirmAllOpen,
    onClose: onConfirmAllClose,
  } = useDisclosure()
  const cancelRef = useRef<HTMLButtonElement | null>(null)

  // Fetch gallery details
  const { data: gallery, isLoading } = useQuery({
    queryKey: ["gallery", galleryId],
    queryFn: () => GalleriesService.readGallery({ id: galleryId }),
  })

  // Fetch project details for name, start_date, and deadline
  const { data: project } = useQuery({
    queryKey: ["project", gallery?.project_id],
    queryFn: () => ProjectsService.readProject({ id: gallery!.project_id }),
    enabled: !!gallery?.project_id,
  })

  // Fetch photos
  const { data: photosData, isLoading: isLoadingPhotos } = useQuery({
    queryKey: ["galleryPhotos", galleryId],
    queryFn: async () => {
      const res = await fetch(`${OpenAPI.BASE}/api/v1/galleries/${galleryId}/photos`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`,
        },
      })
      if (!res.ok) throw new Error("Failed to load photos")
      const data = await res.json() as { data: { id: string; filename: string; url: string }[]; count: number }
      // Convert relative URLs to absolute URLs
      data.data = data.data.map((photo: { id: string; filename: string; url: string }) => ({
        ...photo,
        url: photo.url.startsWith("http") ? photo.url : `${OpenAPI.BASE}${photo.url}`,
      }))
      return data
    },
  })

  const isTeamMember = user?.user_type === "team_member"
  const MAX_PHOTOS = 20

  const uploadMutation = useMutation({
    mutationFn: async (files: FileList) => {
      // Check max photos before upload
      const currentCount = photosData?.count ?? gallery?.photo_count ?? 0
      const filesToUpload = Array.from(files)
      
      if (currentCount + filesToUpload.length > MAX_PHOTOS) {
        const remaining = MAX_PHOTOS - currentCount
        throw new Error(
          `Cannot upload ${filesToUpload.length} photos. Gallery can only hold ${MAX_PHOTOS} photos total. ` +
          `Currently has ${currentCount} photos. You can upload ${remaining > 0 ? remaining : 0} more photo${remaining !== 1 ? "s" : ""}. ` +
          `Please try again with fewer photos.`
        )
      }

      const form = new FormData()
      filesToUpload.forEach((f) => form.append("files", f))
      const res = await fetch(`${OpenAPI.BASE}/api/v1/galleries/${galleryId}/photos`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`,
        },
        body: form,
      })
      if (!res.ok) {
        const msg = await res.text()
        throw new Error(msg || "Upload failed")
      }
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] })
      queryClient.invalidateQueries({ queryKey: ["galleryPhotos", galleryId] })
      if (fileInputRef.current) fileInputRef.current.value = ""
      showSuccessToast("Photos uploaded successfully!")
    },
    onError: (error: Error) => {
      showErrorToast(error.message || "Failed to upload photos")
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      const res = await fetch(`${OpenAPI.BASE}/api/v1/galleries/${galleryId}/photos`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`,
        },
        body: JSON.stringify({ photo_ids: ids }),
      })
      if (!res.ok) throw new Error("Delete failed")
      return res.json()
    },
    onSuccess: () => {
      setSelected({})
      queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] })
      queryClient.invalidateQueries({ queryKey: ["galleryPhotos", galleryId] })
      showSuccessToast("Photos deleted successfully!")
    },
    onError: () => {
      showErrorToast("Failed to delete photos")
    },
  })

  const photos = photosData?.data ?? []
  const anySelected = Object.values(selected).some(Boolean)
  const hasPhotos = photos.length > 0

  // Lightbox state for viewing photos larger with details & navigation
  const [isLightboxOpen, setIsLightboxOpen] = useState(false)
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0)

  const openLightboxAt = (index: number) => {
    if (!photos || photos.length === 0) return
    setCurrentPhotoIndex(index)
    setIsLightboxOpen(true)
  }

  const closeLightbox = () => setIsLightboxOpen(false)

  const showPrevPhoto = () => {
    if (!photos || photos.length === 0) return
    setCurrentPhotoIndex((prev) =>
      prev === 0 ? photos.length - 1 : prev - 1,
    )
  }

  const showNextPhoto = () => {
    if (!photos || photos.length === 0) return
    setCurrentPhotoIndex((prev) =>
      prev === photos.length - 1 ? 0 : prev + 1,
    )
  }

  const onSelectToggle = (id: string) => {
    setSelected((prev: Record<string, boolean>) => ({ ...prev, [id]: !prev[id] }))
  }

  const onDownloadAll = () => {
    if (!hasPhotos) {
      showErrorToast("There are no photos in this gallery to download")
      return
    }
    window.location.href = `${OpenAPI.BASE}/api/v1/galleries/${galleryId}/download-all`
  }

  const onDownloadSelected = async () => {
    const ids = Object.entries(selected)
      .filter(([, v]) => v)
      .map(([k]) => k)
    if (ids.length === 0) {
      showErrorToast("Select at least one photo to download")
      return
    }
    const res = await fetch(`${OpenAPI.BASE}/api/v1/galleries/${galleryId}/photos/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ photo_ids: ids }),
    })
    if (!res.ok) {
      showErrorToast("Failed to download selected photos")
      return
    }
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    // Use project name in download filename
    const projectName = project?.name ? project.name.replace(/[^a-z0-9]/gi, "_") : "Project"
    a.download = `Mosaic-${projectName}-Photos.zip`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  }

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
                <Flex gap={4} fontSize="sm" color="fg.muted" alignItems="center" flexWrap="wrap">
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
                  {project?.start_date && (
                    <Flex alignItems="center" gap={1}>
                      <FiCalendar />
                      <Text>Start: {project.start_date}</Text>
                    </Flex>
                  )}
                  {project?.deadline && (
                    <Flex alignItems="center" gap={1}>
                      <FiCalendar />
                      <Text>Deadline: {project.deadline}</Text>
                    </Flex>
                  )}
                </Flex>
              </Box>
              <Badge size="lg" colorScheme={getStatusColor(gallery.status || "draft")}>
                {getStatusLabel(gallery.status || "draft")}
              </Badge>
            </Flex>
          </Box>
        </Flex>

        {/* Actions and Photos */}
        <Flex gap={3} alignItems="center" justifyContent="space-between">
          <Flex gap={2}>
            <Button variant="solid" onClick={onConfirmAllOpen} disabled={!hasPhotos}>
              Download all photos
            </Button>
            <Button variant="outline" onClick={onDownloadSelected} disabled={!anySelected}>
              Download selected
            </Button>
            {isTeamMember && (
              <Button
                variant="outline"
                colorScheme="red"
                onClick={() => {
                  const ids = Object.entries(selected)
                    .filter(([, v]) => v)
                    .map(([k]) => k)
                  if (ids.length > 0) deleteMutation.mutate(ids)
                }}
                disabled={!anySelected}
              >
                Delete selected
              </Button>
            )}
          </Flex>
          {isTeamMember && (
            <Box>
              <Input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                style={{ display: "none" }}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                  if (e.target.files && e.target.files.length > 0) {
                    uploadMutation.mutate(e.target.files)
                  }
                }}
              />
              <Button
                onClick={() => fileInputRef.current?.click()}
                loading={uploadMutation.isPending}
              >
                Upload Photos
              </Button>
            </Box>
          )}
        </Flex>

        <DialogRoot open={isConfirmAllOpen} onOpenChange={(e: { open: boolean }) => {
          if (!e.open) {
            onConfirmAllClose()
          }
        }}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Download all photos</DialogTitle>
            </DialogHeader>
            <DialogBody>
              Do you agree to download all photos in this project gallery?
            </DialogBody>
            <DialogFooter>
              <Button ref={cancelRef} onClick={onConfirmAllClose}>
                Cancel
              </Button>
              <Button
                colorScheme="blue"
                ml={3}
                onClick={() => {
                  onConfirmAllClose()
                  onDownloadAll()
                }}
              >
                Download
              </Button>
            </DialogFooter>
          </DialogContent>
        </DialogRoot>

        {/* Lightbox dialog for viewing photos larger with details and navigation */}
        <DialogRoot open={isLightboxOpen} onOpenChange={(e: { open: boolean }) => {
          if (!e.open) {
            closeLightbox()
          }
        }}>
          <DialogContent maxW="800px">
            <DialogHeader>
              <DialogTitle>Photo details</DialogTitle>
            </DialogHeader>
            <DialogBody>
              {hasPhotos && photos[currentPhotoIndex] && (
                <Stack gap={4}>
                  <Box
                    position="relative"
                    w="100%"
                    h="400px"
                    bg="gray.100"
                    borderRadius="md"
                    overflow="hidden"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                  >
                    <img
                      src={photos[currentPhotoIndex].url}
                      alt={photos[currentPhotoIndex].filename}
                      style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
                    />
                    {/* Navigation arrows */}
                    <Button
                      position="absolute"
                      left="8px"
                      top="50%"
                      transform="translateY(-50%)"
                      variant="outline"
                      onClick={showPrevPhoto}
                    >
                      ‹
                    </Button>
                    <Button
                      position="absolute"
                      right="8px"
                      top="50%"
                      transform="translateY(-50%)"
                      variant="outline"
                      onClick={showNextPhoto}
                    >
                      ›
                    </Button>
                  </Box>
                  <Box> {/* TODO: Add file size and date added */ }
                    <Text fontWeight="bold">Filename: {photos[currentPhotoIndex].filename}</Text>
                    <Text>
                      Size: unknown (file size is not tracked in the database)
                    </Text>
                    <Text>
                      Date added: {gallery.date ?? "Unknown"}
                    </Text>
                  </Box>
                </Stack>
              )}
            </DialogBody>
            <DialogFooter>
              <Button onClick={closeLightbox}>Close</Button>
            </DialogFooter>
          </DialogContent>
        </DialogRoot>

        <Box>
          <Heading size="lg" mb={4}>
            Photos
          </Heading>
          {isLoadingPhotos ? (
            <Text>Loading photos...</Text>
          ) : photos.length > 0 ? (
            <Grid
              templateColumns={{
                base: "repeat(2, 1fr)",
                md: "repeat(3, 1fr)",
                lg: "repeat(4, 1fr)",
              }}
              gap={4}
            >
              {photos.map((p: { id: string; filename: string; url: string }, index: number) => (
                <Box
                  key={p.id}
                  position="relative"
                  h="200px"
                  bg="gray.100"
                  borderRadius="md"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  overflow="hidden"
                  onClick={() => openLightboxAt(index)}
                  cursor="pointer"
                >
                  <img
                    src={p.url}
                    alt={p.filename}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                  <Box position="absolute" top="8px" left="8px" bg="whiteAlpha.800" borderRadius="md" p={1}>
                    <Checkbox
                      checked={!!selected[p.id]}
                      onCheckedChange={() => onSelectToggle(p.id)}
                    >
                      Select
                    </Checkbox>
                  </Box>
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
              {isTeamMember && (
                <Text mt={2} color="fg.muted">
                  You can upload up to 20 photos.
                </Text>
              )}
            </Box>
          )}
        </Box>
      </Stack>
    </Container>
  )
}
