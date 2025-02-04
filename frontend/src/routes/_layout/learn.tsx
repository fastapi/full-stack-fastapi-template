import {
  Container,
  Flex,
  Heading,
  Button,
  Icon,
} from "@chakra-ui/react"
import { createFileRoute, Outlet, Link } from "@tanstack/react-router"
import { FaRegLightbulb } from "react-icons/fa6"
import { z } from "zod"
import { type ReactNode } from "react"

const learnSearchSchema = z.object({})

export const Route = createFileRoute('/_layout/learn')({
  component: Learn,
  validateSearch: (search) => learnSearchSchema.parse(search),
})

function Learn(): ReactNode {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>Learn</Heading>
      <Flex py={8}>
        <Button
          as={Link}
          to="/learn/chat"
          variant="primary"
          gap={1}
        >
          <Icon as={FaRegLightbulb} /> Start Chat
        </Button>
      </Flex>
      <Outlet />
    </Container>
  )
}
