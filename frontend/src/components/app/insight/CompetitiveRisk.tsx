import {
  Calendar,
  ChartColumnBig,
  ChartLine,
  Loader2,
  Shield,
} from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import {
  type BrandOverviewResponse,
  type BrandRiskOverviewResponse,
  type CompetitorAwarenessResponse,
  type InsightSignalSeverity,
  type TimeRange,
  type TopCompetitorResponse,
  type UserBrand,
  type UserBrandsResponse,
  dashboardAPI,
} from "@/clients/dashboard"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

// ── Chart config ─────────────────────────────────────────────

const CHART_SERIES = [
  { dataKey: "Brand SOV", color: "#3b82f6" },
  { dataKey: "Competitor SOV", color: "#8b5cf6" },
  { dataKey: "SOV Delta", color: "#f97316" },
  { dataKey: "Brand SSI", color: "#22c55e" },
  { dataKey: "Competitor SSI", color: "#ec4899" },
  { dataKey: "SSI Delta", color: "#64748b" },
]

// ── Severity badge ───────────────────────────────────────────

function SeverityBadge({ severity }: { severity: string }) {
  const lower = severity.toLowerCase()
  let classes = "px-3 py-1 rounded-full text-xs font-semibold border "
  if (lower === "high") {
    classes += "text-red-600 bg-red-50 border-red-200"
  } else if (lower === "medium") {
    classes += "text-orange-600 bg-orange-50 border-orange-200"
  } else {
    classes += "text-green-600 bg-green-50 border-green-200"
  }
  return <span className={classes}>{severity}</span>
}

// ── Delta value display ──────────────────────────────────────

function DeltaValue({ value, suffix = "%" }: { value: number; suffix?: string }) {
  const color = value > 0 ? "text-green-600" : value < 0 ? "text-red-600" : "text-slate-600"
  const sign = value > 0 ? "+" : ""
  return (
    <span className={`font-semibold ${color}`}>
      {sign}{value.toFixed(1)}{suffix}
    </span>
  )
}

// ── Chart helpers ────────────────────────────────────────────

const formatDateForDisplay = (isoDate: string): string => {
  const d = new Date(isoDate)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

interface ChartDataPoint {
  date: string
  displayDate: string
  "Brand SOV": number | null
  "Competitor SOV": number | null
  "SOV Delta": number | null
  "Brand SSI": number | null
  "Competitor SSI": number | null
  "SSI Delta": number | null
}

function mergeTimeSeries(
  brandData: BrandOverviewResponse | null,
  competitorData: CompetitorAwarenessResponse | null,
): ChartDataPoint[] {
  const dateMap = new Map<string, ChartDataPoint>()

  if (brandData) {
    for (const p of brandData.data_points) {
      dateMap.set(p.date, {
        date: p.date,
        displayDate: formatDateForDisplay(p.date),
        "Brand SOV": p.share_of_visibility * 100,
        "Competitor SOV": null,
        "SOV Delta": null,
        "Brand SSI": p.search_share_index * 100,
        "Competitor SSI": null,
        "SSI Delta": null,
      })
    }
  }

  if (competitorData) {
    for (const p of competitorData.data_points) {
      const existing = dateMap.get(p.date)
      if (existing) {
        existing["Competitor SOV"] = p.share_of_visibility * 100
        existing["SOV Delta"] =
          existing["Brand SOV"] !== null
            ? existing["Brand SOV"] - p.share_of_visibility * 100
            : null
        existing["Competitor SSI"] = p.search_share_index * 100
        existing["SSI Delta"] =
          existing["Brand SSI"] !== null
            ? existing["Brand SSI"] - p.search_share_index * 100
            : null
      } else {
        dateMap.set(p.date, {
          date: p.date,
          displayDate: formatDateForDisplay(p.date),
          "Brand SOV": null,
          "Competitor SOV": p.share_of_visibility * 100,
          "SOV Delta": null,
          "Brand SSI": null,
          "Competitor SSI": p.search_share_index * 100,
          "SSI Delta": null,
        })
      }
    }
  }

  return Array.from(dateMap.values()).sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
  )
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-gray-700 mb-2">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2 text-sm">
          <span
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-gray-600">{entry.name}:</span>
          <span className="font-medium">
            {entry.value !== null ? `${entry.value.toFixed(1)}%` : "N/A"}
          </span>
        </div>
      ))}
    </div>
  )
}

