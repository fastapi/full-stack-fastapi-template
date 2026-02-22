import { createFileRoute } from "@tanstack/react-router"
import RankingPositionRisk from "@/components/app/insight/RankingPositionRisk"

export const Route = createFileRoute("/app/insight/ranking-risk")({
  component: RankingPositionRisk,
})
