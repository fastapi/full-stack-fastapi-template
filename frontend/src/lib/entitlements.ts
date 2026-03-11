/**
 * Entitlement configuration — single source of truth for tier limits and feature access.
 * Frontend-only enforcement. Backend enforcement can be added later without schema changes.
 */

export type SubscriptionTier = "free_trial" | "basic" | "pro"
export type SubscriptionStatus = "active" | "expired" | "cancelled"

export interface UserSubscription {
  tier: SubscriptionTier
  status: SubscriptionStatus
  trial_expires_at: string | null
  is_super_user?: boolean
}

// ── Quota limits per tier ──────────────────────────────────────────────────────

export interface TierQuota {
  brands: number
  brandsPerProject: number
  segmentsPerBrand: number
  promptsPerSegment: number
}

export const TIER_QUOTAS: Record<SubscriptionTier, TierQuota> = {
  free_trial: {
    brands: 1,
    brandsPerProject: 1,
    segmentsPerBrand: 1,
    promptsPerSegment: 1,
  },
  basic: {
    brands: 1,
    brandsPerProject: 1,
    segmentsPerBrand: 3,
    promptsPerSegment: 1,
  },
  pro: {
    brands: 3,
    brandsPerProject: 1,
    segmentsPerBrand: 3,
    promptsPerSegment: 3,
  },
} as const

// ── Feature access flags per tier ─────────────────────────────────────────────

export interface TierFeatures {
  brandImpression: boolean
  /** Full competitive analysis (all charts/tables). Tier 1 only sees Visibility Gap pill. */
  competitiveAnalysisFull: boolean
  /** Visibility Gap pill in Competitive Current Status card */
  competitiveVisibilityGap: boolean
  /** Brand Risk Overview insight page */
  insightBrandRisk: boolean
  /** All insight pages (competitive risk, growth risk, ranking risk) */
  insightAll: boolean
}

export const TIER_FEATURES: Record<SubscriptionTier, TierFeatures> = {
  free_trial: {
    brandImpression: true,
    competitiveAnalysisFull: false,
    competitiveVisibilityGap: true,
    insightBrandRisk: false,
    insightAll: false,
  },
  basic: {
    brandImpression: true,
    competitiveAnalysisFull: true,
    competitiveVisibilityGap: true,
    insightBrandRisk: true,
    insightAll: false,
  },
  pro: {
    brandImpression: true,
    competitiveAnalysisFull: true,
    competitiveVisibilityGap: true,
    insightBrandRisk: true,
    insightAll: true,
  },
} as const

// ── Tier display names (for upgrade CTAs) ─────────────────────────────────────

export const TIER_NAMES: Record<SubscriptionTier, string> = {
  free_trial: "Free Trial",
  basic: "Basic",
  pro: "Pro",
}

export const TIER_UPGRADE_MESSAGE: Record<SubscriptionTier, string> = {
  free_trial: "Upgrade to Basic to unlock this feature.",
  basic: "Upgrade to Pro to unlock this feature.",
  pro: "",
}
