import { createFileRoute } from "@tanstack/react-router"

import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import MonthlyUsage from "@/components/UserSettings/MonthlyUsage"
import PaymentMethods from "@/components/UserSettings/PaymentMethods"
import SubscriptionPlan from "@/components/UserSettings/SubscriptionPlan"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [
      {
        title: "Settings - FastAPI Template",
      },
    ],
  }),
})

function UserSettings() {
  const { user: currentUser } = useAuth()

  if (!currentUser) {
    return null
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Account Settings</h1>
      </div>

      <SubscriptionPlan />
      <MonthlyUsage />
      <ChangePassword />
      <PaymentMethods />
      <DeleteAccount />
    </div>
  )
}
