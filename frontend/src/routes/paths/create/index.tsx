import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import React from "react"
import { z } from "zod"

export const Route = createFileRoute("/paths/create/")({
  component: CreatePath,
  validateSearch: () => ({}),
})

function CreatePath() {
  return (
    <Container maxW="container.xl">
      <Heading as="h1" mb={4}>
        Create New Path
      </Heading>
    </Container>
  )
}
