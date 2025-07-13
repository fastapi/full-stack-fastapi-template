import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { RouterProvider, createRouter } from "@tanstack/react-router"
import React, { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { routeTree } from "./routeTree.gen"

import { ApiError, OpenAPI } from "./client"
import { CustomProvider } from "./components/ui/provider"

OpenAPI.BASE = (import.meta as any).env.VITE_API_URL
OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

const isTokenExpired = (token: string): boolean => {
  try {
    // Decode JWT token to check expiration
    const payload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Date.now() / 1000
    return payload.exp < currentTime
  } catch {
    return true // If we can't decode, consider it expired
  }
}

const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    const token = localStorage.getItem("access_token")
    
    // Only logout if token is actually expired or missing
    if (!token || isTokenExpired(token)) {
      localStorage.removeItem("access_token")
      window.location.href = "/login"
    } else {
      // Token is valid but we got 401/403 - might be a temporary issue
      // Log the error but don't logout
      console.warn("API returned 401/403 but token appears valid. This might be a temporary issue.", {
        error: error.message,
        status: error.status,
        url: (error as any).request?.url
      })
    }
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // Don't retry on authentication errors
        if (error instanceof ApiError && [401, 403].includes(error.status)) {
          return false
        }
        // Retry up to 3 times for other errors
        return failureCount < 3
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false, // Reduce unnecessary refetches
    },
    mutations: {
      retry: false, // Don't retry mutations
    },
  },
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CustomProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </CustomProvider>
  </StrictMode>,
)
