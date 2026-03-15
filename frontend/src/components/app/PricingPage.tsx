import { useNavigate } from "@tanstack/react-router"
import { Check, Clock, ExternalLink, Loader2, Sparkles } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"
import { billingAPI } from "@/clients/billing"
import { profileAPI } from "@/clients/profile"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useSubscription } from "@/contexts/SubscriptionContext"
import { useEntitlement } from "@/hooks/useEntitlement"
import { TIER_QUOTAS } from "@/lib/entitlements"

const FREE_TRIAL_FEATURES = [
  `${TIER_QUOTAS.free_trial.brands} brand`,
  `${TIER_QUOTAS.free_trial.segmentsPerBrand} segment per brand`,
  `${TIER_QUOTAS.free_trial.promptsPerSegment} prompt per segment`,
  "Brand Impression analytics",
  "Competitive Analysis (visibility gap only)",
]

const PRO_FEATURES = [
  `${TIER_QUOTAS.pro.brands} brand`,
  `${TIER_QUOTAS.pro.segmentsPerBrand} segments per brand`,
  `${TIER_QUOTAS.pro.promptsPerSegment} prompt per segment`,
  "Brand Impression analytics",
  "Full Competitive Analysis",
  "Market Dynamic insights",
  "Risk Intelligence insights",
]

