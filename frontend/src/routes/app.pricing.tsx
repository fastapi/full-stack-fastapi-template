import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/app/pricing")({
  beforeLoad: () => {
    throw redirect({ to: "/app/settings" })
  },
})
