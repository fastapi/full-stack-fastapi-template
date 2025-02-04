import {
  Box,
  Container,
  Flex,
  Textarea,
  Button,
  Icon,
  Text,
  useColorModeValue,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useState, useRef, useEffect } from "react"
import { FiSend } from "react-icons/fi"

interface ChatMessage {
  id: string
  content: string
  isUser: boolean
}

const ChatMessage = ({ message }: { message: ChatMessage }) => {
  const userBg = useColorModeValue("#F5F2EE", "#4A5568")
  const assistantBg = useColorModeValue("white", "gray.800")
  const textColor = useColorModeValue("ui.main", "ui.light")

  return (
    <Flex justify={message.isUser ? "flex-end" : "flex-start"} mb={4}>
      <Box
        maxW="80%"
        bg={message.isUser ? userBg : assistantBg}
        p={4}
        borderRadius="lg"
        color={textColor}
        borderWidth={1}
        borderColor={useColorModeValue("gray.200", "gray.700")}
      >
        <Text>{message.content}</Text>
      </Box>
    </Flex>
  )
}

export const Route = createFileRoute('/learn/chat')({
  component: ChatRoute
})

function ChatRoute() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentMessage, setCurrentMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const borderColor = useColorModeValue("gray.200", "gray.700")
  const textColor = useColorModeValue("ui.main", "ui.light")

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!currentMessage.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: window.crypto.randomUUID(),
      content: currentMessage,
      isUser: true,
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentMessage("")
    setIsLoading(true)

    // Simulate streaming response
    const response = "This is a simulated streaming response..."
    let streamedContent = ""
    
    const newMessage: ChatMessage = {
      id: window.crypto.randomUUID(),
      content: "",
      isUser: false,
    }
    setMessages(prev => [...prev, newMessage])

    for (const char of response) {
      await new Promise(resolve => setTimeout(resolve, 50))
      streamedContent += char
      setMessages(prev => 
        prev.map(msg => 
          msg.id === newMessage.id 
            ? { ...msg, content: streamedContent }
            : msg
        )
      )
    }

    setIsLoading(false)
  }

  return (
    <Flex 
      direction="column" 
      h="calc(100vh - 64px)"
      maxW="3xl" 
      mx="auto"
      borderWidth={1}
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
    >
      <Box flex={1} overflowY="auto" p={4}>
        {messages.map(message => (
          <ChatMessage key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </Box>
      
      <Box p={4} borderTopWidth={1} borderColor={borderColor}>
        <form onSubmit={handleSendMessage}>
          <Flex gap={2}>
            <Textarea
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              placeholder="Type your message..."
              rows={1}
              resize="none"
              disabled={isLoading}
              color={textColor}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage(e)
                }
              }}
            />
            <Button
              type="submit"
              variant="primary"
              isDisabled={!currentMessage.trim() || isLoading}
              isLoading={isLoading}
            >
              <Icon as={FiSend} />
            </Button>
          </Flex>
        </form>
      </Box>
    </Flex>
  )
}