function daysUntil(dateStr: string): number {
  const diff = new Date(dateStr).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

function StatusBadge({ label, variant }: { label: string; variant: "green" | "amber" | "red" | "blue" | "slate" }) {
  const styles = {
    green: "bg-green-100 text-green-700",
    amber: "bg-amber-100 text-amber-700",
    red: "bg-red-100 text-red-700",
    blue: "bg-blue-100 text-blue-700",
    slate: "bg-slate-100 text-slate-600",
  }
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${styles[variant]}`}>
      {label}
    </span>
  )
}

export function PricingPage({ embedded = false }: { embedded?: boolean }) {
  const { subscription, refreshSubscription } = useSubscription()
  const { tier, isExpired, isReadOnly } = useEntitlement()
  const navigate = useNavigate()
  const [checkoutLoading, setCheckoutLoading] = useState(false)
  const [portalLoading, setPortalLoading] = useState(false)
  const [cancelLoading, setCancelLoading] = useState(false)
  const [reactivateLoading, setReactivateLoading] = useState(false)
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false)
  const pollingRef = useRef(false)

  const searchParams = new URLSearchParams(window.location.search)
  const statusParam = searchParams.get("status")

  // Handle return from Stripe Checkout
  useEffect(() => {
    if (statusParam === "cancelled") {
      toast.info("Checkout cancelled")
      navigate({ to: "/app/settings", replace: true })
      return
    }

    if (statusParam !== "success" || pollingRef.current) return
    pollingRef.current = true

    let attempts = 0
    const poll = setInterval(async () => {
      attempts++
      try {
        const profile = await profileAPI.getProfile()
        const sub = (profile as any)?.subscription
        if (sub && sub.tier !== "free_trial" && sub.status === "active") {
          clearInterval(poll)
          await refreshSubscription()
          toast.success("Subscription activated!")
          navigate({ to: "/app/settings", replace: true })
          return
        }
      } catch {
        // ignore
      }
      if (attempts >= 10) {
        clearInterval(poll)
        await refreshSubscription()
        toast.success("Subscription activated! It may take a moment to reflect.")
        navigate({ to: "/app/settings", replace: true })
      }
    }, 1000)

    return () => clearInterval(poll)
  }, [statusParam, refreshSubscription, navigate])

  const handleUpgrade = async () => {
    try {
      setCheckoutLoading(true)
      const priceId = import.meta.env.VITE_STRIPE_PRO_PRICE_ID ?? ""
      const { checkout_url } = await billingAPI.createCheckoutSession(priceId)
      window.location.href = checkout_url
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to start checkout")
    } finally {
      setCheckoutLoading(false)
    }
  }

  const handleCancel = async () => {
    try {
      setCancelLoading(true)
      await billingAPI.cancelSubscription()
      await refreshSubscription()
      toast.success("Subscription will cancel at end of billing period.")
      setCancelDialogOpen(false)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to cancel subscription")
    } finally {
      setCancelLoading(false)
    }
  }

  const handleReactivate = async () => {
    try {
      setReactivateLoading(true)
      await billingAPI.reactivateSubscription()
      await refreshSubscription()
      toast.success("Subscription reactivated!")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to reactivate subscription")
    } finally {
      setReactivateLoading(false)
    }
  }

  const handlePortal = async () => {
    try {
      setPortalLoading(true)
      const { portal_url } = await billingAPI.createPortalSession()
      window.location.href = portal_url
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to open billing portal")
    } finally {
      setPortalLoading(false)
    }
  }

  const isFreeTrial = tier === "free_trial"
  const isPro = tier === "pro"
  const status = subscription?.status ?? "active"
  const cancelAtPeriodEnd = subscription?.cancel_at_period_end ?? false
  const currentPeriodEnd = subscription?.current_period_end ?? null
  const trialExpiresAt = subscription?.trial_expires_at ?? null
  const trialDaysLeft = trialExpiresAt ? daysUntil(trialExpiresAt) : null

  // Pro is "active" from access perspective if cancel_at_period_end is true (still within period)
  const proAccessActive = isPro && status === "active" && !isExpired

  return (
    <div className={embedded ? "space-y-5" : "mx-auto max-w-2xl px-4 py-10 space-y-5"}>

      {/* ── Current plan: Free Trial ── */}
      {isFreeTrial && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-slate-500" />
                Free Trial
              </CardTitle>
              <StatusBadge
                label={isExpired ? "Expired" : "Active"}
                variant={isExpired ? "red" : "green"}
              />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {trialExpiresAt && (
              <div className={`rounded-lg px-4 py-3 text-sm ${
                isExpired
                  ? "bg-red-50 text-red-700"
                  : trialDaysLeft !== null && trialDaysLeft <= 3
                    ? "bg-amber-50 text-amber-700"
                    : "bg-blue-50 text-blue-700"
              }`}>
                {isExpired
                  ? "Your free trial has ended. Upgrade to Pro to continue."
                  : `Trial ends ${formatDate(trialExpiresAt)} — ${trialDaysLeft} day${trialDaysLeft === 1 ? "" : "s"} remaining.`}
              </div>
            )}
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                What's included in your trial
              </p>
              <ul className="space-y-1.5">
                {FREE_TRIAL_FEATURES.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-slate-600">
                    <Check className="h-3.5 w-3.5 text-green-500 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
          <CardFooter>
            <Button className="w-full" onClick={handleUpgrade} disabled={checkoutLoading}>
              {checkoutLoading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Upgrade to Pro — $299/month
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* ── Current plan: Pro ── */}
      {isPro && (
        <Card className={`border-blue-200 ${!proAccessActive ? "opacity-80" : ""}`}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-blue-500" />
                Pro Plan — $299/month
              </CardTitle>
              {cancelAtPeriodEnd ? (
                <StatusBadge label="Cancelling" variant="amber" />
              ) : isExpired ? (
                <StatusBadge label="Expired" variant="red" />
              ) : isReadOnly ? (
                <StatusBadge label="Cancelled" variant="red" />
              ) : status === "past_due" ? (
                <StatusBadge label="Past Due" variant="amber" />
              ) : (
                <StatusBadge label="Active" variant="green" />
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Cancelling notice */}
            {cancelAtPeriodEnd && currentPeriodEnd && (
              <div className="rounded-lg px-4 py-3 text-sm bg-amber-50 text-amber-800 space-y-2">
                <p className="font-medium">Your subscription is set to cancel.</p>
                <p>
                  You have full Pro access until{" "}
                  <span className="font-semibold">{formatDate(currentPeriodEnd)}</span>
                  {" "}({daysUntil(currentPeriodEnd)} day{daysUntil(currentPeriodEnd) === 1 ? "" : "s"} remaining).
                </p>
              </div>
            )}

            {/* Past due notice */}
            {status === "past_due" && (
              <div className="rounded-lg px-4 py-3 text-sm bg-amber-50 text-amber-700">
                Your last payment failed. Update your payment method to avoid losing access.
              </div>
            )}

            {/* Expired / truly cancelled */}
            {(isExpired || (isReadOnly && !cancelAtPeriodEnd)) && (
              <div className="rounded-lg px-4 py-3 text-sm bg-red-50 text-red-700">
                Your Pro subscription is no longer active. Resubscribe to restore full access.
              </div>
            )}

            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                What's included
              </p>
              <ul className="space-y-1.5">
                {PRO_FEATURES.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-slate-600">
                    <Check className="h-3.5 w-3.5 text-green-500 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-2">
            {/* Truly expired/cancelled → resubscribe via Stripe checkout */}
            {(isExpired || (isReadOnly && !cancelAtPeriodEnd)) && (
              <Button className="w-full" onClick={handleUpgrade} disabled={checkoutLoading}>
                {checkoutLoading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                Resubscribe — $299/month
              </Button>
            )}

            {/* Scheduled to cancel → offer reactivation in-app */}
            {cancelAtPeriodEnd && (
              <Button className="w-full" onClick={handleReactivate} disabled={reactivateLoading}>
                {reactivateLoading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                Reactivate Subscription
              </Button>
            )}

            {/* Active and not cancelling → show cancel + payment method options */}
            {proAccessActive && !cancelAtPeriodEnd && (
              <>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handlePortal}
                  disabled={portalLoading}
                >
                  {portalLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <ExternalLink className="h-4 w-4 mr-2" />
                  )}
                  Update Payment Method / View Invoices
                </Button>
                <Button
                  variant="ghost"
                  className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
                  onClick={() => setCancelDialogOpen(true)}
                >
                  Cancel Subscription
                </Button>
              </>
            )}

            {/* Past due → send to portal to fix payment */}
            {status === "past_due" && (
              <Button className="w-full" onClick={handlePortal} disabled={portalLoading}>
                {portalLoading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                Update Payment Method
              </Button>
            )}
          </CardFooter>
        </Card>
      )}

      {/* ── Pro upgrade card (for free trial users) ── */}
      {isFreeTrial && (
        <Card className="border-blue-500 shadow-md">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-blue-500" />
                Upgrade to Pro
              </CardTitle>
              <StatusBadge label="$299/month" variant="blue" />
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1.5">
              {PRO_FEATURES.map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-600">
                  <Check className="h-3.5 w-3.5 text-green-500 shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button className="w-full" onClick={handleUpgrade} disabled={checkoutLoading}>
              {checkoutLoading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Get Started with Pro
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* ── Cancel confirmation dialog ── */}
      <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel your subscription?</DialogTitle>
            <DialogDescription asChild>
              <div className="space-y-2">
                <p>Your subscription won't end immediately.</p>
                {currentPeriodEnd && (
                  <p>
                    You'll keep full Pro access until{" "}
                    <span className="font-semibold text-slate-900">{formatDate(currentPeriodEnd)}</span>.
                    After that, your account moves back to Free Trial limits.
                  </p>
                )}
                <p>You can reactivate any time before that date.</p>
              </div>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelDialogOpen(false)}>
              Keep My Plan
            </Button>
            <Button variant="destructive" onClick={handleCancel} disabled={cancelLoading}>
              {cancelLoading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Yes, Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
