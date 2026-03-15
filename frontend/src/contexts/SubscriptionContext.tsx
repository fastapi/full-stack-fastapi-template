import { createContext, useContext } from "react"
import type { UserSubscription } from "@/lib/entitlements"

interface SubscriptionContextValue {
  subscription: UserSubscription | null
  refreshSubscription: () => Promise<void>
}

export const SubscriptionContext = createContext<SubscriptionContextValue>({
  subscription: null,
  refreshSubscription: async () => {},
})

export function useSubscription() {
  return useContext(SubscriptionContext)
}
