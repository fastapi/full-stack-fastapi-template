import { Container, Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

import AddDocument from "@/components/Documents/AddDocument";

export const Route = createFileRoute("/_layout/documents")({
  component: Document,
});

function Document() {
  return (
    <Container maxW="full" py={12}>
      <Heading size="lg" mb={6} textAlign={{ base: "center", md: "left" }}>
        Add Document
      </Heading>
      <AddDocument />
    </Container>
  );
}
