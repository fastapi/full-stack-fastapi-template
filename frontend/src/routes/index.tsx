import { useAuth } from "@clerk/clerk-react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import LandingPage from "@/components/landing/LandingPage"

export const Route = createFileRoute("/")({
  component: IndexPage,
})

function IndexPage() {
  const { isLoaded, isSignedIn } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      navigate({ to: "/app/brands" })
    }
  }, [isLoaded, isSignedIn, navigate])

  // Show landing page while loading or if not signed in
  if (isLoaded && isSignedIn) {
    return null
  }

  return <LandingPage />
}
