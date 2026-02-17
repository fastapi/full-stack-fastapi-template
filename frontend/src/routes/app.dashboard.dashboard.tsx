import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/app/dashboard/dashboard")({
  beforeLoad: () => {
    throw redirect({ to: "/app/dashboard/overview" })
  },
  component: () => null,
})
