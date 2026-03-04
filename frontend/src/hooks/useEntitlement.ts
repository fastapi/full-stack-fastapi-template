import { useSubscription } from "@/contexts/SubscriptionContext"
import {
  TIER_FEATURES,
  TIER_QUOTAS,
  type TierFeatures,
  type TierQuota,
  type SubscriptionTier,
} from "@/lib/entitlements"

interface EntitlementResult {
  tier: SubscriptionTier
  isExpired: boolean
  isReadOnly: boolean
  features: TierFeatures
  quota: TierQuota
  canAccess: (feature: keyof TierFeatures) => boolean
  isWithinQuota: (resource: keyof TierQuota, currentCount: number) => boolean
}

export function useEntitlement(): EntitlementResult {
  const { subscription } = useSubscription()

  // Default to free_trial if no subscription loaded yet
  const tier: SubscriptionTier = subscription?.tier ?? "free_trial"
  const status = subscription?.status ?? "active"

  const isExpired = status === "expired"
  const isReadOnly = isExpired || status === "cancelled"

  const features = TIER_FEATURES[tier]
  const quota = TIER_QUOTAS[tier]

  const canAccess = (feature: keyof TierFeatures): boolean => {
    if (isReadOnly) return false
    return features[feature]
  }

  const isWithinQuota = (resource: keyof TierQuota, currentCount: number): boolean => {
    if (isReadOnly) return false
    return currentCount < quota[resource]
  }

  return { tier, isExpired, isReadOnly, features, quota, canAccess, isWithinQuota }
}
