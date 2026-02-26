import { Loader2, TrendingDown, TrendingUp, Minus, Globe, MessageSquare, LayoutList } from "lucide-react"
import React, { useEffect, useState } from "react"
import {
  type BrandImpressionMetric,
  type BrandImpressionSummaryResponse,
  type BrandOverviewResponse,
  type TimeRange,
  type UserBrand,
  dashboardAPI,
} from "@/clients/dashboard"
import { DashboardPageLayout } from "@/components/app/dashboard/components/DashboardPageLayout"
import { OverviewChart } from "@/components/app/dashboard/components/OverviewChart"
import { SegmentMetricsTable } from "@/components/app/dashboard/components/SegmentMetricsTable"
import { AIReferenceSourceTable } from "@/components/app/dashboard/components/AIReferenceSourceTable"
import { CustomerReviewTable } from "@/components/app/dashboard/components/CustomerReviewTable"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

// ── Impression summary metric box ─────────────────────────────────────────────

interface ImpressionMetricBoxProps {
  label: string
  metric: BrandImpressionMetric
  formatValue: (v: number) => string
  /** True if a higher numeric value is "good" (for colour coding) */
  higherIsBetter?: boolean
}

function ImpressionMetricBox({
  label,
  metric,
  formatValue,
  higherIsBetter = true,
}: ImpressionMetricBoxProps) {
  const { current_value, change, trend } = metric

  const trendIcon =
    trend === "up" ? (
      <TrendingUp className="h-2.5 w-2.5" />
    ) : trend === "down" ? (
      <TrendingDown className="h-2.5 w-2.5" />
    ) : trend === "flat" ? (
      <Minus className="h-2.5 w-2.5" />
    ) : null

  const isGood =
    trend === "up" ? higherIsBetter : trend === "down" ? !higherIsBetter : null

  const trendColour =
    isGood === true
      ? "text-emerald-600"
      : isGood === false
        ? "text-red-500"
        : "text-slate-400"

  const valueStr =
    current_value !== null && current_value !== undefined
      ? formatValue(current_value)
      : "—"

  const changeStr =
    trend !== "no_data" && change !== null && change !== undefined
      ? `${change > 0 ? "+" : ""}${formatValue(Math.abs(change))}`
      : null

  return (
    <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-slate-200 bg-slate-50 text-xs whitespace-nowrap">
      <span className="text-black">{label}</span>
      <span className="font-semibold text-slate-700">{valueStr}</span>
      {changeStr && (
        <span className={`flex items-center gap-0.5 font-medium ${trendColour}`}>
          {trendIcon}
          {changeStr}
        </span>
      )}
    </div>
  )
}

// ── Summary boxes fetched per brand ───────────────────────────────────────────

function BrandImpressionSummaryBoxes({
  brandId,
}: {
  brandId: string
}) {
  const [summary, setSummary] =
    useState<BrandImpressionSummaryResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsLoading(true)
    setSummary(null)
    dashboardAPI
      .getBrandImpressionSummary(brandId)
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setIsLoading(false))
  }, [brandId])

  if (isLoading) {
    return (
      <div className="flex items-center gap-1 text-slate-400 text-xs">
        <Loader2 className="h-3 w-3 animate-spin" />
        <span>Loading…</span>
      </div>
    )
  }

  if (!summary) return null

  return (
    <>
      <ImpressionMetricBox
        label="Visibility"
        metric={summary.visibility}
        formatValue={(v) => `${v.toFixed(1)}%`}
        higherIsBetter={true}
      />
      <ImpressionMetricBox
        label="Position"
        metric={summary.position}
        formatValue={(v) => `#${Math.round(v)}`}
        higherIsBetter={false}
      />
      <ImpressionMetricBox
        label="Sentiment"
        metric={summary.sentiment}
        formatValue={(v) => `${v.toFixed(1)}`}
        higherIsBetter={true}
      />
    </>
  )
}

// ── Main page content ──────────────────────────────────────────────────────────

interface BrandImpressionContentProps {
  brandId: string
  brandName: string
  segment: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
  timeRangeControls: React.ReactNode
  customDateInputs: React.ReactNode
}

