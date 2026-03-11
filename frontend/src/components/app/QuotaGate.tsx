import type { ReactNode } from "react"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { useEntitlement } from "@/hooks/useEntitlement"
import type { TierQuota } from "@/lib/entitlements"

interface QuotaGateProps {
  /** Which quota limit to check */
  resource: keyof TierQuota
  /** Current count of this resource (e.g. number of segments the brand already has) */
  currentCount: number
  /** The button or trigger element to wrap */
  children: ReactNode
  /** Optional custom tooltip message when at quota limit */
  limitMessage?: string
}

/**
 * Wraps a create/add button and disables it when the user has reached their quota.
 * Shows a tooltip explaining why the button is disabled.
 */
export function QuotaGate({
  resource,
  currentCount,
  children,
  limitMessage,
}: QuotaGateProps) {
  const { isWithinQuota, quota } = useEntitlement()
  const atLimit = !isWithinQuota(resource, currentCount)

  const resourceLabel = resource
    .replace(/([A-Z])/g, " $1")
    .toLowerCase()
    .trim()

  const message =
    limitMessage ??
    `You've reached the limit of ${quota[resource]} ${resourceLabel}(s) on your current plan. Upgrade to add more.`

  if (!atLimit) {
    return <>{children}</>
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          {/* Wrap in span so Tooltip works on disabled buttons */}
          <span className="inline-block cursor-not-allowed">
            <span className="pointer-events-none opacity-50">{children}</span>
          </span>
        </TooltipTrigger>
        <TooltipContent
          side="top"
          className="max-w-[220px] text-xs text-center"
        >
          <p>{message}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