interface CustomLegendProps {
  payload?: any[]
  hiddenSeries: Set<string>
  onToggle: (name: string) => void
}

const CustomLegend = ({ payload, hiddenSeries, onToggle }: CustomLegendProps) => {
  if (!payload) return null
  return (
    <div className="flex flex-wrap justify-center gap-4 mt-4">
      {payload.map((entry: any) => {
        const isHidden = hiddenSeries.has(entry.value)
        return (
          <button
            key={entry.value}
            type="button"
            onClick={() => onToggle(entry.value)}
            className={`flex items-center gap-2 text-sm cursor-pointer transition-opacity ${
              isHidden ? "opacity-30" : "opacity-100"
            }`}
          >
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600">{entry.value}</span>
          </button>
        )
      })}
    </div>
  )
}

// ── Main component ───────────────────────────────────────────

export default function CompetitiveRisk() {
  // Brand selection
  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [isLoadingBrands, setIsLoadingBrands] = useState(true)
  const [brandsError, setBrandsError] = useState<string | null>(null)

  // Segment selection
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState<string>("All-Segment")

  // Top competitor
  const [topCompetitor, setTopCompetitor] = useState<TopCompetitorResponse | null>(null)

  // Brand overview (for Card 1 metrics)
  const [brandOverview, setBrandOverview] = useState<BrandOverviewResponse | null>(null)

  // Competitor awareness (for Card 1 metrics + breakthrough calc)
  const [competitorAwareness, setCompetitorAwareness] =
    useState<CompetitorAwarenessResponse | null>(null)

  // Risk overview (for severity badges)
  const [riskOverview, setRiskOverview] = useState<BrandRiskOverviewResponse | null>(null)

  // Loading states for Card 1
  const [isLoadingOverview, setIsLoadingOverview] = useState(false)

  // Time range (for chart)
  const [timeRange, setTimeRange] = useState<TimeRange>("1month")
  const [showCustomDate, setShowCustomDate] = useState(false)
  const [customDateRange, setCustomDateRange] = useState({ start: "", end: "" })
  const [customDateApplied, setCustomDateApplied] = useState<{
    start: string
    end: string
  } | null>(null)

  // Chart
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [isLoadingChart, setIsLoadingChart] = useState(false)
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set())

  const selectedBrand = brands.find((b) => b.brand_id === selectedBrandId)

  // ── Fetch brands ──
  const fetchUserBrands = useCallback(async () => {
    try {
      setIsLoadingBrands(true)
      setBrandsError(null)
      const data: UserBrandsResponse = await dashboardAPI.getUserBrands()
      setBrands(data.brands)
      if (data.brands.length > 0 && !selectedBrandId) {
        setSelectedBrandId(data.brands[0].brand_id)
      }
    } catch (err) {
      setBrandsError(err instanceof Error ? err.message : "Failed to load brands")
    } finally {
      setIsLoadingBrands(false)
    }
  }, [selectedBrandId])

  useEffect(() => {
    fetchUserBrands()
  }, [fetchUserBrands])

  // ── Fetch segments on brand change ──
  useEffect(() => {
    if (!selectedBrandId) return
    const fetchSegments = async () => {
      try {
        const data = await dashboardAPI.getBrandSegments(selectedBrandId)
        setSegments(data.segments)
        if (data.segments.length > 0) {
          setSelectedSegment(
            data.segments.includes("All-Segment") ? "All-Segment" : data.segments[0],
          )
        }
      } catch {
        setSegments([])
      }
    }
    fetchSegments()
  }, [selectedBrandId])

  // ── Fetch Card 1 data on brand+segment change ──
  useEffect(() => {
    if (!selectedBrandId || !selectedSegment) return

    const fetchOverviewData = async () => {
      setIsLoadingOverview(true)
      try {
        // Fetch top competitor, brand overview, and risk overview in parallel
        const [topCompRes, brandRes, riskRes] = await Promise.all([
          dashboardAPI.getTopCompetitor({
            brandId: selectedBrandId,
            segment: selectedSegment,
            timeRange: "1month",
          }),
          dashboardAPI.getBrandOverview({
            brandId: selectedBrandId,
            timeRange: "1month",
            segment: selectedSegment,
          }),
          dashboardAPI.getRiskOverview({
            brandId: selectedBrandId,
            segment: selectedSegment,
          }),
        ])

        setTopCompetitor(topCompRes)
        setBrandOverview(brandRes)
        setRiskOverview(riskRes)

        // If we have a top competitor, fetch their awareness data
        if (topCompRes.top_competitor_name) {
          const compRes = await dashboardAPI.getCompetitorAwareness({
            brandId: selectedBrandId,
            competitorBrandName: topCompRes.top_competitor_name,
            timeRange: "1month",
            segment: selectedSegment,
          })
          setCompetitorAwareness(compRes)
        } else {
          setCompetitorAwareness(null)
        }
      } catch {
        setTopCompetitor(null)
        setBrandOverview(null)
        setCompetitorAwareness(null)
        setRiskOverview(null)
      } finally {
        setIsLoadingOverview(false)
      }
    }
    fetchOverviewData()
  }, [selectedBrandId, selectedSegment])

  // ── Fetch chart data on brand+segment+timeRange change ──
  useEffect(() => {
    if (!selectedBrandId || !selectedSegment || !topCompetitor?.top_competitor_name)
      return
    if (timeRange === "custom" && (!customDateApplied?.start || !customDateApplied?.end))
      return

    const fetchChartData = async () => {
      setIsLoadingChart(true)
      try {
        const params = {
          brandId: selectedBrandId,
          timeRange,
          segment: selectedSegment,
          startDate: customDateApplied?.start,
          endDate: customDateApplied?.end,
        }

        const [brandRes, compRes] = await Promise.all([
          dashboardAPI.getBrandOverview(params),
          dashboardAPI.getCompetitorAwareness({
            ...params,
            competitorBrandName: topCompetitor.top_competitor_name!,
          }),
        ])

        setChartData(mergeTimeSeries(brandRes, compRes))
      } catch {
        setChartData([])
      } finally {
        setIsLoadingChart(false)
      }
    }
    fetchChartData()
  }, [selectedBrandId, selectedSegment, timeRange, customDateApplied, topCompetitor])

  const toggleSeries = (name: string) => {
    setHiddenSeries((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  const handleRefresh = async () => {
    try {
      dashboardAPI.clearUserBrandsCache()
      await fetchUserBrands()
      toast.success("Data refreshed successfully")
    } catch {
      toast.error("Failed to refresh data")
    }
  }

  const handleCustomDateApply = () => {
    if (customDateRange.start && customDateRange.end) {
      setTimeRange("custom")
      setCustomDateApplied({ start: customDateRange.start, end: customDateRange.end })
    }
  }

  // ── Computed values for Card 1 ──
  const getSeverity = (signalType: string): InsightSignalSeverity | undefined =>
    riskOverview?.signals.find((s) => s.signal_type === signalType)

  const brandSOV = brandOverview
    ? brandOverview.summary.share_of_visibility.current_value * 100
    : null
  const brandSSI = brandOverview
    ? brandOverview.summary.search_share_index.current_value * 100
    : null

  // Get competitor latest SOV & SSI from data points
  const competitorLatest = competitorAwareness?.data_points.length
    ? competitorAwareness.data_points[competitorAwareness.data_points.length - 1]
    : null
  const competitorSOV = competitorLatest
    ? competitorLatest.share_of_visibility * 100
    : null
  const competitorSSI = competitorLatest
    ? competitorLatest.search_share_index * 100
    : null

  const sovGap =
    brandSOV !== null && competitorSOV !== null ? brandSOV - competitorSOV : null
  const ssiGap =
    brandSSI !== null && competitorSSI !== null ? brandSSI - competitorSSI : null

  // Competitor breakthrough: (current SSI - min SSI in available data) * 100
  const breakthroughScore = (() => {
    if (!competitorAwareness?.data_points.length) return null
    const ssiValues = competitorAwareness.data_points.map((p) => p.search_share_index)
    const currentSSI = ssiValues[ssiValues.length - 1]
    const minSSI = Math.min(...ssiValues)
    return (currentSSI - minSSI) * 100
  })()

  // ── Render ──
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 px-4 py-4">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Competitive Risk</h1>
            <p className="text-slate-600 mt-2">
              Competitive risk analysis comparing your brand against the top competitor
            </p>
          </div>
          <Button variant="outline" onClick={handleRefresh}>
            Refresh Data
          </Button>
        </div>

        {/* Brand Selector */}
        <Card className="shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-semibold">
              Select Brand to Monitor
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingBrands ? (
              <div className="flex items-center gap-2 text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Loading brands...</span>
              </div>
            ) : brandsError ? (
              <div className="text-red-500">
                <p>{brandsError}</p>
                <Button
                  variant="link"
                  className="p-0 h-auto text-red-500 underline"
                  onClick={handleRefresh}
                >
                  Try again
                </Button>
              </div>
            ) : brands.length === 0 ? (
              <p className="text-slate-500">
                No brands found. Create a project with brand settings to get started.
              </p>
            ) : (
              <div className="flex items-center gap-4">
                <Select
                  value={selectedBrandId || undefined}
                  onValueChange={setSelectedBrandId}
                >
                  <SelectTrigger className="w-[350px]">
                    <SelectValue placeholder="Select a brand" />
                  </SelectTrigger>
                  <SelectContent>
                    {brands.map((brand) => (
                      <SelectItem key={brand.brand_id} value={brand.brand_id}>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{brand.brand_name}</span>
                          <span className="text-xs text-slate-400">
                            ({brand.project_name})
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedBrand && (
                  <div className="text-sm text-slate-500">
                    <span className="font-medium">Project:</span>{" "}
                    {selectedBrand.project_name}
                    <span className="mx-2">|</span>
                    <span className="font-medium">Role:</span>{" "}
                    <span className="capitalize">{selectedBrand.user_role}</span>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Card 1: Competitive Risk Overview */}
        {selectedBrandId && (
          <Card className="shadow-lg">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-blue-500" />
                <CardTitle className="text-xl font-bold">
                  Your Brand Competitive Risk Overview
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Segment selector */}
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-slate-700">Segment:</span>
                <Select value={selectedSegment} onValueChange={setSelectedSegment}>
                  <SelectTrigger className="w-[220px]">
                    <SelectValue placeholder="Select segment" />
                  </SelectTrigger>
                  <SelectContent>
                    {segments.map((seg) => (
                      <SelectItem key={seg} value={seg}>
                        {seg}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {isLoadingOverview ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
                </div>
              ) : (
                <>
                  {/* Top competitor label */}
                  <div className="text-sm text-slate-600">
                    <span className="font-medium">Top Competitor:</span>{" "}
                    {topCompetitor?.top_competitor_name ? (
                      <span className="text-slate-800 font-semibold">
                        {topCompetitor.top_competitor_name}
                      </span>
                    ) : (
                      <span className="text-slate-400 italic">No competitor found</span>
                    )}
                  </div>

                  {/* 3 Sub-cards */}
                  <div className="grid grid-cols-3 gap-4">
                    {/* Sub-card A: Competitive Dominance Risk */}
                    <div className="border rounded-lg p-5 bg-white shadow-sm space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-slate-700">
                          Competitive Dominance Risk
                        </span>
                        {getSeverity("competitive_dominance_signal") && (
                          <SeverityBadge
                            severity={
                              getSeverity("competitive_dominance_signal")!.severity
                            }
                          />
                        )}
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-500">Brand SOV</span>
                          <span className="font-semibold text-slate-800">
                            {brandSOV !== null ? `${brandSOV.toFixed(1)}%` : "N/A"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">
                            SOV Gap vs Top Competitor
                          </span>
                          {sovGap !== null ? (
                            <DeltaValue value={sovGap} />
                          ) : (
                            <span className="text-slate-400">N/A</span>
                          )}
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Brand SSI</span>
                          <span className="font-semibold text-slate-800">
                            {brandSSI !== null ? `${brandSSI.toFixed(1)}%` : "N/A"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Sub-card B: Competitive Erosion Risk */}
                    <div className="border rounded-lg p-5 bg-white shadow-sm space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-slate-700">
                          Competitive Erosion Risk
                        </span>
                        {getSeverity("competitive_erosion_signal") && (
                          <SeverityBadge
                            severity={
                              getSeverity("competitive_erosion_signal")!.severity
                            }
                          />
                        )}
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-500">SOV Delta (Brand − Competitor)</span>
                          {sovGap !== null ? (
                            <DeltaValue value={sovGap} />
                          ) : (
                            <span className="text-slate-400">N/A</span>
                          )}
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">SSI Delta (Brand − Competitor)</span>
                          {ssiGap !== null ? (
                            <DeltaValue value={ssiGap} />
                          ) : (
                            <span className="text-slate-400">N/A</span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Sub-card C: Competitor Breakthrough Risk */}
                    <div className="border rounded-lg p-5 bg-white shadow-sm space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-slate-700">
                          Competitor Breakthrough Risk
                        </span>
                        {getSeverity("competitive_breakthrough_signal") && (
                          <SeverityBadge
                            severity={
                              getSeverity("competitive_breakthrough_signal")!.severity
                            }
                          />
                        )}
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-500">
                            SSI Surge (current − 3wk min)
                          </span>
                          <span className="font-semibold text-slate-800">
                            {breakthroughScore !== null
                              ? `${breakthroughScore.toFixed(1)}%`
                              : "N/A"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}

        {/* Card 2: Historical Comparison Chart */}
        {selectedBrandId && topCompetitor?.top_competitor_name && (
          <Card className="shadow-lg">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl font-bold">
                Competitive Historical Comparison
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Time range + chart toggle row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Tabs
                    value={showCustomDate ? "custom" : timeRange}
                    onValueChange={(value) => {
                      if (value === "custom") {
                        setShowCustomDate(true)
                      } else {
                        setTimeRange(value as TimeRange)
                        setShowCustomDate(false)
                        setCustomDateApplied(null)
                      }
                    }}
                  >
                    <TabsList className="bg-transparent rounded-none border-b h-auto p-0">
                      {(
                        [
                          ["1month", "1M"],
                          ["1quarter", "1Q"],
                          ["1year", "1Y"],
                          ["ytd", "YTD"],
                        ] as const
                      ).map(([val, label]) => (
                        <TabsTrigger
                          key={val}
                          value={val}
                          className="bg-transparent rounded-none shadow-none px-4 py-2
                            data-[state=active]:bg-transparent data-[state=active]:shadow-none
                            border-b-2 border-transparent data-[state=active]:border-primary"
                        >
                          {label}
                        </TabsTrigger>
                      ))}
                    </TabsList>
                  </Tabs>
                  <Button
                    variant={showCustomDate ? "default" : "outline"}
                    onClick={() => setShowCustomDate(!showCustomDate)}
                    size="sm"
                    type="button"
                  >
                    <Calendar className="h-4 w-4 mr-2" />
                    Custom Range
                  </Button>
                </div>

                {/* Line / Bar toggle */}
                <Tabs
                  value={chartType}
                  onValueChange={(v) => setChartType(v as "line" | "bar")}
                >
                  <TabsList className="h-8">
                    <TabsTrigger value="line" className="h-6 px-2">
                      <ChartLine size={16} />
                    </TabsTrigger>
                    <TabsTrigger value="bar" className="h-6 px-2">
                      <ChartColumnBig size={16} />
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Custom date inputs */}
              {showCustomDate && (
                <div className="flex gap-3 items-center p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <label className="text-sm font-medium text-gray-700 block mb-1">
                      Start Date
                    </label>
                    <input
                      type="date"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={customDateRange.start}
                      onChange={(e) =>
                        setCustomDateRange({ ...customDateRange, start: e.target.value })
                      }
                    />
                  </div>
                  <div className="flex-1">
                    <label className="text-sm font-medium text-gray-700 block mb-1">
                      End Date
                    </label>
                    <input
                      type="date"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={customDateRange.end}
                      onChange={(e) =>
                        setCustomDateRange({ ...customDateRange, end: e.target.value })
                      }
                    />
                  </div>
                  <Button onClick={handleCustomDateApply} className="mt-6" size="sm">
                    Apply
                  </Button>
                </div>
              )}

              {/* Chart */}
              {isLoadingChart ? (
                <div className="flex items-center justify-center h-96">
                  <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                </div>
              ) : chartData.length === 0 ? (
                <div className="w-full h-96 bg-gray-50 rounded-lg flex items-center justify-center">
                  <p className="text-slate-500">
                    No data available for the selected time range
                  </p>
                </div>
              ) : (
                <div className="w-full h-96 bg-gray-50 rounded-lg p-4">
                  <ResponsiveContainer width="100%" height="100%">
                    {chartType === "line" ? (
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis
                          dataKey="displayDate"
                          tick={{ fontSize: 12, fill: "#64748b" }}
                        />
                        <YAxis
                          domain={[0, 100]}
                          tick={{ fontSize: 12, fill: "#64748b" }}
                          label={{
                            value: "Score (%)",
                            angle: -90,
                            position: "insideLeft",
                            style: { fontSize: 12, fill: "#64748b" },
                          }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                          content={
                            <CustomLegend
                              hiddenSeries={hiddenSeries}
                              onToggle={toggleSeries}
                            />
                          }
                        />
                        {CHART_SERIES.map(({ dataKey, color }) => (
                          <Line
                            key={dataKey}
                            type="monotone"
                            dataKey={dataKey}
                            stroke={color}
                            strokeWidth={2}
                            dot={{ r: 3 }}
                            activeDot={{ r: 5 }}
                            hide={hiddenSeries.has(dataKey)}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    ) : (
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis
                          dataKey="displayDate"
                          tick={{ fontSize: 12, fill: "#64748b" }}
                        />
                        <YAxis
                          domain={[0, 100]}
                          tick={{ fontSize: 12, fill: "#64748b" }}
                          label={{
                            value: "Score (%)",
                            angle: -90,
                            position: "insideLeft",
                            style: { fontSize: 12, fill: "#64748b" },
                          }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                          content={
                            <CustomLegend
                              hiddenSeries={hiddenSeries}
                              onToggle={toggleSeries}
                            />
                          }
                        />
                        {CHART_SERIES.map(({ dataKey, color }) => (
                          <Bar
                            key={dataKey}
                            dataKey={dataKey}
                            fill={color}
                            hide={hiddenSeries.has(dataKey)}
                          />
                        ))}
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
