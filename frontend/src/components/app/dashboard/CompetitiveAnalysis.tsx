import {
  HelpCircle,
  Link2,
  Loader2,
  MessageCircle,
  Minus,
  TrendingDown,
  TrendingUp,
} from "lucide-react"
import type React from "react"
import { useEffect, useState } from "react"
import {
  type CompetitorGapMetric,
  type CompetitorGapSummaryResponse,
  type CompetitorGapTrendDataPoint,
  type CompetitorRankingDetailDataPoint,
  dashboardAPI,
  type TimeRange,
  type UserBrand,
} from "@/clients/dashboard"
import { CompetitorGapTrendChart } from "@/components/app/dashboard/components/CompetitorGapTrendChart"
import { CompetitorRankingDetailChart } from "@/components/app/dashboard/components/CompetitorRankingDetailChart"
import { DashboardPageLayout } from "@/components/app/dashboard/components/DashboardPageLayout"
import { ReferenceSourceComparisonTable } from "@/components/app/dashboard/components/ReferenceSourceComparisonTable"
import { SentimentComparisonTable } from "@/components/app/dashboard/components/SentimentComparisonTable"
import { FeatureGate } from "@/components/app/FeatureGate"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { useEntitlement } from "@/hooks/useEntitlement"

/** Sentinel from DashboardPageLayout meaning "All Segment" */
const ALL_SEGMENTS_VALUE = "__all_segments__"

function segmentForApi(segment: string): string {
  return segment === ALL_SEGMENTS_VALUE
    ? "all-segment"
    : segment || "all-segment"
}

// ── Gap metric pill ────────────────────────────────────────────────────────────

interface GapMetricPillProps {
  label: string
  metric: CompetitorGapMetric
  formatValue: (v: number) => string
  higherIsBetter?: boolean
  helpText: string
}

function GapMetricPill({
  label,
  metric,
  formatValue,
  higherIsBetter = true,
  helpText,
}: GapMetricPillProps) {
  const { gap_value, change, trend } = metric

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
    gap_value !== null && gap_value !== undefined
      ? (gap_value > 0 ? "+" : "") + formatValue(gap_value)
      : "—"

  const changeStr =
    trend !== "no_data" && change !== null && change !== undefined
      ? `${change > 0 ? "+" : ""}${formatValue(Math.abs(change))}`
      : null

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="relative flex items-center gap-1.5 px-2 py-1 rounded border border-slate-200 bg-slate-50 text-xs whitespace-nowrap cursor-default">
            <span className="text-black">{label}</span>
            <span className="font-semibold text-slate-700">{valueStr}</span>
            {changeStr && (
              <span
                className={`flex items-center gap-0.5 font-medium ${trendColour}`}
              >
                {trendIcon}
                {changeStr}
              </span>
            )}
            <HelpCircle className="h-3 w-3 text-slate-400 flex-shrink-0" />
          </div>
        </TooltipTrigger>
        <TooltipContent
          side="bottom"
          className="max-w-[220px] text-xs text-center"
        >
          <p>{helpText}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

// ── Gap summary pills ──────────────────────────────────────────────────────────

function CompetitorGapSummaryPills({
  brandId,
  segment,
  competitorBrandName,
}: {
  brandId: string
  segment: string
  competitorBrandName: string
}) {
  const [summary, setSummary] = useState<CompetitorGapSummaryResponse | null>(
    null,
  )
  const [isLoading, setIsLoading] = useState(true)
  const { canAccess } = useEntitlement()

  useEffect(() => {
    setIsLoading(true)
    setSummary(null)
    dashboardAPI
      .getCompetitorGapSummary(
        brandId,
        segmentForApi(segment),
        competitorBrandName,
      )
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setIsLoading(false))
  }, [brandId, segment, competitorBrandName])

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
      {/* Visibility Gap — available to all tiers */}
      <GapMetricPill
        label="Visibility Gap"
        metric={summary.visibility_gap}
        formatValue={(v) => `${v.toFixed(1)}%`}
        higherIsBetter={true}
        helpText="My visibility rate minus competitor's. Positive = I appear more often in AI search."
      />
      {/* Position Gap and Sentiment Gap — Tier 2+ only */}
      {canAccess("competitiveAnalysisFull") && (
        <>
          <GapMetricPill
            label="Position Gap"
            metric={summary.position_gap}
            formatValue={(v) => `${Math.round(Math.abs(v))}`}
            higherIsBetter={true}
            helpText="Competitor's median rank minus my median rank. Positive = I rank higher (lower number is better)."
          />
          <GapMetricPill
            label="Sentiment Gap"
            metric={summary.sentiment_gap}
            formatValue={(v) => `${v.toFixed(1)}`}
            higherIsBetter={true}
            helpText="My sentiment score minus competitor's (0–100). Positive = my brand is perceived more positively."
          />
        </>
      )}
    </>
  )
}

