import { createFileRoute } from "@tanstack/react-router"

import PaymentSuccess from "@/components/Payments/PaymentSuccess"

export const Route = createFileRoute("/payment-success")({
  component: PaymentSuccess,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      order_id: (search.order_id as string) || undefined,
      payment_id: (search.payment_id as string) || undefined,
    }
  },
})

