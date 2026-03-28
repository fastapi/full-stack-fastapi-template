import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/admin/")({
  beforeLoad: () => {
    throw redirect({
      to: "/admin/dashboard",
    })
  },
})