// ── Competitor dropdown + gap pills (rendered inside the brand card) ───────────

interface CompetitorSelectorProps {
  brandId: string
  segment: string
  selectedCompetitor: string | null
  onCompetitorChange: (name: string | null) => void
}

function CompetitorSelector({
  brandId,
  segment,
  selectedCompetitor,
  onCompetitorChange,
}: CompetitorSelectorProps) {
  const [competitors, setCompetitors] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!brandId) {
      setCompetitors([])
      onCompetitorChange(null)
      return
    }

    setIsLoading(true)
    setCompetitors([])
    dashboardAPI
      .getCompetitorsBySegment(brandId, segmentForApi(segment))
      .then((data) => {
        setCompetitors(data.competitor_names)
        onCompetitorChange(
          data.competitor_names.length > 0 ? data.competitor_names[0] : null,
        )
      })
      .catch(() => {
        setCompetitors([])
        onCompetitorChange(null)
      })
      .finally(() => setIsLoading(false))
  }, [brandId, segment, onCompetitorChange])

  return (
    <>
      <div className="flex items-center gap-1.5">
        <span className="text-[10px] text-slate-500 font-medium whitespace-nowrap">
          Competitor
        </span>
        {isLoading ? (
          <div className="flex items-center gap-1 text-slate-400">
            <Loader2 className="h-3 w-3 animate-spin" />
          </div>
        ) : competitors.length > 0 ? (
          <Select
            value={selectedCompetitor || undefined}
            onValueChange={onCompetitorChange}
          >
            <SelectTrigger className="w-[140px] !h-6 !py-0 px-2 text-[10px] [&_svg:last-child]:size-3">
              <SelectValue placeholder="Select competitor" />
            </SelectTrigger>
            <SelectContent className="max-h-40">
              {competitors.map((name) => (
                <SelectItem
                  key={name}
                  value={name}
                  className="text-[10px] !py-0.5 px-2"
                >
                  {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : (
          <span className="text-[10px] text-slate-400">No competitors</span>
        )}
      </div>

      {selectedCompetitor && (
        <CompetitorGapSummaryPills
          brandId={brandId}
          segment={segment}
          competitorBrandName={selectedCompetitor}
        />
      )}
    </>
  )
}

// ── Page content ───────────────────────────────────────────────────────────────

interface CompetitiveAnalysisContentProps {
  brandId: string
  brandName: string
  segment: string
  selectedCompetitor: string | null
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
  timeRangeControls: React.ReactNode
  customDateInputs: React.ReactNode
}

function CompetitiveAnalysisContent({
  brandId,
  brandName,
  segment,
  selectedCompetitor,
  timeRange,
  customStartDate,
  customEndDate,
  timeRangeControls,
  customDateInputs,
}: CompetitiveAnalysisContentProps) {
  const dbSegment = segmentForApi(segment)

  // ── Gap trend data (col 1, row 1) ─────────────────────────────────────────
  const [gapTrendData, setGapTrendData] = useState<
    CompetitorGapTrendDataPoint[]
  >([])
  const [isLoadingGapTrend, setIsLoadingGapTrend] = useState(false)
  const [gapTrendError, setGapTrendError] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedCompetitor) {
      setGapTrendData([])
      return
    }
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) return

    setIsLoadingGapTrend(true)
    setGapTrendError(null)
    dashboardAPI
      .getCompetitorGapTrend(
        brandId,
        dbSegment,
        selectedCompetitor,
        timeRange,
        customStartDate,
        customEndDate,
      )
      .then((data) => setGapTrendData(data.data_points))
      .catch((err) =>
        setGapTrendError(
          err instanceof Error ? err.message : "Failed to load gap trend",
        ),
      )
      .finally(() => setIsLoadingGapTrend(false))
  }, [
    brandId,
    dbSegment,
    selectedCompetitor,
    timeRange,
    customStartDate,
    customEndDate,
  ])

  // ── Ranking detail data (col 2, row 1) ────────────────────────────────────
  const [rankingData, setRankingData] = useState<
    CompetitorRankingDetailDataPoint[]
  >([])
  const [isLoadingRanking, setIsLoadingRanking] = useState(false)
  const [rankingError, setRankingError] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedCompetitor) {
      setRankingData([])
      return
    }
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) return

    setIsLoadingRanking(true)
    setRankingError(null)
    dashboardAPI
      .getCompetitorRankingDetail(
        brandId,
        dbSegment,
        selectedCompetitor,
        timeRange,
        customStartDate,
        customEndDate,
      )
      .then((data) => setRankingData(data.data_points))
      .catch((err) =>
        setRankingError(
          err instanceof Error ? err.message : "Failed to load ranking data",
        ),
      )
      .finally(() => setIsLoadingRanking(false))
  }, [
    brandId,
    dbSegment,
    selectedCompetitor,
    timeRange,
    customStartDate,
    customEndDate,
  ])

  if (!selectedCompetitor) {
    return (
      <div className="text-center py-16 text-slate-400 text-sm">
        Select a competitor above to view analysis
      </div>
    )
  }

  return (
    <Card className="rounded-xl ring-1 ring-slate-900/5">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-base font-semibold text-slate-900 bg-indigo-50 px-3 py-1 rounded-full">
                Competitive Dive Deep
              </span>
              <span className="text-xs font-normal text-slate-500">
                — {brandName} vs {selectedCompetitor}
              </span>
            </div>
          </CardTitle>
          {timeRangeControls}
        </div>
        {customDateInputs && <div className="mt-2">{customDateInputs}</div>}
        <div className="h-px w-full bg-slate-200/60" />
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Continuous vertical divider */}
          <div className="absolute top-0 bottom-0 left-1/2 w-px bg-slate-200/60" />

          {/* Row 1 — Gap Trend | Awareness Chart */}
          <div className="flex pt-4 pb-4">
            {/* Col 1: Competitive Gap Historical Trend */}
            <div className="w-1/2 min-w-0 pr-4 flex flex-col">
              <div className="flex items-center gap-1.5 mb-3">
                <TrendingDown className="h-3.5 w-3.5 text-indigo-500" />
                <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full">
                  Gap Historical Trend
                </span>
              </div>
              {isLoadingGapTrend ? (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
                  <span className="ml-2 text-slate-500 text-sm">Loading…</span>
                </div>
              ) : gapTrendError ? (
                <div className="flex items-center justify-center h-64 text-red-500 text-sm">
                  {gapTrendError}
                </div>
              ) : (
                <CompetitorGapTrendChart
                  dataPoints={gapTrendData}
                  brandName={brandName}
                  competitorName={selectedCompetitor}
                />
              )}
            </div>

            {/* Col 2: Ranking Detail */}
            <div className="w-1/2 min-w-0 pl-4 flex flex-col">
              <div className="flex items-center gap-1.5 mb-3">
                <TrendingUp className="h-3.5 w-3.5 text-violet-500" />
                <span className="text-xs font-semibold text-violet-700 bg-violet-50 px-2 py-0.5 rounded-full">
                  Ranking Detail
                </span>
              </div>
              {isLoadingRanking ? (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
                  <span className="ml-2 text-slate-500 text-sm">Loading…</span>
                </div>
              ) : rankingError ? (
                <div className="flex items-center justify-center h-64 text-red-500 text-sm">
                  {rankingError}
                </div>
              ) : (
                <CompetitorRankingDetailChart
                  dataPoints={rankingData}
                  brandName={brandName}
                  competitorName={selectedCompetitor}
                />
              )}
            </div>
          </div>

          {/* Horizontal row divider */}
          <div className="h-px w-full bg-slate-200/60" />

          {/* Row 2 — Sentiment Comparison | Competitor Detail */}
          <div className="flex pt-4 pb-2">
            {/* Col 1: Sentiment Comparison */}
            <div className="w-1/2 min-w-0 pr-4 flex flex-col">
              <div className="flex items-center gap-1.5 mb-3">
                <MessageCircle className="h-3.5 w-3.5 text-rose-500" />
                <span className="text-xs font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full">
                  Sentiment Comparison
                </span>
              </div>
              <SentimentComparisonTable
                brandId={brandId}
                segment={dbSegment}
                competitorBrandName={selectedCompetitor}
                timeRange={timeRange}
                customStartDate={customStartDate}
                customEndDate={customEndDate}
                brandName={brandName}
                competitorName={selectedCompetitor}
              />
            </div>

            {/* Col 2: Reference Source Comparison */}
            <div className="w-1/2 min-w-0 pl-4 flex flex-col">
              <div className="flex items-center gap-1.5 mb-3">
                <Link2 className="h-3.5 w-3.5 text-teal-500" />
                <span className="text-xs font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full">
                  Reference Sources
                </span>
              </div>
              <ReferenceSourceComparisonTable
                brandId={brandId}
                segment={dbSegment}
                competitorBrandName={selectedCompetitor}
                timeRange={timeRange}
                customStartDate={customStartDate}
                customEndDate={customEndDate}
                brandName={brandName}
                competitorName={selectedCompetitor}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ── Exported page component ────────────────────────────────────────────────────

