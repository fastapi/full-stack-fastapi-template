import { createFileRoute } from "@tanstack/react-router"

import PaymentFailure from "@/components/Payments/PaymentFailure"

export const Route = createFileRoute("/payment-failure")({
  component: PaymentFailure,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      error: (search.error as string) || undefined,
    }
  },
})

