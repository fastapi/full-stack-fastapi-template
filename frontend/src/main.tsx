import "./index.css"
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
import { ClerkProvider } from '@clerk/clerk-react'
import { dark } from '@clerk/themes'

import { ApiError, OpenAPI } from "./client"
import { CustomProvider } from "./components/ui/provider"
import { envConfig } from "./env-check"

// Configuración de OpenAPI usando variables verificadas
OpenAPI.BASE = envConfig.VITE_API_URL

// OpenAPI token ahora viene de Clerk
OpenAPI.TOKEN = async () => {
  // El token vendrá de Clerk cuando esté disponible
  const token = window.Clerk?.session?.getToken()
  return token || ""
}

const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    // Redirect to sign-in cuando hay error de auth
    window.location.href = "/sign-in"
  }
}

const queryClient = new QueryClient({
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
    <ClerkProvider 
      publishableKey={envConfig.VITE_CLERK_PUBLISHABLE_KEY}
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: "#000000",
          colorBackground: "#0D1117",
          colorInputBackground: "#161B22",
          colorInputText: "#F0F6FC",
        },
        elements: {
          rootBox: "bg-gray-900",
          card: "bg-gray-800 border border-gray-700",
          headerTitle: "text-white",
          headerSubtitle: "text-gray-300",
          formButtonPrimary: "bg-black hover:bg-gray-800 text-white",
          footerActionLink: "text-blue-400 hover:text-blue-300",
        }
      }}
    >
      <CustomProvider>
        <QueryClientProvider client={queryClient}>
          <RouterProvider router={router} />
        </QueryClientProvider>
      </CustomProvider>
    </ClerkProvider>
  </StrictMode>,
)
