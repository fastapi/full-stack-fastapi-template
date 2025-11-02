import { createFileRoute } from "@tanstack/react-router"

import Checkout from "@/components/Payments/Checkout"

export const Route = createFileRoute("/_layout/checkout")({
  component: Checkout,
})

