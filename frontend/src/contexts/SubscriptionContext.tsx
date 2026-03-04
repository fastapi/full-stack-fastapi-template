import { createContext, useContext } from "react"
import type { UserSubscription } from "@/lib/entitlements"

interface SubscriptionContextValue {
  subscription: UserSubscription | null
}

export const SubscriptionContext = createContext<SubscriptionContextValue>({
  subscription: null,
})

export function useSubscription() {
  return useContext(SubscriptionContext)
}
