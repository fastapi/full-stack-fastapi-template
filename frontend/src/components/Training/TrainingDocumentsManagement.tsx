import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  Grid,
  HStack,
  Heading,
  Icon,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState, useRef } from "react"
import {
  FiActivity,
  FiFileText,
  FiMessageSquare,
  FiTrash2,
  FiUpload,
} from "react-icons/fi"

import {
  type AISoulEntity,
  type ApiError,
  AiSoulsService,
  TrainingService,
} from "../../client"
import { RoleGuard } from "../Common/RoleGuard"
import useCustomToast from "../../hooks/useCustomToast"

export function TrainingDocumentsManagement() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [selectedSoul, setSelectedSoul] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploadingFile, setIsUploadingFile] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Get user's AI souls
  const { data: aiSouls } = useQuery({
    queryKey: ["ai-souls"],
    queryFn: () => AiSoulsService.getAiSouls(),
  })

  // Get training documents for selected soul
  const { data: trainingDocuments, refetch: refetchDocuments } = useQuery({
    queryKey: ["training-documents", selectedSoul],
    queryFn: () =>
      selectedSoul
        ? TrainingService.getTrainingDocuments({ aiSoulId: selectedSoul })
        : null,
    enabled: !!selectedSoul,
  })

  // Delete training document mutation
  const deleteTrainingDocMutation = useMutation({
    mutationFn: ({
      aiSoulId,
      documentId,
    }: { aiSoulId: string; documentId: string }) =>
      TrainingService.deleteTrainingDocument({ aiSoulId, documentId }),
    onSuccess: () => {
      showSuccessToast("Training document deleted successfully")
      queryClient.invalidateQueries({
        queryKey: ["training-documents", selectedSoul],
      })
    },
    onError: (err: ApiError) => {
      const errDetail = (err.body as any)?.detail
      showErrorToast(`Failed to delete training document: ${errDetail}`)
    },
  })

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUploadDocument = async () => {
    if (!selectedFile || !selectedSoul) return

    setIsUploadingFile(true)
    setUploadProgress(0)

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      await TrainingService.uploadTrainingDocument({
        aiSoulId: selectedSoul,
        formData: {
          file: selectedFile,
          description: `Training document: ${selectedFile.name}`
        }
      })

      // Complete progress
      clearInterval(progressInterval)
      setUploadProgress(100)

      // Reset after a short delay
      setTimeout(() => {
        setSelectedFile(null)
        setUploadProgress(0)
        if (fileInputRef.current) {
          fileInputRef.current.value = ""
        }
      }, 1000)

      showSuccessToast(
        `Training document "${selectedFile.name}" uploaded successfully`,
      )
      refetchDocuments()
    } catch (error) {
      showErrorToast("Failed to upload training document")
      setUploadProgress(0)
    } finally {
      setIsUploadingFile(false)
    }
  }

  const handleDeleteDocument = async (documentId: string) => {
    if (!selectedSoul) return
    
    deleteTrainingDocMutation.mutate({
      aiSoulId: selectedSoul,
      documentId: documentId,
    })
  }

  return (
    <RoleGuard permission="access_documents">
      <Container maxW="container.xl" py={8}>
        <VStack gap={8} align="stretch">
          <Flex justify="space-between" align="center">
            <Heading size="lg" color="#2F5249">
              Training Documents Management
            </Heading>
          </Flex>

          {/* AI Soul Selector */}
          <Box>
            <Text mb={4} fontWeight="medium" fontSize="lg">
              Select AI Soul:
            </Text>
            <Flex gap={3} wrap="wrap">
              {aiSouls?.map((soul: AISoulEntity) => (
                <Button
                  key={soul.id}
                  variant={selectedSoul === soul.id ? "solid" : "outline"}
                  bg={selectedSoul === soul.id ? "#437057" : "transparent"}
                  color={selectedSoul === soul.id ? "white" : "#2F5249"}
                  borderColor="#97B067"
                  _hover={{
                    bg: selectedSoul === soul.id ? "#3F7D58" : "#f0f9f4",
                    borderColor: "#437057",
                  }}
                  onClick={() => setSelectedSoul(soul.id || null)}
                  size="md"
                >
                  {soul.name}
                </Button>
              ))}
            </Flex>
          </Box>

          {/* Training Documents Section */}
          {selectedSoul && (
            <Box>
              <VStack align="stretch" gap={6}>
                <Flex justify="space-between" align="center">
                  <Heading size="md" color="#2F5249">
                    Training Documents for{" "}
                    {aiSouls?.find((s) => s.id === selectedSoul)?.name}
                  </Heading>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    bg="#437057"
                    color="white"
                    _hover={{ bg: "#2F5249" }}
                    leftIcon={<Icon as={FiUpload} />}
                  >
                    Upload Document
                  </Button>
                </Flex>

                {/* Upload Progress */}
                {selectedFile && (
                  <Box
                    p={4}
                    bg="blue.50"
                    borderRadius="md"
                    border="1px"
                    borderColor="blue.200"
                  >
                    <VStack align="stretch" gap={3}>
                      <HStack justify="space-between">
                        <Text fontSize="sm" fontWeight="medium">
                          Selected: {selectedFile.name}
                        </Text>
                        <Button
                          size="sm"
                          onClick={handleUploadDocument}
                          isLoading={isUploadingFile}
                          loadingText="Uploading..."
                          bg="#437057"
                          color="white"
                          _hover={{ bg: "#2F5249" }}
                        >
                          Upload
                        </Button>
                      </HStack>
                      {isUploadingFile && (
                        <Box>
                          <Text fontSize="xs" color="gray.600" mb={1}>
                            Upload progress: {uploadProgress}%
                          </Text>
                          <Box bg="gray.200" borderRadius="md" h="6px">
                            <Box
                              bg="#437057"
                              h="100%"
                              borderRadius="md"
                              width={`${uploadProgress}%`}
                              transition="width 0.3s ease"
                            />
                          </Box>
                        </Box>
                      )}
                    </VStack>
                  </Box>
                )}

                {/* Training Documents Grid */}
                {trainingDocuments && trainingDocuments.length > 0 ? (
                  <Grid
                    templateColumns="repeat(auto-fill, minmax(350px, 1fr))"
                    gap={6}
                  >
                    {trainingDocuments.map((doc) => (
                      <Box
                        key={doc.id}
                        p={6}
                        bg="white"
                        _dark={{ bg: "gray.800" }}
                        borderRadius="lg"
                        border="1px"
                        borderColor="#bbe7cc"
                        shadow="md"
                        _hover={{ shadow: "lg", borderColor: "#97B067" }}
                        transition="all 0.2s"
                      >
                        <VStack align="start" gap={4}>
                          <HStack justify="space-between" w="100%">
                            <Badge
                              colorScheme="green"
                              variant="subtle"
                              px={2}
                              py={1}
                            >
                              <Icon as={FiFileText} mr={1} />
                              Training Doc
                            </Badge>
                            <Text fontSize="xs" color="gray.500">
                              {new Date(doc.created_at).toLocaleDateString()}
                            </Text>
                          </HStack>

                          <VStack align="start" gap={2} w="100%">
                            <Text
                              fontWeight="bold"
                              fontSize="md"
                              color="#2F5249"
                              noOfLines={2}
                            >
                              {doc.filename}
                            </Text>
                            {doc.description && (
                              <Text
                                fontSize="sm"
                                color="gray.600"
                                noOfLines={3}
                              >
                                {doc.description}
                              </Text>
                            )}
                          </VStack>

                          <HStack justify="space-between" w="100%">
                            <VStack align="start" gap={1}>
                              <Text fontSize="xs" color="gray.500">
                                File Size
                              </Text>
                              <Text fontSize="sm" fontWeight="medium">
                                {doc.file_size 
                                  ? `${(doc.file_size / 1024 / 1024).toFixed(2)} MB`
                                  : "Unknown"}
                              </Text>
                            </VStack>
                            <Button
                              size="sm"
                              colorScheme="red"
                              variant="ghost"
                              onClick={() => handleDeleteDocument(doc.id)}
                              isLoading={deleteTrainingDocMutation.isPending}
                              leftIcon={<Icon as={FiTrash2} />}
                            >
                              Delete
                            </Button>
                          </HStack>
                        </VStack>
                      </Box>
                    ))}
                  </Grid>
                ) : (
                  <Box
                    p={12}
                    bg="gray.50"
                    _dark={{ bg: "gray.700" }}
                    borderRadius="lg"
                    border="2px"
                    borderColor="gray.200"
                    borderStyle="dashed"
                    textAlign="center"
                  >
                    <VStack gap={4}>
                      <Icon as={FiFileText} boxSize="48px" color="gray.400" />
                      <VStack gap={2}>
                        <Text fontSize="lg" fontWeight="medium" color="gray.600">
                          No training documents found
                        </Text>
                        <Text fontSize="sm" color="gray.500" maxW="md">
                          Upload training documents to provide specialized knowledge
                          and improve this AI soul's responses in specific domains.
                        </Text>
                      </VStack>
                      <Button
                        onClick={() => fileInputRef.current?.click()}
                        bg="#437057"
                        color="white"
                        _hover={{ bg: "#2F5249" }}
                        leftIcon={<Icon as={FiUpload} />}
                        size="lg"
                      >
                        Upload First Document
                      </Button>
                    </VStack>
                  </Box>
                )}

                {/* Summary Stats */}
                {trainingDocuments && trainingDocuments.length > 0 && (
                  <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                    <Box
                      p={4}
                      bg="white"
                      borderRadius="md"
                      border="1px"
                      borderColor="gray.200"
                      shadow="sm"
                    >
                      <HStack>
                        <Icon as={FiFileText} color="#437057" boxSize="20px" />
                        <VStack align="start" gap={0}>
                          <Text fontSize="xs" color="gray.600">
                            Total Documents
                          </Text>
                          <Text fontSize="xl" fontWeight="bold" color="#2F5249">
                            {trainingDocuments.length}
                          </Text>
                        </VStack>
                      </HStack>
                    </Box>
                    <Box
                      p={4}
                      bg="white"
                      borderRadius="md"
                      border="1px"
                      borderColor="gray.200"
                      shadow="sm"
                    >
                      <HStack>
                        <Icon as={FiActivity} color="#437057" boxSize="20px" />
                        <VStack align="start" gap={0}>
                          <Text fontSize="xs" color="gray.600">
                            Total Size
                          </Text>
                          <Text fontSize="xl" fontWeight="bold" color="#2F5249">
                            {(
                              trainingDocuments.reduce(
                                (sum, doc) => sum + (doc.file_size || 0),
                                0
                              ) /
                              1024 /
                              1024
                            ).toFixed(1)}{" "}
                            MB
                          </Text>
                        </VStack>
                      </HStack>
                    </Box>
                  </Grid>
                )}

                {/* Hidden file input */}
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  style={{ display: "none" }}
                  accept=".pdf,.txt,.md,.docx"
                />
              </VStack>
            </Box>
          )}

          {/* No Soul Selected State */}
          {!selectedSoul && (
            <Box
              p={12}
              bg="gray.50"
              _dark={{ bg: "gray.700" }}
              borderRadius="lg"
              textAlign="center"
            >
              <VStack gap={4}>
                <Icon as={FiMessageSquare} boxSize="48px" color="gray.400" />
                <VStack gap={2}>
                  <Text fontSize="lg" fontWeight="medium" color="gray.600">
                    Select an AI Soul to manage training documents
                  </Text>
                  <Text fontSize="sm" color="gray.500" maxW="md">
                    Choose an AI soul from the list above to view, upload, and
                    manage its training documents.
                  </Text>
                </VStack>
              </VStack>
            </Box>
          )}
        </VStack>
      </Container>
    </RoleGuard>
  )
} 