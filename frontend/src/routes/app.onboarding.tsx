import { loadStripe } from "@stripe/stripe-js"
import { EmbeddedCheckout, EmbeddedCheckoutProvider } from "@stripe/react-stripe-js"
import { createFileRoute, useNavigate, useSearch } from "@tanstack/react-router"
import { useCallback, useEffect } from "react"
import { useAuth } from "@clerk/clerk-react"
import { billingAPI } from "@/clients/billing"

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY ?? "")

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

  useEffect(() => {
    if (!isLoaded) return
    if (plan !== "pro") {
      navigate({ to: "/app/brands" })
    }
  }, [isLoaded, plan, navigate])

  const fetchClientSecret = useCallback(async () => {
    const priceId = import.meta.env.VITE_STRIPE_PRO_PRICE_ID
    if (!priceId) throw new Error("Stripe price ID is not configured.")
    const { client_secret } = await billingAPI.createCheckoutSession(priceId)
    return client_secret
  }, [])

  if (!isLoaded || plan !== "pro") {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
          Start your Pro trial
        </h1>
        <EmbeddedCheckoutProvider
          stripe={stripePromise}
          options={{ fetchClientSecret }}
        >
          <EmbeddedCheckout />
        </EmbeddedCheckoutProvider>
      </div>
    </div>
  )
}
