import { useSubscription } from "@/contexts/SubscriptionContext"
import {
  type SubscriptionTier,
  TIER_FEATURES,
  TIER_QUOTAS,
  type TierFeatures,
  type TierQuota,
} from "@/lib/entitlements"

const SUPER_USER_FEATURES = Object.fromEntries(
  Object.keys(TIER_FEATURES.pro).map((k) => [k, true]),
) as unknown as TierFeatures

const SUPER_USER_QUOTA = Object.fromEntries(
  Object.keys(TIER_QUOTAS.pro).map((k) => [k, Number.MAX_SAFE_INTEGER]),
) as unknown as TierQuota

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

  const isSuperUser = subscription?.is_super_user === true

  // Default to free_trial if no subscription loaded yet
  const tier: SubscriptionTier = subscription?.tier ?? "free_trial"
  const status = subscription?.status ?? "active"

  const isExpired = isSuperUser ? false : status === "expired"
  const isReadOnly = isSuperUser ? false : isExpired || status === "cancelled"

  const features = isSuperUser ? SUPER_USER_FEATURES : TIER_FEATURES[tier]
  const quota = isSuperUser ? SUPER_USER_QUOTA : TIER_QUOTAS[tier]

  const canAccess = (feature: keyof TierFeatures): boolean => {
    if (isSuperUser) return true
    if (isReadOnly) return false
    return features[feature]
  }

  const isWithinQuota = (
    resource: keyof TierQuota,
    currentCount: number,
  ): boolean => {
    if (isSuperUser) return true
    if (isReadOnly) return false
    return currentCount < quota[resource]
  }

  return {
    tier,
    isExpired,
    isReadOnly,
    features,
    quota,
    canAccess,
    isWithinQuota,
  }
}
