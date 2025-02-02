import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"
import React from "react"

// Define route params schema
const paramsSchema = z.object({
  pathId: z.string(),
})

export const Route = createFileRoute("/paths/$pathId/")({
  component: ViewPath,
  validateParams: (params) => paramsSchema.parse(params),
})

function ViewPath() {
  const { pathId } = Route.useParams()

  return (
    <Container maxW="container.xl">
      <Heading as="h1" mb={4}>
        View Path {pathId}
      </Heading>
    </Container>
  )
}
