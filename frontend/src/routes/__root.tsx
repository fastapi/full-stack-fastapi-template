import { useAuth } from "@clerk/clerk-react"
import type { QueryClient } from "@tanstack/react-query"
import { createRootRouteWithContext, Outlet } from "@tanstack/react-router"
import { useEffect } from "react"
import { Toaster } from "sonner"
import { setGetTokenFn } from "@/clients/auth-helper"

interface RouterContext {
  queryClient: QueryClient
}

function RootComponent() {
  const { getToken } = useAuth()

  useEffect(() => {
    setGetTokenFn(getToken)
  }, [getToken])

  return (
    <>
      <Outlet />
      <Toaster richColors position="top-right" />
    </>
  )
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
})
