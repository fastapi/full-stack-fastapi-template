import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  Grid,
  HStack,
  Heading,
  Input,
  Select,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { FiCheck, FiRefreshCw, FiSettings, FiTrash2, FiX } from "react-icons/fi"

import {
  type AISoulEntity,
  AiSoulsService,
  type ApiError,
  DocumentsService,
  EnhancedRagService,
  TrainingService,
} from "../../client"
import { RoleGuard } from "../../components/Common/RoleGuard"
import { EnhancedSearch } from "../../components/Search/EnhancedSearch"
import SearchAnalytics from "../../components/Search/SearchAnalytics"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "../../components/ui/dialog"
import { Field } from "../../components/ui/field"
import useCustomToast from "../../hooks/useCustomToast"

export const Route = createFileRoute("/_layout/documents")({
  component: Documents,
})

function Documents() {
  return (
    <RoleGuard permission="access_documents">
      <DocumentsContent />
    </RoleGuard>
  )
}

function DocumentsContent() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [description, setDescription] = useState("")
  const [activeTab, setActiveTab] = useState(0)
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])
  const [processingDocuments, setProcessingDocuments] = useState<string[]>([])
  const [selectedSoul, setSelectedSoul] = useState<string | null>(null)
  const [showTrainingDocuments, setShowTrainingDocuments] = useState(false)

  // Get user's AI souls
  const { data: aiSouls } = useQuery({
    queryKey: ["ai-souls"],
    queryFn: () => AiSoulsService.getAiSouls(),
  })

  // Get training documents for selected soul
  const { data: trainingDocuments } = useQuery({
    queryKey: ["training-documents", selectedSoul],
    queryFn: () =>
      selectedSoul
        ? TrainingService.getTrainingDocuments({ aiSoulId: selectedSoul })
        : null,
    enabled: !!selectedSoul && showTrainingDocuments,
  })

  // Get user's documents
  const {
    data: documents,
    isLoading: documentsLoading,
    error: documentsError,
  } = useQuery({
    queryKey: ["documents"],
    queryFn: () => DocumentsService.getDocuments(),
  })

  // Upload document mutation
  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile) throw new Error("No file selected")

      console.log("Uploading file:", {
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type,
        description: description,
      })

      return DocumentsService.uploadDocument({
        formData: {
          file: selectedFile,
          description: description?.trim() || null,
        },
      })
    },
    onSuccess: (data) => {
      console.log("Upload successful:", data)
      showSuccessToast(`Document "${selectedFile?.name}" uploaded successfully`)
      queryClient.invalidateQueries({ queryKey: ["documents"] })
      setIsUploadDialogOpen(false)
      setSelectedFile(null)
      setDescription("")
    },
    onError: (err: ApiError) => {
      console.error("Upload error:", err)
      let errorMessage = "Failed to upload document"

      if (err.status === 422) {
        const errDetail = (err.body as any)?.detail
        if (Array.isArray(errDetail)) {
          errorMessage = errDetail.map((e) => e.msg).join(", ")
        } else if (typeof errDetail === "string") {
          errorMessage = errDetail
        } else {
          errorMessage = "Invalid file format or data"
        }
      } else if (err.status === 413) {
        errorMessage = "File is too large. Maximum size is 10MB."
      } else if (err.status === 415) {
        errorMessage = "Unsupported file type. Only PDF files are allowed."
      } else if (err.status === 500) {
        errorMessage = "Server error. Please try again later."
      } else if (err.message) {
        errorMessage = err.message
      }

      showErrorToast(errorMessage)
    },
  })

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: (documentId: string) =>
      DocumentsService.deleteDocument({ documentId }),
    onSuccess: () => {
      showSuccessToast("Document deleted successfully")
      queryClient.invalidateQueries({ queryKey: ["documents"] })
    },
    onError: (err: ApiError) => {
      const errDetail = (err.body as any)?.detail
      showErrorToast(`Failed to delete document: ${errDetail}`)
    },
  })

  // Reindex document mutation
  const reindexMutation = useMutation({
    mutationFn: (documentId: string) => {
      setProcessingDocuments((prev) => [...prev, documentId])
      return EnhancedRagService.reindexDocument({ documentId })
    },
    onSuccess: (_, documentId) => {
      showSuccessToast("Document reindexed successfully")
      queryClient.invalidateQueries({ queryKey: ["documents"] })
      setProcessingDocuments((prev) => prev.filter((id) => id !== documentId))
    },
    onError: (err: ApiError, documentId) => {
      const errDetail = (err.body as any)?.detail
      showErrorToast(`Failed to reindex document: ${errDetail}`)
      setProcessingDocuments((prev) => prev.filter((id) => id !== documentId))
    },
  })

  // Bulk process documents mutation
  const bulkProcessMutation = useMutation({
    mutationFn: (documentIds: string[]) => {
      setProcessingDocuments((prev) => [...prev, ...documentIds])
      return EnhancedRagService.bulkProcessDocuments({
        requestBody: documentIds,
        chunkingStrategy: "semantic",
      })
    },
    onSuccess: (_, documentIds) => {
      showSuccessToast(`Successfully processed ${documentIds.length} documents`)
      queryClient.invalidateQueries({ queryKey: ["documents"] })
      setProcessingDocuments((prev) =>
        prev.filter((id) => !documentIds.includes(id)),
      )
      setSelectedDocuments([])
    },
    onError: (err: ApiError, documentIds) => {
      const errDetail = (err.body as any)?.detail
      showErrorToast(`Failed to process documents: ${errDetail}`)
      setProcessingDocuments((prev) =>
        prev.filter((id) => !documentIds.includes(id)),
      )
    },
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

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (file.type !== "application/pdf") {
        showErrorToast("Only PDF files are supported for document upload")
        event.target.value = "" // Clear the input
        return
      }

      // Validate file size (10MB limit)
      const maxSize = 10 * 1024 * 1024 // 10MB in bytes
      if (file.size > maxSize) {
        showErrorToast(
          `File size must be less than 10MB. Current size: ${(file.size / 1024 / 1024).toFixed(1)}MB`,
        )
        event.target.value = "" // Clear the input
        return
      }

      // Validate file name
      if (file.name.length > 255) {
        showErrorToast(
          "File name is too long. Please rename the file to less than 255 characters.",
        )
        event.target.value = "" // Clear the input
        return
      }

      setSelectedFile(file)
      showSuccessToast(`File "${file.name}" selected successfully`)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      showErrorToast("Please select a PDF file to upload")
      return
    }

    // Final validation before upload
    if (selectedFile.type !== "application/pdf") {
      showErrorToast("Invalid file type. Only PDF files are allowed.")
      return
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      showErrorToast("File is too large. Maximum size is 10MB.")
      return
    }

    try {
      uploadMutation.mutate()
    } catch (error) {
      showErrorToast("Failed to start upload. Please try again.")
    }
  }

  const handleDelete = (documentId: string) => {
    if (confirm("Are you sure you want to delete this document?")) {
      deleteMutation.mutate(documentId)
    }
  }

  const handleReindex = (documentId: string) => {
    reindexMutation.mutate(documentId)
  }

  const handleToggleDocumentSelection = (documentId: string) => {
    setSelectedDocuments((prev) =>
      prev.includes(documentId)
        ? prev.filter((id) => id !== documentId)
        : [...prev, documentId],
    )
  }

  const handleSelectAll = () => {
    if (documents?.data) {
      const allIds = documents.data.map((doc) => doc.id)
      setSelectedDocuments((prev) =>
        prev.length === allIds.length ? [] : allIds,
      )
    }
  }

  const handleBulkProcess = () => {
    if (selectedDocuments.length === 0) {
      showErrorToast("Please select documents to process")
      return
    }

    if (
      confirm(
        `Are you sure you want to reprocess ${selectedDocuments.length} selected documents?`,
      )
    ) {
      bulkProcessMutation.mutate(selectedDocuments)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
      case "processed":
        return "gray"
      case "processing":
        return "yellow"
      case "failed":
      case "error":
        return "red"
      default:
        return "gray"
    }
  }

  const handleSearchResultClick = (result: any) => {
    showSuccessToast(`Clicked on result from document: ${result.document_id}`)
    // Here you could navigate to the document or show more details
  }

  const handleDeleteTrainingDoc = (documentId: string) => {
    if (selectedSoul) {
      deleteTrainingDocMutation.mutate({ aiSoulId: selectedSoul, documentId })
    }
  }

  if (documentsError) {
    return <Text color="red.500">Error loading documents</Text>
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={8} align="stretch">
        <Flex justify="space-between" align="center">
          <Heading size="lg">Documents & Search</Heading>
          <RoleGuard permission="upload_documents">
            <Button
              colorScheme="teal"
              onClick={() => setIsUploadDialogOpen(true)}
            >
              Upload Document
            </Button>
          </RoleGuard>
        </Flex>

        {/* Tab Navigation */}
        <Box borderBottom="1px" borderColor="gray.200">
          <Flex gap={4}>
            <Button
              variant={activeTab === 0 ? "solid" : "ghost"}
              colorScheme={activeTab === 0 ? "blue" : "gray"}
              onClick={() => setActiveTab(0)}
            >
              🔍 Enhanced Search
            </Button>
            <Button
              variant={activeTab === 1 ? "solid" : "ghost"}
              colorScheme={activeTab === 1 ? "blue" : "gray"}
              onClick={() => setActiveTab(1)}
            >
              📁 My Documents
            </Button>
            <Button
              variant={activeTab === 2 ? "solid" : "ghost"}
              colorScheme={activeTab === 2 ? "blue" : "gray"}
              onClick={() => setActiveTab(2)}
            >
              🧠 Training Documents
            </Button>
            <Button
              variant={activeTab === 3 ? "solid" : "ghost"}
              colorScheme={activeTab === 3 ? "blue" : "gray"}
              onClick={() => setActiveTab(3)}
            >
              📊 Analytics
            </Button>
          </Flex>
        </Box>

        {/* Tab Content */}
        <Box py={6}>
          {/* Enhanced Search Tab */}
          {activeTab === 0 && (
            <Box>
              <EnhancedSearch
                placeholder="Search through all your documents..."
                onResultClick={handleSearchResultClick}
                autoFocus={true}
              />
            </Box>
          )}

          {/* Documents Management Tab */}
          {activeTab === 1 && (
            <Box>
              {documentsLoading ? (
                <Text>Loading documents...</Text>
              ) : documents?.data && documents.data.length > 0 ? (
                <VStack gap={6} align="stretch">
                  {/* Bulk Actions Bar */}
                  <Flex
                    justify="space-between"
                    align="center"
                    p={4}
                    bg="gray.50"
                    _dark={{ bg: "gray.700" }}
                    borderRadius="md"
                  >
                    <HStack gap={4}>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleSelectAll}
                      >
                        {selectedDocuments.length === documents.data.length ? (
                          <>
                            <FiX style={{ marginRight: "0.5rem" }} />
                            Deselect All
                          </>
                        ) : (
                          <>
                            <FiCheck style={{ marginRight: "0.5rem" }} />
                            Select All
                          </>
                        )}
                      </Button>
                      <Text fontSize="sm" color="gray.600">
                        {selectedDocuments.length} of {documents.data.length}{" "}
                        selected
                      </Text>
                    </HStack>

                    {selectedDocuments.length > 0 && (
                      <Button
                        size="sm"
                        colorScheme="teal"
                        onClick={handleBulkProcess}
                        loading={bulkProcessMutation.isPending}
                        loadingText="Processing..."
                      >
                        <FiRefreshCw style={{ marginRight: "0.5rem" }} />
                        Reprocess Selected ({selectedDocuments.length})
                      </Button>
                    )}
                  </Flex>

                  {/* Documents Grid */}
                  <Grid
                    templateColumns="repeat(auto-fill, minmax(350px, 1fr))"
                    gap={6}
                  >
                    {documents.data.map((doc) => (
                      <Box
                        key={doc.id}
                        p={5}
                        bg="white"
                        _dark={{ bg: "gray.800" }}
                        borderRadius="lg"
                        border="1px"
                        borderColor={
                          selectedDocuments.includes(doc.id)
                            ? "blue.300"
                            : "gray.200"
                        }
                        borderStyle="solid"
                        shadow="sm"
                        position="relative"
                        _hover={{ shadow: "md" }}
                      >
                        {/* Selection Checkbox */}
                        <Box position="absolute" top={3} right={3}>
                          <input
                            type="checkbox"
                            checked={selectedDocuments.includes(doc.id)}
                            onChange={() =>
                              handleToggleDocumentSelection(doc.id)
                            }
                            style={{ cursor: "pointer" }}
                          />
                        </Box>

                        <VStack gap={3} align="stretch">
                          <Heading size="md" maxLines={1} pr={8}>
                            {doc.original_filename}
                          </Heading>

                          {doc.description && (
                            <Text fontSize="sm" color="gray.600" maxLines={2}>
                              {doc.description}
                            </Text>
                          )}

                          {/* Status and Processing Info */}
                          <HStack justify="space-between" align="center">
                            <Badge
                              colorScheme={getStatusColor(
                                doc.processing_status,
                              )}
                              variant="subtle"
                            >
                              {doc.processing_status}
                            </Badge>
                            <Text fontSize="xs" color="gray.500">
                              {doc.chunk_count} chunks
                            </Text>
                          </HStack>

                          {/* File Info */}
                          <Text fontSize="xs" color="gray.500">
                            Size: {(doc.file_size / 1024).toFixed(1)} KB
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            Uploaded:{" "}
                            {new Date(
                              doc.upload_timestamp,
                            ).toLocaleDateString()}
                          </Text>

                          {/* Action Buttons */}
                          <HStack gap={2} pt={2}>
                            <Button
                              size="sm"
                              colorScheme="teal"
                              variant="outline"
                              onClick={() => handleReindex(doc.id)}
                              loading={processingDocuments.includes(doc.id)}
                              loadingText="Processing..."
                              disabled={processingDocuments.includes(doc.id)}
                            >
                              <FiRefreshCw style={{ marginRight: "0.5rem" }} />
                              Reindex
                            </Button>
                            <Button
                              size="sm"
                              colorScheme="red"
                              variant="ghost"
                              onClick={() => handleDelete(doc.id)}
                            >
                              <FiTrash2 style={{ marginRight: "0.5rem" }} />
                              Delete
                            </Button>
                          </HStack>
                        </VStack>
                      </Box>
                    ))}
                  </Grid>
                </VStack>
              ) : (
                <VStack py={8} gap={4}>
                  <Text color="gray.500">No documents uploaded yet</Text>
                  <Button
                    colorScheme="teal"
                    onClick={() => setIsUploadDialogOpen(true)}
                  >
                    Upload Your First Document
                  </Button>
                </VStack>
              )}
            </Box>
          )}

          {/* Training Documents Tab */}
          {activeTab === 2 && (
            <Box>
              <VStack gap={6} align="stretch">
                <Heading size="md" color="#2F5249">
                  Training Documents by AI Soul
                </Heading>

                {/* AI Soul Selector */}
                <Box>
                  <Text mb={2} fontWeight="medium">
                    Select AI Soul:
                  </Text>
                  <Flex gap={3} wrap="wrap">
                    {aiSouls?.map((soul: AISoulEntity) => (
                      <Button
                        key={soul.id}
                        variant={selectedSoul === soul.id ? "solid" : "outline"}
                        bg={
                          selectedSoul === soul.id ? "#437057" : "transparent"
                        }
                        color={selectedSoul === soul.id ? "white" : "#2F5249"}
                        borderColor="#97B067"
                        _hover={{
                          bg: selectedSoul === soul.id ? "#3F7D58" : "#f0f9f4",
                          borderColor: "#437057",
                        }}
                        onClick={() => {
                          setSelectedSoul(soul.id || null)
                          setShowTrainingDocuments(true)
                        }}
                        size="sm"
                      >
                        {soul.name}
                      </Button>
                    ))}
                  </Flex>
                </Box>

                {/* Training Documents for Selected Soul */}
                {selectedSoul && showTrainingDocuments && (
                  <Box>
                    <Text mb={4} color="gray.600">
                      Training documents for:{" "}
                      <strong>
                        {aiSouls?.find((s) => s.id === selectedSoul)?.name}
                      </strong>
                    </Text>

                    {trainingDocuments && trainingDocuments.length > 0 ? (
                      <Grid
                        templateColumns="repeat(auto-fill, minmax(350px, 1fr))"
                        gap={6}
                      >
                        {trainingDocuments.map((doc) => (
                          <Box
                            key={doc.id}
                            p={5}
                            bg="white"
                            _dark={{ bg: "gray.800" }}
                            borderRadius="lg"
                            border="1px"
                            borderColor="#bbe7cc"
                            shadow="sm"
                            _hover={{ shadow: "md", borderColor: "#97B067" }}
                          >
                            <VStack gap={3} align="stretch">
                              <Heading size="md" color="#2F5249">
                                {doc.original_filename}
                              </Heading>

                              {doc.description && (
                                <Text fontSize="sm" color="gray.600">
                                  {doc.description}
                                </Text>
                              )}

                              {/* Status and Processing Info */}
                              <HStack justify="space-between" align="center">
                                <Badge
                                  colorScheme={getStatusColor(
                                    doc.processing_status,
                                  )}
                                  variant="subtle"
                                >
                                  {doc.processing_status}
                                </Badge>
                                <Text fontSize="xs" color="gray.500">
                                  {doc.chunk_count} chunks
                                </Text>
                              </HStack>

                              {/* File Info */}
                              <Text fontSize="xs" color="gray.500">
                                Size: {(doc.file_size / 1024).toFixed(1)} KB
                              </Text>
                              <Text fontSize="xs" color="gray.500">
                                Uploaded:{" "}
                                {new Date(
                                  doc.upload_timestamp,
                                ).toLocaleDateString()}
                              </Text>

                              {/* Action Buttons */}
                              <HStack gap={2} pt={2}>
                                <Button
                                  size="sm"
                                  colorScheme="red"
                                  variant="ghost"
                                  onClick={() =>
                                    handleDeleteTrainingDoc(doc.id)
                                  }
                                  loading={deleteTrainingDocMutation.isPending}
                                >
                                  <FiTrash2 style={{ marginRight: "0.5rem" }} />
                                  Delete
                                </Button>
                              </HStack>
                            </VStack>
                          </Box>
                        ))}
                      </Grid>
                    ) : (
                      <VStack py={8} gap={4}>
                        <Text color="gray.500">
                          No training documents found for this AI soul
                        </Text>
                        <Text fontSize="sm" color="gray.400">
                          Upload training documents through the Training section
                          to improve this AI soul's responses.
                        </Text>
                      </VStack>
                    )}
                  </Box>
                )}

                {!selectedSoul && (
                  <VStack py={8} gap={4}>
                    <Text color="gray.500">
                      Select an AI soul to view its training documents
                    </Text>
                  </VStack>
                )}
              </VStack>
            </Box>
          )}

          {/* Analytics Tab */}
          {activeTab === 3 && (
            <Box>
              <SearchAnalytics />
            </Box>
          )}
        </Box>
      </VStack>

      {/* Upload Dialog */}
      <DialogRoot
        open={isUploadDialogOpen}
        onOpenChange={({ open }) => setIsUploadDialogOpen(open)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <VStack gap={4}>
              <Field label="PDF Document" required>
                <VStack gap={2} align="stretch">
                  <Input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    p={1}
                  />
                  {selectedFile && (
                    <Box
                      p={3}
                      bg="gray.50"
                      borderRadius="md"
                      border="1px"
                      borderColor="gray.200"
                    >
                      <Text fontSize="sm" fontWeight="medium" color="gray.800">
                        Selected: {selectedFile.name}
                      </Text>
                      <Text fontSize="xs" color="gray.600">
                        Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </Text>
                      <Button
                        size="xs"
                        variant="ghost"
                        colorScheme="red"
                        mt={1}
                        onClick={() => {
                          setSelectedFile(null)
                          const fileInput = document.querySelector(
                            'input[type="file"]',
                          ) as HTMLInputElement
                          if (fileInput) fileInput.value = ""
                        }}
                      >
                        Remove
                      </Button>
                    </Box>
                  )}
                </VStack>
              </Field>
              <Field label="Description (Optional)">
                <Input
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter a description for this document (helps with searching)"
                  maxLength={500}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  {description.length}/500 characters
                </Text>
              </Field>
            </VStack>
          </DialogBody>
          <DialogFooter>
            <DialogCloseTrigger asChild>
              <Button variant="ghost">Cancel</Button>
            </DialogCloseTrigger>
            <Button
              colorScheme="teal"
              onClick={handleUpload}
              disabled={uploadMutation.isPending}
              loading={uploadMutation.isPending}
              loadingText="Uploading..."
            >
              Upload
            </Button>
          </DialogFooter>
        </DialogContent>
      </DialogRoot>
    </Container>
  )
}
