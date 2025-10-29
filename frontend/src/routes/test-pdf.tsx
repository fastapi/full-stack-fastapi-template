import { createFileRoute } from "@tanstack/react-router"
import { TestPDFWorker } from "@/components/TestPDFWorker"

// @ts-expect-error - Temporary test route, route tree will be regenerated
export const Route = createFileRoute("/test-pdf")({
  component: TestPDFWorker,
})
