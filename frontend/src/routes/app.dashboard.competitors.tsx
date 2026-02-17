import { createFileRoute } from "@tanstack/react-router"
import { CompetitiveAnalysis } from "@/components/app/dashboard/CompetitiveAnalysis"

export const Route = createFileRoute("/app/dashboard/competitors")({
  component: CompetitiveAnalysis,
})
