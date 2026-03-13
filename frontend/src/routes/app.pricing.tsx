import { createFileRoute } from "@tanstack/react-router"
import { PricingPage } from "@/components/app/PricingPage"

export const Route = createFileRoute("/app/pricing")({
  component: PricingPage,
})
