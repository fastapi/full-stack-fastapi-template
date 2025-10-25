import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { UploadForm } from "@/components/Ingestions/UploadForm"

export const Route = createFileRoute("/_layout/ingestions/upload")({
  component: UploadPage,
})

function UploadPage() {
  return (
    <Container maxW="container.md" py={8}>
      <Heading mb={6}>Upload Worksheet</Heading>
      <UploadForm />
    </Container>
  )
}
