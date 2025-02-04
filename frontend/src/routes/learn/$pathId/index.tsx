import React, { useState, KeyboardEvent, ChangeEvent } from "react"
import {
  Box,
  Container,
  Flex,
  Input,
  VStack,
  Text,
  IconButton,
  useColorModeValue,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { ArrowUpIcon } from "@chakra-ui/icons"
import { z } from "zod"

interface Message {
  role: "user" | "assistant"
  content: string
}

export const Route = createFileRoute("/learn/$pathId")({
  component: Learn,
  validateParams: (params) => ({
    pathId: z.string().parse(params.pathId),
  }),
})

function Learn() {
  const { pathId } = Route.useParams()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const bgColor = useColorModeValue("white", "gray.800")
  const bubbleBgUser = useColorModeValue("blue.500", "blue.200")
  const bubbleBgAssistant = useColorModeValue("gray.100", "gray.700")
  const bubbleColorUser = useColorModeValue("white", "gray.800")

  const handleSubmit = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      role: "user",
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")

    try {
      const response = await fetch(`/api/v1/learn/${pathId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          model: "anthropic"
        }),
      })

      const data = await response.json()
      const assistantMessage: Message = {
        role: "assistant",
        content: data.message,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Error sending message:", error)
    }
  }

  return (
    <Container maxW="container.md" h="100vh" p={4}>
      <Flex direction="column" h="full">
        {/* Messages Area */}
        <VStack
          flex={1}
          overflowY="auto"
          spacing={4}
          align="stretch"
          mb={4}
          p={4}
          borderRadius="md"
          bg={bgColor}
          boxShadow="sm"
        >
          {messages.map((message, index) => (
            <Flex
              key={index}
              justify={message.role === "user" ? "flex-end" : "flex-start"}
            >
              <Box
                maxW="80%"
                p={3}
                borderRadius="lg"
                bg={message.role === "user" ? bubbleBgUser : bubbleBgAssistant}
                color={message.role === "user" ? bubbleColorUser : "inherit"}
              >
                <Text>{message.content}</Text>
              </Box>
            </Flex>
          ))}
        </VStack>

        {/* Input Area */}
        <Flex>
          <Input
            value={input}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
            placeholder="Type your message..."
            mr={2}
            onKeyPress={(e: KeyboardEvent<HTMLInputElement>) => {
              if (e.key === "Enter") {
                handleSubmit()
              }
            }}
          />
          <IconButton
            aria-label="Send message"
            icon={<ArrowUpIcon />}
            onClick={handleSubmit}
            colorScheme="blue"
          />
        </Flex>
      </Flex>
    </Container>
  )
}
