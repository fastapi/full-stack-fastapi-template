import {
  Box,
  Button,
  Container,
  Flex,
  Grid,
  HStack,
  Heading,
  Text,
  VStack,
  Icon,
  Badge,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import {
  FiActivity,
  FiAlertTriangle,
  FiBook,
  FiCpu,
  FiEdit3,
  FiMessageSquare,
  FiPlus,
  FiTrash2,
  FiUser,
} from "react-icons/fi"

import { AiSoulsService } from "@/client"
import {
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog"
import { Skeleton, SkeletonText } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import useAuth from "@/hooks/useAuth"
import { hasPermission } from "@/utils/roles"

export const Route = createFileRoute("/_layout/ai-souls")({
  component: AISouls,
})

// Enhanced Skeleton Card Component
const SkeletonCard = () => (
  <Box
    bg="white"
    p={8}
    rounded="xl"
    shadow="md"
    borderWidth="1px"
    borderColor="gray.100"
    minH="500px"
    display="flex"
    flexDirection="column"
    transition="all 0.3s ease"
  >
    <VStack align="stretch" gap={6} flex="1">
      <Box>
        <Skeleton height="8" width="70%" mb={3} rounded="md" />
        <Skeleton height="5" width="50%" rounded="md" />
      </Box>

      <Box flex="1">
        <SkeletonText noOfLines={4} gap={3} />
      </Box>

      <Box>
        <Skeleton height="5" width="60%" mb={3} rounded="md" />
        <SkeletonText noOfLines={2} gap={2} />
      </Box>

      <Box>
        <Skeleton height="5" width="40%" mb={2} rounded="md" />
      </Box>

      <HStack gap={3} mt="auto" pt={6}>
        <Skeleton height="12" flex={1} rounded="lg" />
        <Skeleton height="12" flex={1} rounded="lg" />
        <Skeleton height="12" width="20" rounded="lg" />
        <Skeleton height="12" width="20" rounded="lg" />
      </HStack>
    </VStack>
  </Box>
)

function AISouls() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { user } = useAuth()
  
  // Modal state for delete confirmation
  const [isOpen, setIsOpen] = useState(false)
  const [soulToDelete, setSoulToDelete] = useState<{id: string, name: string} | null>(null)

  const { data: aiSouls, isLoading, error } = useQuery({
    queryKey: ["ai-souls"],
    queryFn: () => AiSoulsService.getAiSouls(),
    retry: (failureCount, error) => {
      // Don't retry on authentication errors
      if (error?.message?.includes('401') || error?.message?.includes('403')) {
        return false
      }
      return failureCount < 3
    },
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Delete AI Soul mutation
  const deleteAiSoulMutation = useMutation({
    mutationFn: (aiSoulId: string) => AiSoulsService.deleteAiSoul({ aiSoulId }),
    onSuccess: () => {
      showSuccessToast("AI Soul deleted successfully.")
      queryClient.invalidateQueries({ queryKey: ["ai-souls"] })
      setIsOpen(false)
      setSoulToDelete(null)
    },
    onError: (err: any) => {
      const errDetail = err.body?.detail || "Failed to delete AI Soul"
      showErrorToast(errDetail)
      setIsOpen(false)
      setSoulToDelete(null)
    },
  })

  // Delete handler function - opens modal
  const handleDeleteAiSoul = (aiSoulId: string, soulName: string) => {
    setSoulToDelete({ id: aiSoulId, name: soulName })
    setIsOpen(true)
  }

  // Confirm delete - actual deletion
  const confirmDelete = () => {
    if (soulToDelete) {
      deleteAiSoulMutation.mutate(soulToDelete.id)
    }
  }

  // Render skeleton cards during loading
  const renderSkeletonCards = () => (
    <>
      {Array.from({ length: 6 }).map((_, index) => (
        <SkeletonCard key={index} />
      ))}
    </>
  )

  // Get persona type color
  const getPersonaTypeColor = (personaType: string) => {
    const colors = {
      therapist: "purple",
      counselor: "blue",
      coach: "green",
      mentor: "teal",
      guide: "orange",
      teacher: "red",
      support: "pink",
      creative: "yellow",
      spiritual: "cyan",
      default: "gray"
    }
    return colors[personaType?.toLowerCase() as keyof typeof colors] || colors.default
  }

  // Render actual AI soul cards
  const renderAiSoulCards = () => {
    if (!aiSouls || aiSouls.length === 0) {
      return (
        <Box gridColumn="1 / -1" />
      )
    }

    return aiSouls.map((soul) => (
      <Box
        key={soul.id}
        bg="white"
        p={8}
        rounded="xl"
        shadow="md"
        borderWidth="1px"
        borderColor="gray.100"
        position="relative"
        transition="all 0.3s ease"
        _hover={{ 
          transform: "translateY(-4px)", 
          shadow: "xl", 
          borderColor: "blue.200" 
        }}
        minH="500px"
        display="flex"
        flexDirection="column"
        overflow="hidden"
      >
        {/* Header with status indicator */}
        <Box position="relative" mb={6}>
          <Flex justify="space-between" align="start" mb={4}>
            <Badge
              colorScheme={getPersonaTypeColor(soul.persona_type)}
              variant="subtle"
              fontSize="xs"
              fontWeight="600"
              px={3}
              py={1}
              rounded="full"
            >
              {soul.persona_type || "AI Assistant"}
            </Badge>
            <Badge
              colorScheme={soul.is_active ? "green" : "gray"}
              variant="solid"
              fontSize="xs"
              fontWeight="600"
              px={3}
              py={1}
              rounded="full"
            >
              {soul.is_active ? "Active" : "Inactive"}
            </Badge>
          </Flex>
          
          <Heading 
            size="lg" 
            mb={2} 
            color="gray.800"
            fontWeight="700"
            lineHeight="1.2"
          >
            {soul.name || "Unnamed Soul"}
          </Heading>
        </Box>

        {/* Description */}
        <Box flex="1" mb={6}>
          <Text 
            color="gray.600"
            fontSize="md"
            lineHeight="1.6"
            lineClamp={4}
            minH="96px"
          >
            {soul.description || "No description available"}
          </Text>
        </Box>

        {/* Specializations */}
        <Box mb={6}>
          <Flex align="center" gap={2} mb={3}>
            <Icon as={FiUser} color="gray.500" />
            <Text fontWeight="600" color="gray.700" fontSize="sm">
              Specializations
            </Text>
          </Flex>
          <Text 
            fontSize="sm"
            color="gray.600"
            lineHeight="1.5"
            lineClamp={2}
            minH="40px"
          >
            {soul.specializations || "General AI assistance"}
          </Text>
        </Box>

        {/* Interaction Stats */}
        <Box mb={6}>
          <Flex align="center" gap={2} mb={2}>
            <Icon as={FiActivity} color="blue.500" />
            <Text fontWeight="600" color="gray.700" fontSize="sm">
              Interactions
            </Text>
          </Flex>
          <Text fontSize="2xl" fontWeight="700" color="blue.600">
            {soul.interaction_count || 0}
          </Text>
          <Text fontSize="xs" color="gray.500">
            Total conversations
          </Text>
        </Box>

        {/* Action Buttons */}
        <VStack gap={3} mt="auto">
          {/* Primary Chat Button */}
                     <Button
             bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
             color="white"
             borderRadius="xl"
             _hover={{ 
               bg: "linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)",
               transform: "translateY(-1px)",
               shadow: "lg"
             }}
             _active={{ transform: "translateY(0)" }}
             size="lg"
             width="100%"
             height="48px"
             fontSize="md"
             fontWeight="600"
             onClick={() => navigate({ to: "/chat", search: { soul: soul.id } })}
           >
             <FiMessageSquare style={{ marginRight: "0.5rem" }} />
             Start Conversation
           </Button>

          {/* Secondary Actions */}
          <HStack gap={2} width="100%">
                         {hasPermission(user || null, "access_training") && (
               <Button
                 colorScheme="teal"
                 variant="outline"
                 size="md"
                 flex={1}
                 height="44px"
                 fontSize="sm"
                 fontWeight="500"
                 borderRadius="lg"
                 onClick={() => navigate({ to: "/training", search: { soul: soul.id } })}
               >
                 <FiBook style={{ marginRight: "0.5rem" }} />
                 Train
               </Button>
             )}
                         {hasPermission(user || null, "edit_souls") && (
               <Button
                 colorScheme="gray"
                 variant="outline"
                 size="md"
                 height="44px"
                 fontSize="sm"
                 fontWeight="500"
                 borderRadius="lg"
                 onClick={() => navigate({
                   to: "/ai-souls-edit/$id",
                   params: { id: soul.id },
                 })}
               >
                 <FiEdit3 style={{ marginRight: "0.5rem" }} />
                 Edit
               </Button>
             )}
             {hasPermission(user || null, "delete_souls") && (
               <Button
                 colorScheme="red"
                 variant="outline"
                 size="md"
                 height="44px"
                 fontSize="sm"
                 fontWeight="500"
                 borderRadius="lg"
                 onClick={() => handleDeleteAiSoul(soul.id!, soul.name)}
               >
                 <FiTrash2 style={{ marginRight: "0.5rem" }} />
                 Delete
               </Button>
             )}
          </HStack>
        </VStack>
      </Box>
    ))
  }

  return (
    <Box
      minH="calc(100vh - 4rem)"
      bg="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
      _dark={{ bg: "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)" }}
    >
      <Container maxW="7xl" py={10}>
        {/* Header */}
        <Box
          bg="white"
          rounded="2xl"
          shadow="lg"
          p={8}
          mb={8}
          borderWidth="1px"
          borderColor="gray.100"
        >
          <Flex justify="space-between" align="center">
            <Box>
              <Heading size="xl" mb={3} color="gray.800" fontWeight="700">
                AI Souls
              </Heading>
              <Text color="gray.600" fontSize="lg">
                Discover and interact with AI companions tailored to your needs
              </Text>
            </Box>
            {hasPermission(user || null, "create_souls") && (
              <Button
                bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                color="white"
                _hover={{ 
                  bg: "linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)",
                  transform: "translateY(-2px)",
                  shadow: "xl"
                }}
                _active={{ transform: "translateY(0)" }}
                size="lg"
                height="56px"
                px={8}
                fontSize="md"
                fontWeight="600"
                borderRadius="xl"
                onClick={() => navigate({ to: "/create-soul" })}
              >
                <FiPlus style={{ marginRight: "0.5rem" }} />
                Create New Soul
              </Button>
            )}
          </Flex>
        </Box>

        {/* Error State */}
        {error && (
          <Box
            bg="red.50"
            rounded="2xl"
            shadow="lg"
            p={8}
            mb={8}
            borderWidth="1px"
            borderColor="red.200"
            textAlign="center"
          >
            <VStack gap={4}>
              <Icon as={FiAlertTriangle} boxSize={12} color="red.500" />
              <VStack gap={2}>
                <Heading size="md" color="red.700">
                  Failed to Load AI Souls
                </Heading>
                <Text color="red.600" fontSize="md">
                  {error?.message?.includes('401') || error?.message?.includes('403') 
                    ? "You don't have permission to access AI souls. Please contact your administrator."
                    : "There was an error loading AI souls. Please try again later."
                  }
                </Text>
              </VStack>
              <Button
                colorScheme="red"
                variant="outline"
                onClick={() => queryClient.invalidateQueries({ queryKey: ["ai-souls"] })}
              >
                Try Again
              </Button>
            </VStack>
          </Box>
        )}

        {/* AI Souls Grid */}
        {!error && (
          <Grid
            templateColumns={{
              base: "1fr",
              md: "repeat(2, 1fr)",
              lg: "repeat(2, 1fr)",
            }}
            gap={8}
          >
            {isLoading ? renderSkeletonCards() : renderAiSoulCards()}
          </Grid>
        )}

        {/* Empty State */}
        {!error && !isLoading && (!aiSouls || aiSouls.length === 0) && (
          <Box
            bg="white"
            rounded="2xl"
            shadow="lg"
            p={12}
            textAlign="center"
            borderWidth="1px"
            borderColor="gray.100"
          >
            <VStack gap={6}>
              <Box
                bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                rounded="full"
                p={6}
                display="inline-flex"
              >
                <Icon as={FiCpu} boxSize={12} color="white" />
              </Box>
              <VStack gap={3}>
                <Heading size="lg" color="gray.700" fontWeight="600">
                  No AI Souls Available
                </Heading>
                <Text color="gray.500" maxW="md" fontSize="md" lineHeight="1.6">
                  {hasPermission(user || null, "create_souls") 
                    ? "Get started by creating your first AI soul entity to chat with. Each soul can be customized with unique personalities and specializations."
                    : "No AI souls have been created yet. Contact your administrator or trainer to create AI companions for interaction."
                  }
                </Text>
              </VStack>
              {hasPermission(user || null, "create_souls") && (
                <Button
                  bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                  color="white"
                  _hover={{ 
                    bg: "linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)",
                    transform: "translateY(-2px)",
                    shadow: "xl"
                  }}
                  _active={{ transform: "translateY(0)" }}
                  size="lg"
                  height="48px"
                  px={8}
                  fontSize="md"
                  fontWeight="600"
                  borderRadius="xl"
                  onClick={() => navigate({ to: "/create-soul" })}
                >
                  <FiPlus style={{ marginRight: "0.5rem" }} />
                  Create Your First AI Soul
                </Button>
              )}
            </VStack>
          </Box>
        )}

        {/* Delete Confirmation Modal */}
        <DialogRoot
          size={{ base: "xs", md: "md" }}
          role="alertdialog"
          placement="center"
          open={isOpen}
          onOpenChange={({ open }) => setIsOpen(open)}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete AI Soul</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <VStack gap={4} align="start">
                <Flex align="center" gap={3}>
                  <Icon as={FiAlertTriangle} color="red.500" boxSize={6} />
                  <Text fontWeight="600">Are you sure you want to delete this AI soul?</Text>
                </Flex>
                <Text color="gray.600">
                  This action cannot be undone. The AI soul "{soulToDelete?.name}" and all its data will be permanently removed.
                </Text>
              </VStack>
            </DialogBody>
            <DialogFooter>
              <Button
                variant="outline"
                mr={3}
                onClick={() => setIsOpen(false)}
              >
                Cancel
              </Button>
              <Button
                colorScheme="red"
                onClick={confirmDelete}
                loading={deleteAiSoulMutation.isPending}
              >
                Delete
              </Button>
            </DialogFooter>
          </DialogContent>
        </DialogRoot>
      </Container>
    </Box>
  )
}
