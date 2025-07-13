import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  HStack,
  Heading,
  Input,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import React, { useState } from "react"
import {
  FiActivity,
  FiAlertCircle,
  FiCheckCircle,
  FiDatabase,
  FiPlay,
  FiRefreshCw,
  FiSearch,
  FiXCircle,
} from "react-icons/fi"

import {
  type ApiError,
  type DocumentPublic,
  DocumentsService,
  EnhancedRagService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { getStatusColor as getThemeStatusColor } from "../../theme/colors"
import { RoleGuard } from "../Common/RoleGuard"

export function AdvancedRAGManagement() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState("bulk-processing")
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState("")

  // Get all documents for bulk processing
  const { data: documents, isLoading: documentsLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: () => DocumentsService.getDocuments(),
  })

  // Get system health status
  const {
    data: healthStatus,
    isLoading: healthLoading,
    refetch: refetchHealth,
  } = useQuery({
    queryKey: ["rag-health"],
    queryFn: () => EnhancedRagService.healthCheck(),
  })

  // Get collection info
  const {
    data: collectionInfo,
    isLoading: collectionLoading,
    refetch: refetchCollection,
  } = useQuery({
    queryKey: ["collection-info"],
    queryFn: () => EnhancedRagService.getCollectionInfo(),
  })

  // Get search suggestions
  const {
    data: searchSuggestions,
    isLoading: suggestionsLoading,
    refetch: refetchSuggestions,
  } = useQuery({
    queryKey: ["search-suggestions", searchQuery],
    queryFn: () =>
      EnhancedRagService.getSearchSuggestions({
        query: searchQuery,
        limit: 20,
      }),
    enabled: searchQuery.length >= 2,
  })

  // Bulk process documents mutation
  const bulkProcessMutation = useMutation({
    mutationFn: (documentIds: string[]) =>
      EnhancedRagService.bulkProcessDocuments({
        requestBody: documentIds,
        chunkingStrategy: "semantic",
      }),
    onSuccess: (data: any) => {
      showSuccessToast(
        `Successfully processed ${data.total_documents} documents`,
      )
      queryClient.invalidateQueries({ queryKey: ["documents"] })
      queryClient.invalidateQueries({ queryKey: ["collection-info"] })
      setSelectedDocuments([])
    },
    onError: (err: ApiError) => {
      const errDetail = (err.body as any)?.detail
      showErrorToast(`Failed to process documents: ${errDetail}`)
    },
  })

  const handleDocumentSelection = (documentId: string) => {
    setSelectedDocuments((prev) =>
      prev.includes(documentId)
        ? prev.filter((id) => id !== documentId)
        : [...prev, documentId],
    )
  }

  const handleSelectAll = () => {
    if (!documents?.data) return

    if (selectedDocuments.length === documents.data.length) {
      setSelectedDocuments([])
    } else {
      setSelectedDocuments(documents.data.map((doc) => doc.id))
    }
  }

  const handleBulkProcess = () => {
    if (selectedDocuments.length === 0) {
      showErrorToast("Please select documents to process")
      return
    }
    bulkProcessMutation.mutate(selectedDocuments)
  }

  const getStatusColor = (status: string) => {
    return getThemeStatusColor(status)
  }

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case "healthy":
      case "ok":
      case "completed":
      case "processed":
        return <FiCheckCircle />
      case "degraded":
      case "warning":
      case "processing":
        return <FiAlertCircle />
      case "unhealthy":
      case "error":
      case "failed":
        return <FiXCircle />
      default:
        return <FiActivity />
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Number.parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num)
  }

  return (
    <RoleGuard permission="admin">
      <Container maxW="7xl" py={8}>
        <VStack gap={8} align="stretch">
          <Flex justify="space-between" align="center">
            <Heading size="lg">Advanced RAG Management</Heading>
            <Button
              onClick={() => {
                refetchHealth()
                refetchCollection()
                refetchSuggestions()
              }}
              size="sm"
              colorScheme="teal"
            >
              <FiRefreshCw /> Refresh
            </Button>
          </Flex>

          {/* Tab Navigation */}
          <HStack gap={4}>
            <Button
              variant={activeTab === "bulk-processing" ? "solid" : "outline"}
              onClick={() => setActiveTab("bulk-processing")}
              colorScheme="teal"
            >
              <FiDatabase /> Bulk Processing
            </Button>
            <Button
              variant={activeTab === "health" ? "solid" : "outline"}
              onClick={() => setActiveTab("health")}
              colorScheme="teal"
            >
              <FiActivity /> System Health
            </Button>
            <Button
              variant={activeTab === "analytics" ? "solid" : "outline"}
              onClick={() => setActiveTab("analytics")}
              colorScheme="teal"
            >
              <FiSearch /> Search Analytics
            </Button>
          </HStack>

          {/* Bulk Processing Tab */}
          {activeTab === "bulk-processing" && (
            <VStack gap={6} align="stretch">
              <Box
                p={6}
                bg="white"
                borderRadius="lg"
                border="1px"
                borderColor="gray.200"
                shadow="sm"
              >
                <VStack gap={4} align="stretch">
                  <Flex justify="space-between" align="center">
                    <Heading size="md">Document Processing</Heading>
                    <Button
                      onClick={handleSelectAll}
                      size="sm"
                      variant="outline"
                      colorScheme="gray"
                    >
                      {selectedDocuments.length === documents?.data?.length
                        ? "Deselect All"
                        : "Select All"}
                    </Button>
                  </Flex>

                  {documentsLoading ? (
                    <Flex justify="center" p={8}>
                      <Spinner size="lg" />
                    </Flex>
                  ) : (
                    <VStack gap={3} align="stretch">
                      {documents?.data?.map((doc: DocumentPublic) => (
                        <Box
                          key={doc.id}
                          p={4}
                          bg="gray.50"
                          borderRadius="md"
                          border="1px"
                          borderColor="gray.200"
                        >
                          <Flex justify="space-between" align="center">
                            <HStack>
                              <input
                                type="checkbox"
                                checked={selectedDocuments.includes(doc.id)}
                                onChange={() => handleDocumentSelection(doc.id)}
                              />
                              <VStack align="start" gap={1}>
                                <Text fontWeight="medium">
                                  {doc.original_filename}
                                </Text>
                                {doc.description && (
                                  <Text fontSize="xs" color="gray.500">
                                    {doc.description}
                                  </Text>
                                )}
                              </VStack>
                            </HStack>
                            <HStack>
                              <Badge
                                colorScheme={getStatusColor(
                                  doc.processing_status,
                                )}
                              >
                                {doc.processing_status}
                              </Badge>
                              <Text fontSize="sm">
                                {formatBytes(doc.file_size)}
                              </Text>
                              <Text fontSize="sm">
                                {doc.chunk_count || 0} chunks
                              </Text>
                            </HStack>
                          </Flex>
                        </Box>
                      ))}
                    </VStack>
                  )}

                  <HStack>
                    <Button
                      colorScheme="teal"
                      onClick={handleBulkProcess}
                      disabled={
                        bulkProcessMutation.isPending ||
                        selectedDocuments.length === 0
                      }
                    >
                      <FiPlay />{" "}
                      {bulkProcessMutation.isPending
                        ? "Processing..."
                        : `Process Selected (${selectedDocuments.length})`}
                    </Button>
                  </HStack>
                </VStack>
              </Box>
            </VStack>
          )}

          {/* System Health Tab */}
          {activeTab === "health" && (
            <VStack gap={6} align="stretch">
              {healthLoading ? (
                <Flex justify="center" p={8}>
                  <Spinner size="lg" />
                </Flex>
              ) : healthStatus &&
                typeof healthStatus === "object" &&
                "status" in healthStatus ? (
                <Box
                  p={6}
                  bg="white"
                  borderRadius="lg"
                  border="1px"
                  borderColor="gray.200"
                  shadow="sm"
                >
                  <VStack gap={4} align="stretch">
                    <HStack>
                      <Box
                        color={`${getStatusColor((healthStatus as any).status)}.500`}
                      >
                        {getStatusIcon((healthStatus as any).status)}
                      </Box>
                      <Heading size="md">System Status</Heading>
                      <Badge
                        colorScheme={getStatusColor(
                          (healthStatus as any).status,
                        )}
                        fontSize="sm"
                      >
                        {(
                          (healthStatus as any).status || "unknown"
                        ).toUpperCase()}
                      </Badge>
                    </HStack>

                    <VStack gap={4} align="stretch">
                      {(healthStatus as any).components &&
                        Object.entries((healthStatus as any).components).map(
                          ([component, status]) => (
                            <Box
                              key={component}
                              p={4}
                              bg="gray.50"
                              borderRadius="md"
                              border="1px"
                              borderColor="gray.200"
                            >
                              <HStack justify="space-between">
                                <HStack>
                                  <Box
                                    color={`${getStatusColor((status as any).status)}.500`}
                                  >
                                    {getStatusIcon((status as any).status)}
                                  </Box>
                                  <Text
                                    fontWeight="medium"
                                    textTransform="capitalize"
                                  >
                                    {component}
                                  </Text>
                                </HStack>
                                <HStack>
                                  <Badge
                                    colorScheme={getStatusColor(
                                      (status as any).status,
                                    )}
                                    size="sm"
                                  >
                                    {(status as any).status}
                                  </Badge>
                                  {(status as any).response_time_ms && (
                                    <Text fontSize="sm" color="gray.500">
                                      {(status as any).response_time_ms}ms
                                    </Text>
                                  )}
                                </HStack>
                              </HStack>
                            </Box>
                          ),
                        )}
                    </VStack>

                    <Text fontSize="sm" color="gray.500">
                      Last updated:{" "}
                      {(healthStatus as any).timestamp
                        ? new Date(
                            (healthStatus as any).timestamp,
                          ).toLocaleString()
                        : "Unknown"}
                    </Text>
                  </VStack>
                </Box>
              ) : (
                <Box
                  p={4}
                  bg="red.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="red.200"
                >
                  <VStack>
                    <Text fontWeight="medium" color="red.800">
                      Unable to fetch system health!
                    </Text>
                    <Text fontSize="sm" color="red.600">
                      There was an error retrieving system health information.
                    </Text>
                  </VStack>
                </Box>
              )}

              {/* Collection Info */}
              {collectionLoading ? (
                <Flex justify="center" p={8}>
                  <Spinner size="lg" />
                </Flex>
              ) : collectionInfo && typeof collectionInfo === "object" ? (
                <Box
                  p={6}
                  bg="white"
                  borderRadius="lg"
                  border="1px"
                  borderColor="gray.200"
                  shadow="sm"
                >
                  <VStack gap={4} align="stretch">
                    <Heading size="md">Vector Database</Heading>

                    <HStack gap={8}>
                      <Box>
                        <Text fontSize="sm" color="gray.500">
                          Total Vectors
                        </Text>
                        <Text fontSize="2xl" fontWeight="bold">
                          {formatNumber(
                            (collectionInfo as any).total_vectors || 0,
                          )}
                        </Text>
                      </Box>
                      <Box>
                        <Text fontSize="sm" color="gray.500">
                          Total Points
                        </Text>
                        <Text fontSize="2xl" fontWeight="bold">
                          {formatNumber(
                            (collectionInfo as any).total_points || 0,
                          )}
                        </Text>
                      </Box>
                      <Box>
                        <Text fontSize="sm" color="gray.500">
                          Disk Usage
                        </Text>
                        <Text fontSize="2xl" fontWeight="bold">
                          {formatBytes(
                            (collectionInfo as any).total_disk_size || 0,
                          )}
                        </Text>
                      </Box>
                      <Box>
                        <Text fontSize="sm" color="gray.500">
                          RAM Usage
                        </Text>
                        <Text fontSize="2xl" fontWeight="bold">
                          {formatBytes(
                            (collectionInfo as any).total_ram_size || 0,
                          )}
                        </Text>
                      </Box>
                    </HStack>

                    <VStack gap={3} align="stretch">
                      <Text fontWeight="medium">Collections</Text>
                      {(collectionInfo as any).collections &&
                        Array.isArray((collectionInfo as any).collections) &&
                        (collectionInfo as any).collections.map(
                          (collection: any) => (
                            <Box
                              key={collection.name}
                              p={4}
                              bg="gray.50"
                              borderRadius="md"
                              border="1px"
                              borderColor="gray.200"
                            >
                              <HStack justify="space-between">
                                <Text fontWeight="medium">
                                  {collection.name}
                                </Text>
                                <HStack gap={4}>
                                  <Text fontSize="sm">
                                    Vectors:{" "}
                                    {formatNumber(
                                      collection.vectors_count || 0,
                                    )}
                                  </Text>
                                  <Text fontSize="sm">
                                    Points:{" "}
                                    {formatNumber(collection.points_count || 0)}
                                  </Text>
                                  <Text fontSize="sm">
                                    Disk:{" "}
                                    {formatBytes(
                                      collection.disk_data_size || 0,
                                    )}
                                  </Text>
                                  <Text fontSize="sm">
                                    RAM:{" "}
                                    {formatBytes(collection.ram_data_size || 0)}
                                  </Text>
                                </HStack>
                              </HStack>
                            </Box>
                          ),
                        )}
                    </VStack>
                  </VStack>
                </Box>
              ) : (
                <Box
                  p={4}
                  bg="red.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="red.200"
                >
                  <VStack>
                    <Text fontWeight="medium" color="red.800">
                      Unable to fetch collection info!
                    </Text>
                    <Text fontSize="sm" color="red.600">
                      There was an error retrieving vector database information.
                    </Text>
                  </VStack>
                </Box>
              )}
            </VStack>
          )}

          {/* Search Analytics Tab */}
          {activeTab === "analytics" && (
            <VStack gap={6} align="stretch">
              <Box
                p={6}
                bg="white"
                borderRadius="lg"
                border="1px"
                borderColor="gray.200"
                shadow="sm"
              >
                <VStack gap={4} align="stretch">
                  <Heading size="md">Search Suggestions</Heading>
                  <Text color="gray.500">
                    Analyze and manage popular search queries
                  </Text>

                  <Box>
                    <Text mb={2}>Search Query</Text>
                    <Input
                      placeholder="Type to see suggestions..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </Box>

                  {searchQuery.length >= 2 && (
                    <Box>
                      <Heading size="sm" mb={3}>
                        Popular Suggestions
                      </Heading>
                      {suggestionsLoading ? (
                        <Spinner size="sm" />
                      ) : searchSuggestions &&
                        typeof searchSuggestions === "object" &&
                        "suggestions" in searchSuggestions &&
                        Array.isArray((searchSuggestions as any).suggestions) &&
                        (searchSuggestions as any).suggestions.length > 0 ? (
                        <VStack gap={2} align="stretch">
                          {(searchSuggestions as any).suggestions.map(
                            (suggestion: any, index: number) => (
                              <Box
                                key={index}
                                p={3}
                                bg="gray.50"
                                borderRadius="md"
                                border="1px"
                                borderColor="gray.200"
                              >
                                <Flex justify="space-between" align="center">
                                  <Text>{suggestion.text}</Text>
                                  <Badge colorScheme="teal">
                                    {suggestion.count} searches
                                  </Badge>
                                </Flex>
                              </Box>
                            ),
                          )}
                        </VStack>
                      ) : (
                        <Text color="gray.500">No suggestions found</Text>
                      )}
                    </Box>
                  )}
                </VStack>
              </Box>
            </VStack>
          )}
        </VStack>
      </Container>
    </RoleGuard>
  )
}
