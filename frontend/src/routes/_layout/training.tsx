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
import { useQuery } from "@tanstack/react-query"
import { useNavigate, useSearch } from "@tanstack/react-router"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import {
  FiActivity,
  FiFileText,
  FiMessageSquare,
  FiPaperclip,
  FiUpload,
} from "react-icons/fi"
import {
  type AISoulEntity,
  AiSoulsService,
  TrainingService,
} from "../../client"
import { RoleGuard } from "../../components/Common/RoleGuard"
import useCustomToast from "../../hooks/useCustomToast"

interface TrainingMessage {
  id: string
  content: string
  is_from_trainer: boolean
  timestamp: string
}

interface TrainingSearchParams {
  soul?: string
}

export const Route = createFileRoute("/_layout/training")({
  component: Training,
  validateSearch: (search: Record<string, unknown>): TrainingSearchParams => {
    return {
      soul: search.soul as string,
    }
  },
})

export function Training() {
  return (
    <RoleGuard permission="access_training">
      <TrainingContent />
    </RoleGuard>
  )
}

function TrainingContent() {
  const navigate = useNavigate()
  const toast = useCustomToast()
  const search = useSearch({ from: "/_layout/training" })

  const [aiSoul, setAiSoul] = useState<AISoulEntity | null>(null)
  const [messages, setMessages] = useState<TrainingMessage[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploadingFile, setIsUploadingFile] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [activeTab, setActiveTab] = useState(0)
  const [trainingMetrics, setTrainingMetrics] = useState({
    totalMessages: 0,
    documentsUploaded: 0,
    lastTrainingSession: null as string | null,
  })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Fetch real training documents
  const { data: trainingDocuments, refetch: refetchDocuments } = useQuery({
    queryKey: ["training-documents", search.soul],
    queryFn: () => TrainingService.getTrainingDocuments({ aiSoulId: search.soul! }),
    enabled: !!search.soul,
  })

  const handleDeleteDocument = async (documentId: string) => {
    try {
      await TrainingService.deleteTrainingDocument({
        aiSoulId: search.soul!,
        documentId: documentId,
      })
      toast.success("Document deleted successfully")
      refetchDocuments()
    } catch (error) {
      toast.error("Failed to delete document")
    }
  }

  useEffect(() => {
    if (search.soul) {
      loadAiSoul(search.soul)
      loadTrainingMessages(search.soul)
    }
  }, [search.soul])

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const loadAiSoul = async (soulId: string) => {
    try {
      const soul = await AiSoulsService.getAiSoul({ aiSoulId: soulId })
      setAiSoul(soul)
    } catch (error) {
      toast.error("Failed to load AI soul")
      navigate({ to: "/ai-souls" })
    }
  }

  const loadTrainingMessages = async (soulId: string) => {
    try {
      // Load real training messages from API
      const messages = await TrainingService.getTrainingMessages({
        aiSoulId: soulId,
        skip: 0,
        limit: 50
      })
      
      // Convert API response to local message format
      const formattedMessages: TrainingMessage[] = messages.map(msg => ({
        id: msg.id,
        content: msg.content,
        is_from_trainer: msg.is_from_trainer || false,
        timestamp: msg.timestamp
      }))
      
      // Sort messages by timestamp (oldest first, newest last)
      const sortedMessages = formattedMessages.sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      )
      
      setMessages(sortedMessages)

      // Calculate real metrics from actual data
      const documentsCount = trainingDocuments?.length || 0
      // Only count messages from trainer (user inputs) as training sessions
      const trainerMessages = sortedMessages.filter(msg => msg.is_from_trainer)
      const totalTrainingSessions = trainerMessages.length
      const lastTrainerMessage = trainerMessages[trainerMessages.length - 1]
      
             setTrainingMetrics((prev) => ({
         ...prev,
         totalMessages: totalTrainingSessions,
         documentsUploaded: documentsCount,
         lastTrainingSession: lastTrainerMessage?.timestamp || null,
       }))
    } catch (error) {
      console.error("Failed to load training messages:", error)
      // Set empty state for real data
      setMessages([])
             setTrainingMetrics((prev) => ({
         ...prev,
         totalMessages: 0,
         documentsUploaded: trainingDocuments?.length || 0,
         lastTrainingSession: null,
       }))
    }
  }

  const sendTrainingMessage = async () => {
    if (!newMessage.trim() || !search.soul) return

    setIsLoading(true)
    try {
      // Add user message to UI immediately
      const userMessage: TrainingMessage = {
        id: Date.now().toString(),
        content: newMessage,
        is_from_trainer: true,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])
      
      // Update metrics immediately for trainer message
      setTrainingMetrics((prev) => ({
        ...prev,
        totalMessages: prev.totalMessages + 1,
        lastTrainingSession: userMessage.timestamp,
      }))
      
      const messageContent = newMessage
      setNewMessage("")

      // Send message to API
      const response = await TrainingService.sendTrainingMessage({
        aiSoulId: search.soul,
        requestBody: {
          content: messageContent,
          is_from_trainer: true,
        },
      })

      // The API generates an AI response automatically but doesn't return it
      // We need to reload messages to get the AI response
      await loadTrainingMessages(search.soul)
      
      // Auto-scroll to bottom to show the new AI response
      setTimeout(() => {
        scrollToBottom()
      }, 100)

      toast.success("Training message sent")
    } catch (error) {
      console.error("Failed to send training message:", error)
      toast.error("Failed to send training message")
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      const validTypes = ["application/pdf", "text/plain", "text/markdown"]
      const validExtensions = ['.pdf', '.txt', '.md']
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
      
      if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
        toast.error("Only PDF, TXT, and Markdown files are supported")
        return
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast.error("File size must be less than 10MB")
        return
      }

      setSelectedFile(file)
    }
  }

  const uploadTrainingFile = async () => {
    if (!selectedFile || !search.soul) return

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

      // Fix: Pass structured object instead of FormData
      await TrainingService.uploadTrainingDocument({
        aiSoulId: search.soul,
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

      toast.success(
        `Training document "${selectedFile.name}" uploaded successfully`,
      )
      refetchDocuments()
      
      // Update metrics after document upload
      setTrainingMetrics((prev) => ({
        ...prev,
        documentsUploaded: prev.documentsUploaded + 1,
      }))
    } catch (error) {
      toast.error("Failed to upload training document")
      setUploadProgress(0)
    } finally {
      setIsUploadingFile(false)
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      sendTrainingMessage()
    }
  }

  // Get available AI souls for selection
  const { data: availableSouls } = useQuery({
    queryKey: ["ai-souls"],
    queryFn: () => AiSoulsService.getAiSouls(),
  })

  if (!search.soul) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack gap={6} align="stretch">
          <Heading size="lg" color="#2F5249">
            Select AI Soul for Training
          </Heading>
          <Text color="gray.600">
            Choose an AI Soul to start training and improve its responses.
          </Text>

          {availableSouls && availableSouls.length > 0 ? (
            <Grid
              templateColumns="repeat(auto-fill, minmax(300px, 1fr))"
              gap={6}
            >
              {availableSouls.map((soul: AISoulEntity) => (
                <Box
                  key={soul.id}
                  p={6}
                  bg="white"
                  borderRadius="lg"
                  border="1px"
                  borderColor="#bbe7cc"
                  shadow="sm"
                  _hover={{ shadow: "md", borderColor: "#97B067" }}
                  transition="all 0.2s"
                  cursor="pointer"
                  onClick={() =>
                    navigate({ to: "/training", search: { soul: soul.id } })
                  }
                >
                  <VStack align="start" gap={3}>
                    <Heading size="md" color="#2F5249">
                      {soul.name}
                    </Heading>
                    <Text fontSize="sm" color="gray.600">
                      {soul.description}
                    </Text>
                    <Badge colorScheme="gray" variant="subtle">
                      {soul.persona_type}
                    </Badge>
                    <Button
                      size="sm"
                      bg="#437057"
                      color="white"
                      _hover={{ bg: "#3F7D58" }}
                      onClick={(e) => {
                        e.stopPropagation()
                        navigate({ to: "/training", search: { soul: soul.id } })
                      }}
                    >
                      Start Training
                    </Button>
                  </VStack>
                </Box>
              ))}
            </Grid>
          ) : (
            <VStack gap={4}>
              <Text color="gray.500">No AI souls available for training</Text>
              <Button
                bg="#437057"
                color="white"
                _hover={{ bg: "#3F7D58" }}
                onClick={() => navigate({ to: "/ai-souls" })}
              >
                Create Your First AI Soul
              </Button>
            </VStack>
          )}
        </VStack>
      </Container>
    )
  }

  return (
    <Box h="calc(100vh - 8rem)" display="flex" flexDirection="column">
      {/* Header */}
      <Box p={4} borderBottom="1px" borderColor="gray.200" bg="white">
        <Flex justify="space-between" align="center">
          <VStack align="start">
            <Heading size="lg">Training {aiSoul?.name || "AI Soul"}</Heading>
            <Text color="gray.500">
              Train your AI soul and track progress with advanced metrics
            </Text>
          </VStack>
          <Button
            variant="outline"
            onClick={() => navigate({ to: "/ai-souls" })}
          >
            Back to AI Souls
          </Button>
        </Flex>
      </Box>

      {/* Tab Navigation */}
      <Box borderBottom="1px" borderColor="gray.200" bg="white">
        <Flex gap={4} px={4} pb={4}>
          <Button
            variant={activeTab === 0 ? "solid" : "ghost"}
            bg={activeTab === 0 ? "#437057" : "transparent"}
            bgColor={activeTab === 1 ? "gray.100" : "#437057"}
            color={activeTab === 0 ? "white" : "gray.600"}
            _hover={{ bg: activeTab === 0 ? "#2F5249" : "gray.100" }}
            onClick={() => setActiveTab(0)}
            size="lg"
          >
            Training Chat
          </Button>
          <Button
            variant={activeTab === 1 ? "solid" : "ghost"}
            bg={activeTab === 1 ? "#437057" : "transparent"}
            bgColor={activeTab === 0 ? "gray.100" : "#437057"}
            color={activeTab === 1 ? "white" : "gray.600"}
            _hover={{ bg: activeTab === 1 ? "#2F5249" : "gray.100" }}
            onClick={() => setActiveTab(1)}
            size="lg"
          >
            Training Metrics
          </Button>
        </Flex>
      </Box>

      {/* Tab Content */}
      <Box flex={1} overflow="hidden">
        {/* Training Chat Tab */}
        {activeTab === 0 && (
          <Box h="100%" display="flex" flexDirection="column">
            {/* Messages */}
            <Box flex={1} overflow="auto" p={4} bg="gray.50">
              {messages.length === 0 ? (
                <VStack 
                  justify="center" 
                  align="center" 
                  h="100%" 
                  gap={4}
                  color="gray.500"
                >
                  <Box fontSize="48px">💬</Box>
                  <VStack gap={2} textAlign="center">
                    <Text fontSize="lg" fontWeight="medium" color="gray.600">
                      Start Training {aiSoul?.name || "Your AI Soul"}
                    </Text>
                    <Text fontSize="sm" color="gray.500" maxW="300px">
                      Send messages to train your AI soul's personality and responses. 
                      Each conversation helps it learn your communication style.
                    </Text>
                  </VStack>
                  <Box 
                    p={3} 
                    bg="blue.50" 
                    borderRadius="md" 
                    border="1px solid" 
                    borderColor="blue.200"
                    maxW="400px"
                  >
                    <Text fontSize="xs" color="blue.600" textAlign="center">
                      💡 <strong>Tip:</strong> Start with "Tell me about yourself" or describe how you want your AI to respond
                    </Text>
                  </Box>
                </VStack>
              ) : (
                <VStack align="stretch" gap={4}>
                  {messages.map((message) => (
                    <Box
                      key={message.id}
                      alignSelf={
                        message.is_from_trainer ? "flex-end" : "flex-start"
                      }
                      maxW="70%"
                    >
                      <Box
                        bg={message.is_from_trainer ? "blue.500" : "gray.100"}
                        color={message.is_from_trainer ? "white" : "black"}
                        p={3}
                        borderRadius="lg"
                        borderBottomRightRadius={
                          message.is_from_trainer ? "sm" : "lg"
                        }
                        borderBottomLeftRadius={
                          message.is_from_trainer ? "lg" : "sm"
                        }
                        boxShadow="sm"
                      >
                        <Text>{message.content}</Text>
                        <Text fontSize="xs" opacity={0.7} mt={1}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </Text>
                      </Box>
                    </Box>
                  ))}
                  <div ref={messagesEndRef} />
                </VStack>
              )}
            </Box>

            {/* Input Area */}
            <Box p={4} bg="white" borderTop="1px" borderColor="gray.200">
              <VStack gap={4}>
                {/* File Upload */}
                <Flex w="100%" justify="space-between" align="center">
                  <Text fontSize="sm" color="gray.600">
                    {selectedFile
                      ? `Selected: ${selectedFile.name}`
                      : "No file selected"}
                  </Text>
                  <HStack>
                    <Button
                      size="sm"
                      onClick={() => fileInputRef.current?.click()}
                      variant="outline"
                    >
                      <Icon as={FiPaperclip} mr={2} />
                      Choose File
                    </Button>
                    {selectedFile && (
                      <Button
                        size="sm"
                        colorScheme="teal"
                        onClick={uploadTrainingFile}
                        loading={isUploadingFile}
                      >
                        <Icon as={FiUpload} mr={2} />
                        Upload
                      </Button>
                    )}
                  </HStack>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    style={{ display: "none" }}
                    accept=".pdf,.txt,.md"
                  />
                </Flex>

                {/* Upload Progress */}
                {isUploadingFile && (
                  <Box w="100%">
                    <Flex justify="space-between" mb={2}>
                      <Text fontSize="sm" color="gray.600">
                        Uploading...
                      </Text>
                      <Text fontSize="sm" fontWeight="bold">
                        {uploadProgress}%
                      </Text>
                    </Flex>
                    <Box bg="gray.200" borderRadius="md" h="6px" w="100%">
                      <Box
                        bg="#437057"
                        h="100%"
                        borderRadius="md"
                        w={`${uploadProgress}%`}
                        transition="width 0.3s ease"
                      />
                    </Box>
                  </Box>
                )}

                {/* Message Input */}
                <Flex w="100%" gap={2}>
                  <Input
                    placeholder="Type your message to train your AI Soul Entity..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={handleKeyPress}
                    size="lg"
                    disabled={isLoading}
                    bg="white"
                    _focus={{ boxShadow: "outline" }}
                  />
                  <Button
                    bg="#437057"
                    color="white"
                    _hover={{ bg: "#2F5249" }}
                    onClick={sendTrainingMessage}
                    loading={isLoading}
                    size="lg"
                    minW="80px"
                    flexShrink={0}
                  >
                    Send
                  </Button>
                </Flex>
              </VStack>
            </Box>
          </Box>
        )}

        {/* Training Management Tab */}
        {activeTab === 1 && (
          <Box p={6} overflow="auto">
            <VStack gap={6} align="stretch">
              <Heading size="xl" color="#2F5249">
                Training Management
              </Heading>



              {/* Training Overview */}
              <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
                <Box
                  p={6}
                  bg="white"
                  borderRadius="lg"
                  border="1px"
                  borderColor="gray.200"
                  shadow="sm"
                >
                  <VStack align="start" gap={3}>
                    <HStack>
                      <Icon as={FiMessageSquare} color="#437057" boxSize="20px" />
                      <Text fontSize="sm" color="gray.600" fontWeight="medium">
                        Training Sessions
                      </Text>
                    </HStack>
                    <Text fontSize="3xl" fontWeight="bold" color="#2F5249">
                      {trainingMetrics.totalMessages}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      Messages exchanged
                    </Text>
                  </VStack>
                </Box>

                <Box
                  p={6}
                  bg="white"
                  borderRadius="lg"
                  border="1px"
                  borderColor="gray.200"
                  shadow="sm"
                >
                  <VStack align="start" gap={3}>
                    <HStack>
                      <Icon as={FiFileText} color="#437057" boxSize="20px" />
                      <Text fontSize="sm" color="gray.600" fontWeight="medium">
                        Training Materials
                      </Text>
                    </HStack>
                    <Text fontSize="3xl" fontWeight="bold" color="#2F5249">
                      {trainingMetrics.documentsUploaded}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      Documents processed
                    </Text>
                  </VStack>
                </Box>

                <Box
                  p={6}
                  bg="white"
                  borderRadius="lg"
                  border="1px"
                  borderColor="gray.200"
                  shadow="sm"
                >
                  <VStack align="start" gap={3}>
                    <HStack>
                      <Icon as={FiActivity} color="#437057" boxSize="20px" />
                      <Text fontSize="sm" color="gray.600" fontWeight="medium">
                        Last Session
                      </Text>
                    </HStack>
                    <Text fontSize="lg" fontWeight="bold" color="#2F5249">
                      {trainingMetrics.lastTrainingSession
                        ? new Date(trainingMetrics.lastTrainingSession).toLocaleDateString()
                        : "Never"}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      Most recent training
                    </Text>
                  </VStack>
                </Box>
              </Grid>

              {/* Document Management */}
              <Box
                p={6}
                bg="white"
                borderRadius="lg"
                border="1px"
                borderColor="gray.200"
                shadow="sm"
              >
                <VStack align="stretch" gap={6}>
                  <Flex justify="space-between" align="center">
                    <Heading size="xl" color="#2F5249">
                      Document Management
                    </Heading>
                    {/* <Button
                      onClick={() => fileInputRef.current?.click()}
                      bg="#437057"
                      color="white"
                      _hover={{ bg: "#2F5249" }}
                      size="sm"
                    >
                      <Icon as={FiUpload} mr={2} />
                       Document
                    </Button> */}
                  </Flex>

                  {/* Upload Area */}
                  {selectedFile && (
                    <Box
                      p={4}
                      bg="blue.50"
                      borderRadius="md"
                      border="1px"
                      borderColor="blue.200"
                    >
                      <VStack align="stretch" gap={3}>
                        <Text fontSize="sm" color="blue.800" fontWeight="medium">
                          Ready to upload: {selectedFile.name}
                        </Text>
                        <Flex gap={3}>
                          <Button
                            size="sm"
                            bg="#437057"
                            color="white"
                            _hover={{ bg: "#2F5249" }}
                            onClick={uploadTrainingFile}
                            loading={isUploadingFile}
                          >
                            Upload Document
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedFile(null)}
                          >
                            Cancel
                          </Button>
                        </Flex>
                      </VStack>
                    </Box>
                  )}

                  {/* Upload Progress */}
                  {isUploadingFile && (
                    <Box
                      p={4}
                      bg="green.50"
                      borderRadius="md"
                      border="1px"
                      borderColor="green.200"
                    >
                      <VStack align="stretch" gap={3}>
                        <Flex justify="space-between" align="center">
                          <Text fontSize="sm" color="green.800" fontWeight="medium">
                            Uploading document...
                          </Text>
                          <Text fontSize="sm" fontWeight="bold" color="green.800">
                            {uploadProgress}%
                          </Text>
                        </Flex>
                        <Box bg="green.200" borderRadius="md" h="6px" w="100%">
                          <Box
                            bg="green.500"
                            h="100%"
                            borderRadius="md"
                            w={`${uploadProgress}%`}
                            transition="width 0.3s ease"
                          />
                        </Box>
                      </VStack>
                    </Box>
                  )}

                  {/* Documents List */}
                  <VStack align="stretch" gap={4}>
                    <Text fontSize="sm" color="gray.600" fontWeight="medium">
                      Training Documents ({trainingDocuments?.length || 0})
                    </Text>

                    {trainingDocuments && trainingDocuments.length > 0 ? (
                      <VStack align="stretch" gap={3}>
                        {trainingDocuments.map((doc) => (
                          <Box
                            key={doc.id}
                            p={4}
                            bg="gray.50"
                            borderRadius="md"
                            border="1px"
                            borderColor="gray.200"
                            _hover={{ bg: "gray.100" }}
                            transition="background-color 0.2s"
                          >
                            <Flex justify="space-between" align="start">
                              <VStack align="start" gap={2}>
                                <Text fontWeight="medium" color="#2F5249">
                                  {doc.original_filename}
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                  {doc.description}
                                </Text>
                                <HStack gap={4}>
                                  <Text fontSize="xs" color="gray.500">
                                    {(doc.file_size / 1024).toFixed(1)} KB
                                  </Text>
                                  <Text fontSize="xs" color="gray.500">
                                    {new Date(doc.upload_timestamp).toLocaleDateString()}
                                  </Text>
                                  <Badge
                                    colorScheme={
                                      doc.processing_status === "completed"
                                        ? "green"
                                        : "yellow"
                                    }
                                    size="sm"
                                  >
                                    {doc.processing_status}
                                  </Badge>
                                </HStack>
                              </VStack>
                              <Button
                                size="sm"
                                colorScheme="red"
                                variant="ghost"
                                onClick={() => handleDeleteDocument(doc.id)}
                              >
                                Delete
                              </Button>
                            </Flex>
                          </Box>
                        ))}
                      </VStack>
                    ) : (
                      <Box
                        p={8}
                        bg="gray.50"
                        borderRadius="md"
                        border="2px"
                        borderColor="gray.200"
                        borderStyle="dashed"
                        textAlign="center"
                      >
                        <VStack gap={3}>
                          <Icon as={FiFileText} boxSize="32px" color="gray.400" />
                          <Text fontSize="sm" color="gray.500" fontWeight="medium">
                            No training documents uploaded yet
                          </Text>
                          <Text fontSize="xs" color="gray.400">
                            Upload documents to provide training materials for your AI soul
                          </Text>
                          <Button
                            size="sm"
                            onClick={() => fileInputRef.current?.click()}
                            bg="#437057"
                            color="white"
                            _hover={{ bg: "#2F5249" }}
                            mt={2}
                          >
                            <Icon as={FiUpload} mr={2} />
                            Upload First Document
                          </Button>
                        </VStack>
                      </Box>
                    )}
                  </VStack>

                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    style={{ display: "none" }}
                    accept=".pdf,.txt,.md"
                  />
                </VStack>
              </Box>
            </VStack>
          </Box>
        )}
      </Box>
    </Box>
  )
}
