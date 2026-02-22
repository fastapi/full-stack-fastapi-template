import { createFileRoute } from "@tanstack/react-router"
import CompetitiveRisk from "@/components/app/insight/CompetitiveRisk"

export const Route = createFileRoute("/app/insight/competitive-risk")({
  component: CompetitiveRisk,
})
