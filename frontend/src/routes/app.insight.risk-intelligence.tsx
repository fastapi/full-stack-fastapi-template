import { createFileRoute, redirect } from "@tanstack/react-router"

// Risk Intelligence is temporarily hidden — redirect direct URL access to market dynamic
// The component and backend endpoints are preserved for future re-enabling
export const Route = createFileRoute("/app/insight/risk-intelligence")({
  beforeLoad: () => {
    throw redirect({ to: "/app/insight/market-dynamic" })
  },
})