export function CompetitiveAnalysis() {
  const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(
    null,
  )

  return (
    <DashboardPageLayout
      title="Competitive Analysis"
      description="Analyze competitor performance relative to your brand in AI search results"
      brandCardTitle="Competitive Current Status"
      brandCardDescription=""
      showProjectRole={false}
      brandCardExtras={(
        selectedBrand: UserBrand | undefined,
        selectedSegment: string,
      ) =>
        selectedBrand ? (
          <CompetitorSelector
            brandId={selectedBrand.brand_id}
            segment={selectedSegment}
            selectedCompetitor={selectedCompetitor}
            onCompetitorChange={setSelectedCompetitor}
          />
        ) : null
      }
    >
      {({
        selectedBrandId,
        selectedBrand,
        selectedSegment,
        timeRange,
        customStartDate,
        customEndDate,
        timeRangeControls,
        customDateInputs,
      }) => (
        <FeatureGate
          feature="competitiveAnalysisFull"
          upgradeMessage="Upgrade to Basic to unlock full competitive analysis charts and tables."
        >
          <CompetitiveAnalysisContent
            brandId={selectedBrandId}
            brandName={selectedBrand.brand_name}
            segment={selectedSegment}
            selectedCompetitor={selectedCompetitor}
            timeRange={timeRange}
            customStartDate={customStartDate}
            customEndDate={customEndDate}
            timeRangeControls={timeRangeControls}
            customDateInputs={customDateInputs}
          />
        </FeatureGate>
      )}
    </DashboardPageLayout>
  )
}
