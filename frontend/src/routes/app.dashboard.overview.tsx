import { createFileRoute } from "@tanstack/react-router"
import { BrandOverview } from "@/components/app/dashboard/BrandOverview"

export const Route = createFileRoute("/app/dashboard/overview")({
  component: BrandOverview,
})
