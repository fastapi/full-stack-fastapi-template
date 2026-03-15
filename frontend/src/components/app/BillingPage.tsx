import { useNavigate } from "@tanstack/react-router"
import { CreditCard, ExternalLink, Loader2 } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"
import { billingAPI } from "@/clients/billing"
import { profileAPI } from "@/clients/profile"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useSubscription } from "@/contexts/SubscriptionContext"
import { useEntitlement } from "@/hooks/useEntitlement"
import { TIER_NAMES } from "@/lib/entitlements"

export function BillingPage() {
  const { subscription, refreshSubscription } = useSubscription()
  const { tier, isExpired, isReadOnly } = useEntitlement()
  const navigate = useNavigate()
  const [portalLoading, setPortalLoading] = useState(false)
  const pollingRef = useRef(false)

  const searchParams = new URLSearchParams(window.location.search)
  const statusParam = searchParams.get("status")

  useEffect(() => {
    if (statusParam !== "success" || pollingRef.current) return
    pollingRef.current = true

    let attempts = 0
    const maxAttempts = 10
    const poll = setInterval(async () => {
      attempts++
      try {
        const profile = await profileAPI.getProfile()
        const sub = (profile as any)?.subscription
        if (sub && sub.tier !== "free_trial" && sub.status === "active") {
          clearInterval(poll)
          await refreshSubscription()
          toast.success("Subscription activated!")
          navigate({ to: "/app/billing", replace: true })
          return
        }
      } catch {
        // ignore fetch errors during polling
      }
      if (attempts >= maxAttempts) {
        clearInterval(poll)
        await refreshSubscription()
        toast.success("Subscription activated! It may take a moment to reflect.")
        navigate({ to: "/app/billing", replace: true })
      }
    }, 1000)

    return () => clearInterval(poll)
  }, [statusParam, refreshSubscription, navigate])

  const handleManageSubscription = async () => {
    try {
      setPortalLoading(true)
      const { portal_url } = await billingAPI.createPortalSession()
      window.location.href = portal_url
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to open billing portal",
      )
    } finally {
      setPortalLoading(false)
    }
  }

  // Show "Manage Subscription" only for paid, non-cancelled users.
  // stripe_customer_id is not exposed to the frontend; tier + status is used as proxy.
  const hasStripeCustomer =
    tier !== "free_trial" && subscription?.status !== "cancelled"

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Billing</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Subscription
          </CardTitle>
          <CardDescription>Manage your subscription and billing</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-slate-100">
            <span className="text-sm text-slate-500">Current Plan</span>
            <span className="text-sm font-medium text-slate-900">
              {TIER_NAMES[tier]}
            </span>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-slate-100">
            <span className="text-sm text-slate-500">Status</span>
            <span
              className={`text-sm font-medium ${
                isExpired || isReadOnly
                  ? "text-red-600"
                  : subscription?.status === "past_due"
                    ? "text-amber-600"
                    : "text-green-600"
              }`}
            >
              {subscription?.status === "past_due"
                ? "Past Due"
                : isExpired
                  ? "Expired"
                  : isReadOnly
                    ? "Cancelled"
                    : "Active"}
            </span>
          </div>

          {subscription?.trial_expires_at && tier === "free_trial" && (
            <div className="flex items-center justify-between py-2 border-b border-slate-100">
              <span className="text-sm text-slate-500">Trial Expires</span>
              <span className="text-sm font-medium text-slate-900">
                {new Date(subscription.trial_expires_at).toLocaleDateString()}
              </span>
            </div>
          )}

          <div className="flex flex-col gap-2 pt-2">
            {hasStripeCustomer && (
              <Button
                variant="outline"
                onClick={handleManageSubscription}
                disabled={portalLoading}
              >
                {portalLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <ExternalLink className="h-4 w-4 mr-2" />
                )}
                Manage Subscription
              </Button>
            )}

            <Button
              variant="ghost"
              onClick={() => navigate({ to: "/app/settings" })}
            >
              {isExpired || isReadOnly ? "Subscribe" : "Change Plan"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
