import { createFileRoute } from "@tanstack/react-router"
import RiskIntelligence from "@/components/app/insight/RiskIntelligence"

export const Route = createFileRoute("/app/insight/risk-intelligence")({
  component: RiskIntelligence,
})
