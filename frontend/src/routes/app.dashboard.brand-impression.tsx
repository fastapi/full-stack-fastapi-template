import { createFileRoute } from "@tanstack/react-router"
import { BrandImpression } from "@/components/app/dashboard/BrandImpression"

export const Route = createFileRoute("/app/dashboard/brand-impression")({
  component: BrandImpression,
})
