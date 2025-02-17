import { Outlet, createRootRouteWithContext } from "@tanstack/react-router"
import React, { Suspense } from "react"

import type { QueryClient } from "@tanstack/react-query"
import NotFound from "../components/Common/NotFound"

const loadDevtools = () =>
  Promise.all([
    import("@tanstack/router-devtools"),
    import("@tanstack/react-query-devtools"),
  ]).then(([routerDevtools, reactQueryDevtools]) => {
    return {
      default: () => (
        <>
          <routerDevtools.TanStackRouterDevtools />
          <reactQueryDevtools.ReactQueryDevtools />
        </>
      ),
    }
  })

const TanStackDevtools =
  process.env.NODE_ENV === "production" ? () => null : React.lazy(loadDevtools)

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()(
  {
    component: () => (
      <>
        <Outlet />
        <Suspense>
          <TanStackDevtools />
        </Suspense>
      </>
    ),
    notFoundComponent: () => <NotFound />,
  },
)
