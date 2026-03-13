import { createFileRoute } from "@tanstack/react-router"
import { BillingPage } from "@/components/app/BillingPage"

export const Route = createFileRoute("/app/billing")({
  component: BillingPage,
})
