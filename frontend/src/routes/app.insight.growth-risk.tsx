import { createFileRoute } from "@tanstack/react-router"
import GrowthRisk from "@/components/app/insight/GrowthRisk"

export const Route = createFileRoute("/app/insight/growth-risk")({
  component: GrowthRisk,
})
