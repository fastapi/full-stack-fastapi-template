import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/")({
  beforeLoad: () => {
    // Redirect to default language
    throw redirect({
      to: "/$lang",
      params: { lang: "vi" },
    })
  },
})
