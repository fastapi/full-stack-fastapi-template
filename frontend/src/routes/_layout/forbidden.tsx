import { createFileRoute } from "@tanstack/react-router"

import AccessDenied from "@/components/Common/AccessDenied"

export const Route = createFileRoute("/_layout/forbidden")({
  component: AccessDenied,
  head: () => ({
    meta: [
      {
        title: "Access Denied - FastAPI Template",
      },
    ],
  }),
})
