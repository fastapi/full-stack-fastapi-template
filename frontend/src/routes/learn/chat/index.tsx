import {
  Container,
  Flex,
  Heading,
  Button,
  Icon,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FaLightbulb } from "react-icons/fa"
import { z } from "zod"
import { type ReactNode } from "react"

export const Route = createFileRoute("/learn/chat/")({
  component: LearnChat,
  validateSearch: (search) => z.object({}).parse(search),
})

function LearnChat(): ReactNode {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>Chat</Heading>
      <Flex py={8}>
        {/* Chat interface will go here */}
      </Flex>
    </Container>
  )
}
