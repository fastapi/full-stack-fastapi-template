import { createFileRoute } from "@tanstack/react-router"
import Insight from "@/components/app/Insight"

export const Route = createFileRoute("/app/insight")({
  component: Insight,
})
