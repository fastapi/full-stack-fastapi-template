import { createFileRoute } from "@tanstack/react-router"
import { TestPDFWorker } from "@/components/TestPDFWorker"

export const Route = createFileRoute("/test-pdf")({
  component: TestPDFWorker,
})
