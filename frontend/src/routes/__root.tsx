// This file defines the main route configuration for the application using 
// TanStack's router, including the devtools integration for development and a 
// "Not Found" component for undefined routes.

import { Outlet, createRootRoute } from "@tanstack/react-router"
import React, { Suspense } from "react"

import NotFound from "../components/Common/NotFound"

// Lazy-load the devtools for development mode only, optimizing the production build
const loadDevtools = () =>
  Promise.all([
    import("@tanstack/router-devtools"),           // Router devtools for inspecting routes
    import("@tanstack/react-query-devtools"),      // React Query devtools for inspecting queries
  ]).then(([routerDevtools, reactQueryDevtools]) => {
    return {
      default: () => (
        <>
          <routerDevtools.TanStackRouterDevtools />   // Render Router devtools component
          <reactQueryDevtools.ReactQueryDevtools />   // Render React Query devtools component
        </>
      ),
    }
  })

// Define a lazy-loaded component for TanStackDevtools, which renders only in development mode
const TanStackDevtools =
  process.env.NODE_ENV === "production" ? () => null : React.lazy(loadDevtools)

// Create the root route with the main layout and devtools
export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />             {/* Render child routes inside this main route */}
      <Suspense>
        <TanStackDevtools /> {/* Suspense wrapper for lazy-loaded devtools */}
      </Suspense>
    </>
  ),
  notFoundComponent: () => <NotFound />, // Render NotFound component for unmatched routes
})