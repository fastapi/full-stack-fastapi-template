import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { useSubscription } from "@/contexts/SubscriptionContext"
import ActionableInsights from "@/components/app/insight/ActionableInsights"

export const Route = createFileRoute("/app/insight/risk-intelligence")({
  component: RiskSignalsPage,
})

function RiskSignalsPage() {
  const navigate = useNavigate()
  const { subscription } = useSubscription()
  const isSuperUser = subscription?.is_super_user === true

  useEffect(() => {
    if (subscription !== undefined && !isSuperUser) {
      navigate({ to: "/app/dashboard/overview" })
    }
  }, [isSuperUser, subscription, navigate])

  if (!isSuperUser) return null

  return <ActionableInsights />
}
