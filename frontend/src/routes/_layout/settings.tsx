import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/settings")({
  beforeLoad: async () => {
    throw redirect({ to: "/profile" })
  },
})
