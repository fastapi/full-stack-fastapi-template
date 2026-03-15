import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/app/users")({
  beforeLoad: () => {
    throw redirect({ to: "/app/settings" })
  },
})
