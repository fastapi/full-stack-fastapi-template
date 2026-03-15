import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/app/billing")({
  beforeLoad: () => {
    // Billing is now inside Settings > My Plan
    throw redirect({ to: "/app/settings" })
  },
})
