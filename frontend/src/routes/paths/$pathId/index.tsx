import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

// Define route params schema
const paramsSchema = z.object({
  pathId: z.string(),
})

export const Route = createFileRoute("/paths/$pathId/")({
  component: ViewPath,
  beforeLoad: ({ params }) => {
    return paramsSchema.parse(params)
  },
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