function BrandImpressionContent({
  brandId,
  brandName,
  segment,
  timeRange,
  customStartDate,
  customEndDate,
  timeRangeControls,
  customDateInputs,
}: BrandImpressionContentProps) {
  const [overviewData, setOverviewData] =
    useState<BrandOverviewResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await dashboardAPI.getBrandOverview({
          brandId,
          timeRange,
          startDate: customStartDate,
          endDate: customEndDate,
          segment: segment || "All-Segment",
        })
        setOverviewData(data)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load brand impression data",
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [brandId, segment, timeRange, customStartDate, customEndDate])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
        <span className="ml-3 text-slate-500">Loading brand impression...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-16 text-red-500">
        <p>{error}</p>
      </div>
    )
  }

  if (!overviewData) {
    return (
      <div className="text-center py-16 text-slate-500">
        <p>No data available</p>
      </div>
    )
  }

  const { data_points } = overviewData

  return (
    <Card className="rounded-xl border-t-4 border-t-slate-300 ring-1 ring-slate-900/5">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-base font-semibold text-slate-900 bg-indigo-50 px-3 py-1 rounded-full">Impression History</span>
              <span className="text-xs font-normal text-slate-500">— {brandName}</span>
            </div>
          </CardTitle>
          {timeRangeControls}
        </div>
        {customDateInputs && (
          <div className="mt-2">{customDateInputs}</div>
        )}
        <div className="h-px w-full bg-slate-300" />
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Continuous vertical divider spanning all rows */}
          <div className="absolute top-0 bottom-0 left-1/2 w-px bg-slate-300" />

          {/* Row 1 — Chart + Segment Breakdown */}
          <div className="flex py-4">
            <div className="w-1/2 min-w-0 pr-4 flex flex-col">
              <div className="flex items-center gap-1.5 mb-3">
                <TrendingUp className="h-3.5 w-3.5 text-indigo-500" />
                <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full">Historical Trend</span>
              </div>
              <OverviewChart dataPoints={data_points} />
            </div>
            <div className="w-1/2 min-w-0 pl-4 overflow-hidden">
              <div className="flex items-center gap-1.5 mb-3">
                <LayoutList className="h-3.5 w-3.5 text-indigo-500" />
                <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full">Ranking Details</span>
              </div>
              <SegmentMetricsTable
                brandId={brandId}
                timeRange={timeRange}
                customStartDate={customStartDate}
                customEndDate={customEndDate}
              />
            </div>
          </div>

          {/* Horizontal row divider */}
          <div className="h-px w-full bg-slate-300" />

          {/* Row 2 — AI Reference Source + Customer Reviews */}
          <div className="flex py-4">
            <div className="w-1/2 min-w-0 pr-4 overflow-hidden">
              <div className="flex items-center gap-1.5 mb-3">
                <Globe className="h-3.5 w-3.5 text-indigo-500" />
                <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full">AI Reference Source</span>
              </div>
              <AIReferenceSourceTable
                brandId={brandId}
                segment={segment}
                timeRange={timeRange}
                customStartDate={customStartDate}
                customEndDate={customEndDate}
              />
            </div>
            <div className="w-1/2 min-w-0 pl-4 overflow-hidden">
              <div className="flex items-center gap-1.5 mb-3">
                <MessageSquare className="h-3.5 w-3.5 text-violet-500" />
                <span className="text-xs font-semibold text-violet-700 bg-violet-50 px-2 py-0.5 rounded-full">Sentiment - Customer Review</span>
              </div>
              <CustomerReviewTable
                brandId={brandId}
                segment={segment}
                timeRange={timeRange}
                customStartDate={customStartDate}
                customEndDate={customEndDate}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ── Exported page component ────────────────────────────────────────────────────

export function BrandImpression() {
  return (
    <DashboardPageLayout
      title="Brand Impression"
      description="Monitor Your Brand's AI Search Impression"
      brandCardTitle="Current Impression"
      brandCardDescription=""
      showProjectRole={false}
      brandCardExtras={(selectedBrand: UserBrand | undefined) =>
        selectedBrand ? (
          <BrandImpressionSummaryBoxes brandId={selectedBrand.brand_id} />
        ) : null
      }
    >
      {({ selectedBrandId, selectedBrand, selectedSegment, timeRange, customStartDate, customEndDate, timeRangeControls, customDateInputs }) => (
        <BrandImpressionContent
          brandId={selectedBrandId}
          brandName={selectedBrand.brand_name}
          segment={selectedSegment}
          timeRange={timeRange}
          customStartDate={customStartDate}
          customEndDate={customEndDate}
          timeRangeControls={timeRangeControls}
          customDateInputs={customDateInputs}
        />
      )}
    </DashboardPageLayout>
  )
}
