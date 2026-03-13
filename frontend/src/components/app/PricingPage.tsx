import { useNavigate } from "@tanstack/react-router"
import { Check, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"
import { billingAPI } from "@/clients/billing"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useEntitlement } from "@/hooks/useEntitlement"
import {
  type SubscriptionTier,
  TIER_FEATURES,
  TIER_QUOTAS,
} from "@/lib/entitlements"

const PLANS: {
  tier: SubscriptionTier
  name: string
  price: string
  priceId: string
  description: string
}[] = [
  {
    tier: "basic",
    name: "Basic",
    price: "$29",
    priceId: import.meta.env.VITE_STRIPE_BASIC_PRICE_ID ?? "",
    description: "For individuals getting started with AI brand monitoring",
  },
  {
    tier: "pro",
    name: "Pro",
    price: "$79",
    priceId: import.meta.env.VITE_STRIPE_PRO_PRICE_ID ?? "",
    description: "For teams needing full competitive intelligence",
  },
]

function getFeatureLabels(tier: SubscriptionTier): string[] {
  const features = TIER_FEATURES[tier]
  const quotas = TIER_QUOTAS[tier]
  const labels: string[] = []

  labels.push(`${quotas.brands} brand${quotas.brands > 1 ? "s" : ""}`)
  labels.push(
    `${quotas.segmentsPerBrand} segment${quotas.segmentsPerBrand > 1 ? "s" : ""} per brand`,
  )
  labels.push(
    `${quotas.promptsPerSegment} prompt${quotas.promptsPerSegment > 1 ? "s" : ""} per segment`,
  )

  if (features.brandImpression) labels.push("Brand Impression analytics")
  if (features.competitiveAnalysisFull) labels.push("Full Competitive Analysis")
  if (features.insightBrandRisk) labels.push("Brand Risk insights")
  if (features.insightAll) labels.push("All insight pages")

  return labels
}

export function PricingPage() {
  const { tier: currentTier, isExpired, isReadOnly } = useEntitlement()
  const [loadingPriceId, setLoadingPriceId] = useState<string | null>(null)
  const navigate = useNavigate()

  const searchParams = new URLSearchParams(window.location.search)
  const statusParam = searchParams.get("status")

  useEffect(() => {
    if (statusParam === "cancelled") {
      toast.info("Checkout cancelled")
      navigate({ to: "/app/pricing", replace: true })
    }
  }, [statusParam, navigate])

  const handleUpgrade = async (priceId: string) => {
    try {
      setLoadingPriceId(priceId)
      const { checkout_url } = await billingAPI.createCheckoutSession(priceId)
      window.location.href = checkout_url
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to start checkout",
      )
    } finally {
      setLoadingPriceId(null)
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Choose Your Plan</h1>
        <p className="mt-2 text-sm text-slate-500">
          Unlock powerful AI brand monitoring and competitive intelligence
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {PLANS.map((plan) => {
          const isCurrent =
            currentTier === plan.tier && !isExpired && !isReadOnly
          const isLoading = loadingPriceId === plan.priceId

          return (
            <Card
              key={plan.tier}
              className={`relative ${plan.tier === "pro" ? "border-blue-500 shadow-lg" : ""}`}
            >
              {plan.tier === "pro" && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-medium px-3 py-1 rounded-full">
                  Most Popular
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-lg">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="mt-2">
                  <span className="text-3xl font-bold text-slate-900">
                    {plan.price}
                  </span>
                  <span className="text-sm text-slate-500">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {getFeatureLabels(plan.tier).map((label) => (
                    <li key={label} className="flex items-start gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                      <span className="text-slate-700">{label}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  variant={plan.tier === "pro" ? "default" : "outline"}
                  disabled={isCurrent || isLoading}
                  onClick={() => handleUpgrade(plan.priceId)}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : null}
                  {isCurrent
                    ? "Current Plan"
                    : isExpired || isReadOnly
                      ? "Subscribe"
                      : `Upgrade to ${plan.name}`}
                </Button>
              </CardFooter>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
