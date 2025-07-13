import { useEffect, useRef, useState } from "react"
import {
    Box,
    Button,
    Container,
    Flex,
    HStack,
    Input,
    Text,
    VStack,
    Icon,
    useDisclosure,
} from "@chakra-ui/react"
import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query"
import { FiSend, FiChevronDown, FiChevronUp } from "react-icons/fi"
import { createFileRoute, useNavigate, useSearch } from "@tanstack/react-router"

import {
    AiSoulsService,
    ChatService,
    type ChatCreateChatMessageData,
    type ChatMessagePublic,
    type ChatMessagePairResponse,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"

function Chat() {
    const navigate = useNavigate()
    const search = useSearch({ from: "/_layout/chat" })
    const [selectedSoulId, setSelectedSoulId] = useState<string>("")
    const [message, setMessage] = useState("")
    const [hasPendingReview, setHasPendingReview] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const queryClient = useQueryClient()
    const toast = useCustomToast()

    // Helper functions for localStorage
    const getStoredTemporaryMessages = (soulId: string): ChatMessagePublic[] => {
        try {
            const stored = localStorage.getItem(`temp-messages-${soulId}`)
            return stored ? JSON.parse(stored) : []
        } catch {
            return []
        }
    }

    const storeTemporaryMessage = (soulId: string, message: ChatMessagePublic) => {
        try {
            const existing = getStoredTemporaryMessages(soulId)
            const updated = [...existing, message]
            localStorage.setItem(`temp-messages-${soulId}`, JSON.stringify(updated))
        } catch {
            // Ignore storage errors
        }
    }

    const clearTemporaryMessages = (soulId: string) => {
        try {
            localStorage.removeItem(`temp-messages-${soulId}`)
        } catch {
            // Ignore storage errors
        }
    }

    // Load AI soul data
    const { data: aiSoul } = useQuery({
        queryKey: ["ai-soul", selectedSoulId],
        queryFn: () => AiSoulsService.getAiSoul({ aiSoulId: selectedSoulId }),
        enabled: !!selectedSoulId
    })

    // Load messages when soul ID is available
    const { data: messages, isLoading: messagesLoading } = useQuery({
        queryKey: ["chat-messages", selectedSoulId],
        queryFn: async () => {
            const result = await ChatService.getChatMessages({ 
                aiSoulId: selectedSoulId,
                skip: 0,
                limit: 100
            })
            
            // Get stored temporary messages from localStorage
            const storedTemporaryMessages = getStoredTemporaryMessages(selectedSoulId)
            
            console.log('🔵 MESSAGES QUERY:', {
                dbMessages: result.length,
                storedTempMessages: storedTemporaryMessages.length,
                storedTempDetails: storedTemporaryMessages
            })
            
            // Merge database messages with stored temporary messages
            const mergedMessages = [...result, ...storedTemporaryMessages]
            console.log('🔵 MERGED MESSAGES:', mergedMessages.length)
            return mergedMessages
        },
        enabled: !!selectedSoulId,
        refetchInterval: hasPendingReview ? false : 5000, // Don't refetch while pending review
        refetchIntervalInBackground: true, // Keep refreshing in background
    })

    // Send message mutation with optimistic updates
    const sendMessageMutation = useMutation({
        mutationFn: async (messageData: ChatCreateChatMessageData) => {
            return await ChatService.createChatMessage(messageData)
        },
        onMutate: async (messageData) => {
            // Cancel any outgoing refetches
            await queryClient.cancelQueries({ queryKey: ["chat-messages", selectedSoulId] })

            // Snapshot the previous value
            const previousMessages = queryClient.getQueryData<ChatMessagePublic[]>(["chat-messages", selectedSoulId])

            // Optimistically update to the new value
            const optimisticUserMessage: ChatMessagePublic = {
                id: `temp-${Date.now()}`, // Temporary ID
                content: messageData.requestBody.content,
                user_id: "current-user", // Will be replaced by server response
                ai_soul_id: selectedSoulId,
                is_from_user: true,
                timestamp: new Date().toISOString(),
                is_temporary: false,
            }

            queryClient.setQueryData<ChatMessagePublic[]>(
                ["chat-messages", selectedSoulId], 
                (old) => old ? [...old, optimisticUserMessage] : [optimisticUserMessage]
            )

            // Return a context object with the snapshotted value
            return { previousMessages, optimisticUserMessage }
        },
        onError: (err, context) => {
            // If the mutation fails, use the context returned from onMutate to roll back
            queryClient.setQueryData(["chat-messages", selectedSoulId], (context as any)?.previousMessages)
            
            // Check if it's a pending review error (429 status)
            if (err.message?.includes("messages under review")) {
                setHasPendingReview(true)
                toast.error("Please wait for counselor approval before sending new messages", {
                    duration: 5000,
                })
            } else {
                toast.error(err.message || "Failed to send message")
            }
        },
        onSuccess: (data: ChatMessagePairResponse) => {
            // Handle the new response format with both user and AI messages
            const { user_message, ai_message } = data
            
            console.log('🔵 CHAT RESPONSE RECEIVED:', {
                user_message: {
                    content: user_message.content,
                    is_temporary: user_message.is_temporary
                },
                ai_message: {
                    content: ai_message.content,
                    is_temporary: ai_message.is_temporary,
                    id: ai_message.id
                }
            })
            
            // Debug logging for temporary messages
            if (ai_message.is_temporary) {
                console.log('🔶 TEMPORARY MESSAGE RECEIVED:', {
                    content: ai_message.content,
                    is_temporary: ai_message.is_temporary,
                    id: ai_message.id
                })
                // Store temporary message in localStorage
                storeTemporaryMessage(selectedSoulId, ai_message)
                console.log('🔶 STORED IN LOCALSTORAGE:', getStoredTemporaryMessages(selectedSoulId))
                // Set pending review state if we get a temporary message
                setHasPendingReview(true)
            } else {
                console.log('🔵 NORMAL MESSAGE - CLEARING TEMP MESSAGES')
                // Clear temporary messages when we get a normal response (approved)
                clearTemporaryMessages(selectedSoulId)
                // Clear pending review state if we get a normal response
                setHasPendingReview(false)
            }
            
            // Update the query data with both messages
            queryClient.setQueryData<ChatMessagePublic[]>(
                ["chat-messages", selectedSoulId],
                (old) => {
                    if (!old) return [user_message, ai_message]
                    
                    // Remove the temporary optimistic message and add both real messages
                    const withoutOptimistic = old.filter(msg => !msg.id?.startsWith('temp-'))
                    const newMessages = [...withoutOptimistic, user_message, ai_message]
                    
                    console.log('🔵 UPDATING QUERY DATA:', {
                        oldLength: old.length,
                        newLength: newMessages.length,
                        hasTemporary: newMessages.some(m => m.is_temporary)
                    })
                    
                    return newMessages
                }
            )
        },
    })

    useEffect(() => {
        if (search.soul) {
            setSelectedSoulId(search.soul)
        }
    }, [search.soul])

    // Check for stored temporary messages when soul ID changes
    useEffect(() => {
        if (selectedSoulId) {
            const storedTempMessages = getStoredTemporaryMessages(selectedSoulId)
            if (storedTempMessages.length > 0) {
                setHasPendingReview(true)
            }
        }
    }, [selectedSoulId])

    useEffect(() => {
        // Scroll to bottom of messages
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
        
        // Check if there are any temporary messages (indicating pending review)
        if (messages) {
            const hasTemporaryMessage = messages.some(msg => msg.is_temporary)
            setHasPendingReview(hasTemporaryMessage)
            
            // Clean up temporary messages if we have newer real messages from same user
            const temporaryMessages = messages.filter(msg => msg.is_temporary)
            const realMessages = messages.filter(msg => !msg.is_temporary)
            
            if (temporaryMessages.length > 0 && realMessages.length > 0) {
                // Check if the latest real message is newer than temporary messages
                const latestReal = realMessages[realMessages.length - 1]
                const latestTemp = temporaryMessages[temporaryMessages.length - 1]
                
                if (latestReal && latestTemp && new Date(latestReal.timestamp) > new Date(latestTemp.timestamp)) {
                    // Clear temporary messages from localStorage and state
                    clearTemporaryMessages(selectedSoulId)
                    const cleanedMessages = messages.filter(msg => !msg.is_temporary)
                    queryClient.setQueryData(["chat-messages", selectedSoulId], cleanedMessages)
                    setHasPendingReview(false)
                }
            }
        }
    }, [messages])

    const handleSendMessage = async () => {
        if (!message.trim() || !selectedSoulId || sendMessageMutation.isPending) return

        const messageData: ChatCreateChatMessageData = {
            aiSoulId: selectedSoulId,
            requestBody: {
                content: message.trim(),
            },
        }

        setMessage("") // Clear input immediately
        sendMessageMutation.mutate(messageData)
    }

    const handleKeyPress = (event: React.KeyboardEvent) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault()
            handleSendMessage()
        }
    }

    if (!selectedSoulId) {
        return (
            <Container maxW="7xl" py={8}>
                <VStack gap={4} align="stretch">
                    <Text fontSize="lg" fontWeight="bold">
                        Select an AI Soul to start chatting
                    </Text>
                    <Button
                        onClick={() => navigate({ to: "/ai-souls" })}
                        colorScheme="teal"
                    >
                        Select Soul
                    </Button>
                </VStack>
            </Container>
        )
    }

    return (
        <Container maxW="7xl" py={8}>
            <VStack gap={4} align="stretch" h="calc(100vh - 8rem)">
                <Text fontSize="2xl" fontWeight="bold">
                    Chat with {aiSoul?.name || "AI Soul"}
                </Text>

                <Box
                    flex="1"
                    overflowY="auto"
                    bg="white"
                    borderRadius="md"
                    p={4}
                    border="1px"
                    borderColor="gray.200"
                >
                    {messagesLoading ? (
                        <VStack gap={3}>
                            <Box w="60%" h="40px" bg="gray.200" borderRadius="md" opacity={0.7} />
                            <Box w="80%" h="40px" bg="blue.100" borderRadius="md" opacity={0.7} />
                            <Box w="70%" h="40px" bg="gray.200" borderRadius="md" opacity={0.7} />
                        </VStack>
                    ) : messages && messages.length > 0 ? (
                        <VStack gap={3} align="stretch">
                            {messages.map((msg, idx) => {
                                const isTemporary = msg.is_temporary || false
                                
                                // Debug logging for temporary messages only
                                if (isTemporary) {
                                    console.log('🔶 RENDERING TEMPORARY MESSAGE:', {
                                        content: msg.content,
                                        is_temporary: msg.is_temporary,
                                        id: msg.id
                                    })
                                }
                                
                                return (
                                    <Flex
                                        key={msg.id || idx}
                                        justify={msg.is_from_user ? "flex-end" : "flex-start"}
                                        w="100%"
                                    >
                                        <Box
                                            bg={msg.is_from_user ? "teal.500" : isTemporary ? "orange.50" : "gray.100"}
                                            color={msg.is_from_user ? "white" : "black"}
                                            p={3}
                                            borderRadius="lg"
                                            maxW="70%"
                                            borderBottomLeftRadius={msg.is_from_user ? "lg" : "sm"}
                                            borderBottomRightRadius={msg.is_from_user ? "sm" : "lg"}
                                            opacity={isTemporary ? 0.9 : 1}
                                            border={isTemporary ? "1px solid" : "none"}
                                            borderColor={isTemporary ? "orange.200" : "transparent"}
                                            position="relative"
                                        >
                                            <Text>{msg.content}</Text>
                                            {isTemporary && (
                                                <Flex align="center" mt={2} gap={1}>
                                                    <Box
                                                        w={2}
                                                        h={2}
                                                        bg="orange.400"
                                                        borderRadius="full"
                                                        animation="pulse 2s infinite"
                                                    />
                                                    <Text fontSize="xs" color="orange.600" fontStyle="italic">
                                                        Under review by specialist
                                                    </Text>
                                                </Flex>
                                            )}
                                        </Box>
                                    </Flex>
                                )
                            })}
                            {sendMessageMutation.isPending && (
                                <Flex justify="flex-start" w="100%">
                                    <Box
                                        bg="gray.100"
                                        color="black"
                                        p={3}
                                        borderRadius="lg"
                                        maxW="70%"
                                        borderBottomLeftRadius="sm"
                                        opacity={0.7}
                                    >
                                        <Text>💭 {aiSoul?.name || "AI"} is thinking...</Text>
                                    </Box>
                                </Flex>
                            )}
                        </VStack>
                    ) : (
                        <VStack 
                            justify="center" 
                            align="center" 
                            h="100%" 
                            gap={4}
                            color="gray.500"
                        >
                            <Box fontSize="48px">💭</Box>
                            <VStack gap={2} textAlign="center">
                                <Text fontSize="lg" fontWeight="medium" color="gray.600">
                                    Start chatting with {aiSoul?.name || "your AI Soul"}
                                </Text>
                                <Text fontSize="sm" color="gray.500" maxW="300px">
                                    Begin a conversation and discover what your AI soul has learned. 
                                    Ask questions, share thoughts, or just say hello!
                                </Text>
                            </VStack>
                            <Box 
                                p={3} 
                                bg="teal.50" 
                                borderRadius="md" 
                                border="1px solid" 
                                borderColor="teal.200"
                                maxW="400px"
                            >
                                <Text fontSize="xs" color="teal.600" textAlign="center">
                                    💡 <strong>Tip:</strong> Try asking "What can you help me with?" or "Tell me about yourself"
                                </Text>
                            </Box>
                        </VStack>
                    )}
                    <div ref={messagesEndRef} />
                </Box>

                {hasPendingReview && (
                    <Box
                        p={3}
                        bg="orange.50"
                        borderRadius="md"
                        border="1px solid"
                        borderColor="orange.200"
                        mb={2}
                    >
                        <Flex align="center" gap={2}>
                            <Box
                                w={3}
                                h={3}
                                bg="orange.400"
                                borderRadius="full"
                                animation="pulse 2s infinite"
                            />
                            <Text fontSize="sm" color="orange.700" fontWeight="medium">
                                Your message is under review by a specialist
                            </Text>
                        </Flex>
                        <Text fontSize="xs" color="orange.600" mt={1}>
                            Please wait for approval before sending new messages
                        </Text>
                    </Box>
                )}

                <HStack gap={2}>
                    <Input
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder={hasPendingReview ? "Please wait for counselor approval..." : "Type your message..."}
                        disabled={sendMessageMutation.isPending || hasPendingReview}
                        opacity={hasPendingReview ? 0.6 : 1}
                    />
                    <Button
                        onClick={handleSendMessage}
                        loading={sendMessageMutation.isPending}
                        colorScheme="teal"
                        disabled={!message.trim() || hasPendingReview}
                        opacity={hasPendingReview ? 0.6 : 1}
                    >
                        <FiSend />
                    </Button>
                </HStack>
            </VStack>
        </Container>
    )
}

export const Route = createFileRoute("/_layout/chat")({
    component: Chat,
})
