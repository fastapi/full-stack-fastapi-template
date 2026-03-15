import { Lock } from "lucide-react"
import type { ReactNode } from "react"
import { useEntitlement } from "@/hooks/useEntitlement"
import type { TierFeatures } from "@/lib/entitlements"
import { TIER_UPGRADE_MESSAGE } from "@/lib/entitlements"

interface FeatureGateProps {
  feature: keyof TierFeatures
  children: ReactNode
  /**
   * Optional custom message shown in the upgrade overlay.
   * Defaults to the tier-appropriate upgrade message from TIER_UPGRADE_MESSAGE.
   */
  upgradeMessage?: string
}

/**
 * Wraps content that requires a specific feature access.
 * If the user lacks access, renders a locked overlay with an upgrade CTA.
 * Children are kept in the DOM (not unmounted) to preserve layout.
 */
export function FeatureGate({
  feature,
  children,
  upgradeMessage,
}: FeatureGateProps) {
  const { canAccess, tier } = useEntitlement()

  if (canAccess(feature)) {
    return <>{children}</>
  }

  const message = upgradeMessage ?? TIER_UPGRADE_MESSAGE[tier]

  return (
    <div className="relative">
      {/* Blurred content behind the lock */}
      <div className="pointer-events-none select-none blur-sm opacity-40">
        {children}
      </div>

      {/* Lock overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/60 dark:bg-slate-950/60 rounded-lg z-10">
        <div className="flex flex-col items-center gap-2 p-4 text-center">
          <div className="rounded-full bg-slate-100 dark:bg-slate-900 p-2">
            <Lock className="h-5 w-5 text-slate-500" />
          </div>
          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
            {message || "Upgrade to unlock this feature."}
          </p>
          <a
            href="/app/settings"
            className="mt-1 inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-blue-600 text-white hover:bg-blue-700 transition"
          >
            View plans
          </a>
        </div>
      </div>
    </div>
  )
}
