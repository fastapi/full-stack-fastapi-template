import { useAuth } from "@clerk/clerk-react"
import { createFileRoute, useNavigate, useSearch } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import { billingAPI } from "@/clients/billing"

// Search params type — plan=pro is the only supported value
type OnboardingSearch = {
  plan?: string
}

export const Route = createFileRoute("/app/onboarding")({
  validateSearch: (search: Record<string, unknown>): OnboardingSearch => ({
    plan: typeof search.plan === "string" ? search.plan : undefined,
  }),
  component: OnboardingPage,
})

function OnboardingPage() {
  const { isLoaded } = useAuth()
  const navigate = useNavigate()
  const { plan } = useSearch({ from: "/app/onboarding" })
  const [error, setError] = useState<string | null>(null)
  const triggered = useRef(false)

  useEffect(() => {
    // Only handle plan=pro; anything else → go to brands
    if (!isLoaded) return
    if (plan !== "pro") {
      navigate({ to: "/app/brands" })
      return
    }
    // Guard against double-fire in React StrictMode
    if (triggered.current) return
    triggered.current = true

    const priceId = import.meta.env.VITE_STRIPE_PRO_PRICE_ID
    if (!priceId) {
      setError("Stripe price ID is not configured. Please contact support.")
      return
    }

    billingAPI
      .createCheckoutSession(priceId)
      .then(({ checkout_url }) => {
        window.location.href = checkout_url
      })
      .catch((err: Error) => {
        setError(err.message || "Failed to start checkout. Please try again.")
      })
  }, [isLoaded, plan, navigate])

  if (error) {
    return (
      <div className="h-screen flex flex-col items-center justify-center gap-4 bg-gray-50">
        <p className="text-gray-700 text-center max-w-sm">{error}</p>
        <button
          type="button"
          onClick={() => {
            triggered.current = false
            setError(null)
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Try Again
        </button>
        <a
          href="/app/settings"
          className="text-sm text-blue-600 hover:underline"
        >
          Go to Settings instead
        </a>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col items-center justify-center gap-3 bg-gray-50">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      <p className="text-sm text-gray-500">Setting up your Pro trial…</p>
    </div>
  )
}
