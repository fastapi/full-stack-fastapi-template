import type { TimeRange } from "@/clients/dashboard"
import { BrandAwarenessScoreGaugeView } from "@/components/app/dashboard/components/BrandAwarenessScoreGaugeView"
import { BrandAwarenessScoreHistoricalView } from "@/components/app/dashboard/components/BrandAwarenessScoreHistoricalView"
import { BrandAwarenessScoreCurrentScore } from "@/components/app/dashboard/components/BrandAwarnessScoreCurrentScore"

interface BrandAwarenessScoreProps {
  brandId?: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

export function BrandAwarenessScore({
  brandId,
  timeRange,
  customStartDate,
  customEndDate,
}: BrandAwarenessScoreProps) {
  return (
    /* Main Brand Awareness Score Section */
    <div className="grid grid-cols-12 md:grid-cols-12 gap-8 border-b pb-6 items-stretch">
      <div className="col-span-6 flex">
        <BrandAwarenessScoreCurrentScore brandId={brandId} />
      </div>
      <div className="col-span-6 flex">
        <BrandAwarenessScoreGaugeView brandId={brandId} />
      </div>

      <div className="col-span-12">
        {/* Brand Score historic view */}
        <BrandAwarenessScoreHistoricalView
          brandId={brandId}
          timeRange={timeRange}
          customStartDate={customStartDate}
          customEndDate={customEndDate}
        />
      </div>
    </div>
  )
}
