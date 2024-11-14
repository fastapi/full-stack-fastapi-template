// This file is the main entry point for the React application. It sets up
// providers for Chakra UI (for UI components and theming), React Query (for 
// data fetching and caching), and Tanstack Router (for routing). It also 
// configures the OpenAPI client with a base URL and token, and renders 
// the main component tree to the DOM.

import { ChakraProvider } from "@chakra-ui/react"  // Chakra UI for theme and UI components
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"  // React Query for data fetching and caching
import { RouterProvider, createRouter } from "@tanstack/react-router"  // Tanstack Router for routing management
import ReactDOM from "react-dom/client"  // React DOM to render the component tree to the DOM
import { routeTree } from "./routeTree.gen"  // Pre-defined routes generated from route config

import { StrictMode } from "react"  // Enforces best practices in React development
import { OpenAPI } from "./client"  // OpenAPI client for API requests
import theme from "./theme"  // Custom Chakra UI theme

// Set the base URL for the OpenAPI client from environment variables
OpenAPI.BASE = import.meta.env.VITE_API_URL

// Configure the OpenAPI client to use the access token from local storage
OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

// Initialize a new React Query client for caching and managing server state
const queryClient = new QueryClient()

// Create the router using the pre-defined route tree
const router = createRouter({ routeTree })

// Extend Tanstack Router's module to recognize the new router type
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

// Render the application to the root DOM element
// ChakraProvider wraps the app with Chakra UI's theme and styles
// QueryClientProvider supplies the React Query client for data fetching
// RouterProvider supplies routing capabilities to the application
ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </ChakraProvider>
  </StrictMode>,
)
