import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import React, { StrictMode, useState } from "react"
import ReactDOM from "react-dom/client"
import { ApiError, OpenAPI } from "./client"
import { ThemeProvider } from "./components/theme-provider"
import { Toaster } from "./components/ui/sonner"
import "./index.css"
import { routeTree } from "./routeTree.gen"

OpenAPI.BASE = import.meta.env.VITE_API_URL
OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    localStorage.removeItem("access_token")
    window.location.href = "/login"
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
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <QueryClientProvider client={queryClient}>
        {/* Small visible demo: dismissible banner and floating feedback button */}
        <div style={{position: 'relative'}}>
          <Banner />
          <Fab />
        </div>
        <RouterProvider router={router} />
        <Toaster richColors closeButton />
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>,
)

function Banner() {
  const [open, setOpen] = useState(true)
  if (!open) return null
  return (
    <div className="card ui-update-banner" style={{maxWidth: 920, margin: '1rem auto'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12}}>
        <div>
          <strong>UI updated</strong>
          <div style={{opacity: 0.85}}>Refreshed typography, subtle background gradients, buttons, and cards.</div>
        </div>
        <div style={{display: 'flex', gap: 8}}>
          <button className="btn" onClick={() => window.location.reload()}>Refresh</button>
          <button className="btn" onClick={() => setOpen(false)}>Dismiss</button>
        </div>
      </div>
    </div>
  )
}

function Fab() {
  return (
    <a className="btn fab" href="mailto:dev@example.com" title="Send feedback">
      Feedback
    </a>
  )
}
