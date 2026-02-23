import { Calendar, ChartColumnBig, ChartLine, Lightbulb, Loader2 } from "lucide-react"
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
  type BrandRiskOverviewResponse,
  type InsightSignalSeverity,
  type RiskHistoryDataPoint,
  type RiskHistoryResponse,
  type TimeRange,
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

// ── Signal display config ──────────────────────────────────────

const SIGNAL_COLORS: Record<string, string> = {
  "Competitive Dominance Risk": "#3b82f6",
  "Competitive Erosion Risk": "#8b5cf6",
  "Competitor Breakthrough Risk": "#f97316",
  "Growth Deceleration Risk": "#ec4899",
  "Position Structure Weakness Risk": "#22c55e",
}

const CHART_KEYS = [
  { dataKey: "competitive_dominance", name: "Competitive Dominance Risk" },
  { dataKey: "competitive_erosion", name: "Competitive Erosion Risk" },
  { dataKey: "competitor_breakthrough", name: "Competitor Breakthrough Risk" },
  { dataKey: "growth_deceleration", name: "Growth Deceleration Risk" },
  { dataKey: "position_weakness", name: "Position Structure Weakness Risk" },
]

const SEVERITY_LABEL: Record<number, string> = { 1: "Low", 2: "Medium", 4: "High" }

// ── Severity badge component ───────────────────────────────────

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

// ── Chart helpers ──────────────────────────────────────────────

const formatDateForDisplay = (isoDate: string): string => {
  const d = new Date(isoDate)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

interface ChartDataPoint {
  date: string
  displayDate: string
  "Competitive Dominance Risk": number | null
  "Competitive Erosion Risk": number | null
  "Competitor Breakthrough Risk": number | null
  "Growth Deceleration Risk": number | null
  "Position Structure Weakness Risk": number | null
}

function transformHistoryData(dataPoints: RiskHistoryDataPoint[]): ChartDataPoint[] {
  return dataPoints.map((p) => ({
    date: p.date,
    displayDate: formatDateForDisplay(p.date),
    "Competitive Dominance Risk": p.competitive_dominance,
    "Competitive Erosion Risk": p.competitive_erosion,
    "Competitor Breakthrough Risk": p.competitor_breakthrough,
    "Growth Deceleration Risk": p.growth_deceleration,
    "Position Structure Weakness Risk": p.position_weakness,
  }))
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-gray-700 mb-2">{label}</p>
      {payload.map((entry: any) => {
        const severityText = SEVERITY_LABEL[entry.value] || "N/A"
        return (
          <div key={entry.name} className="flex items-center gap-2 text-sm">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600">{entry.name}:</span>
            <span className="font-medium">{severityText}</span>
          </div>
        )
      })}
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

const CustomYAxisTick = ({ x, y, payload }: any) => {
  const label = SEVERITY_LABEL[payload.value]
  if (!label) return null
  return (
    <text x={x} y={y} dy={4} textAnchor="end" fontSize={12} fill="#64748b">
      {label}
    </text>
  )
}

// ── Main component ─────────────────────────────────────────────

export default function Insight() {
  // Brand selection
  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [isLoadingBrands, setIsLoadingBrands] = useState(true)
  const [brandsError, setBrandsError] = useState<string | null>(null)

  // Segment selection
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState<string>("All-Segment")

  // Risk overview (5 cards)
  const [riskOverview, setRiskOverview] = useState<BrandRiskOverviewResponse | null>(null)
  const [isLoadingOverview, setIsLoadingOverview] = useState(false)

  // Time range
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

  // ── Fetch risk overview on brand+segment change ──
  useEffect(() => {
    if (!selectedBrandId || !selectedSegment) return
    const fetchOverview = async () => {
      try {
        setIsLoadingOverview(true)
        const data = await dashboardAPI.getRiskOverview({
          brandId: selectedBrandId,
          segment: selectedSegment,
        })
        setRiskOverview(data)
      } catch {
        setRiskOverview(null)
      } finally {
        setIsLoadingOverview(false)
      }
    }
    fetchOverview()
  }, [selectedBrandId, selectedSegment])

  // ── Fetch risk history on brand+segment+timeRange change ──
  useEffect(() => {
    if (!selectedBrandId || !selectedSegment) return
    if (timeRange === "custom" && (!customDateApplied?.start || !customDateApplied?.end)) return

    const fetchHistory = async () => {
      try {
        setIsLoadingChart(true)
        const data: RiskHistoryResponse = await dashboardAPI.getRiskHistory({
          brandId: selectedBrandId,
          segment: selectedSegment,
          timeRange,
          startDate: customDateApplied?.start,
          endDate: customDateApplied?.end,
        })
        setChartData(transformHistoryData(data.data_points))
      } catch {
        setChartData([])
      } finally {
        setIsLoadingChart(false)
      }
    }
    fetchHistory()
  }, [selectedBrandId, selectedSegment, timeRange, customDateApplied])

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

  // ── Render ──
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6 sm:space-y-8">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl sm:text-4xl font-bold text-slate-900">Insight</h1>
            <p className="text-slate-600 mt-1 text-sm sm:text-base">
              AI-powered risk signals and performance insights for your brand
            </p>
          </div>
          <Button variant="outline" onClick={handleRefresh} size="sm">
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
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <Select
                  value={selectedBrandId || undefined}
                  onValueChange={setSelectedBrandId}
                >
                  <SelectTrigger className="w-full sm:w-[350px]">
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

        {/* Risk Overview Card */}
        {selectedBrandId && (
          <Card className="shadow-lg">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                <CardTitle className="text-xl font-bold">
                  Your Brand Risk Overview
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Segment selector */}
              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <span className="text-sm font-medium text-slate-700">Segment:</span>
                <Select value={selectedSegment} onValueChange={setSelectedSegment}>
                  <SelectTrigger className="w-full sm:w-[220px]">
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

              {/* 5 Severity Cards */}
              {isLoadingOverview ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
                </div>
              ) : riskOverview ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                  {riskOverview.signals.map((signal: InsightSignalSeverity) => (
                    <div
                      key={signal.signal_type}
                      className="border rounded-lg p-4 bg-white shadow-sm flex flex-col items-center gap-3"
                    >
                      <span className="text-xs font-semibold text-slate-600 text-center leading-tight">
                        {signal.signal_name}
                      </span>
                      <SeverityBadge severity={signal.severity} />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 text-center py-4">
                  No risk data available
                </p>
              )}

              {/* Divider */}
              <hr className="border-slate-200" />

              {/* Risk Historical Status header row */}
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-lg font-semibold text-slate-800">
                    Risk Historical Status
                  </span>
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
                <div className="flex flex-col sm:flex-row gap-3 sm:items-end p-4 bg-gray-50 rounded-lg">
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
                <div className="flex items-center justify-center h-64 sm:h-80 lg:h-96">
                  <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                </div>
              ) : chartData.length === 0 ? (
                <div className="w-full h-64 sm:h-80 lg:h-96 bg-gray-50 rounded-lg flex items-center justify-center">
                  <p className="text-slate-500">
                    No data available for the selected time range
                  </p>
                </div>
              ) : (
                <div className="w-full h-64 sm:h-80 lg:h-96 bg-gray-50 rounded-lg p-4">
                  <ResponsiveContainer width="100%" height="100%">
                    {chartType === "line" ? (
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis
                          dataKey="displayDate"
                          tick={{ fontSize: 12, fill: "#64748b" }}
                        />
                        <YAxis
                          domain={[0, 5]}
                          ticks={[1, 2, 4]}
                          tick={<CustomYAxisTick />}
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
                        {CHART_KEYS.map(({ dataKey, name }) => (
                          <Line
                            key={dataKey}
                            type="monotone"
                            dataKey={name}
                            stroke={SIGNAL_COLORS[name]}
                            strokeWidth={2}
                            dot={{ r: 3 }}
                            activeDot={{ r: 5 }}
                            hide={hiddenSeries.has(name)}
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
                          domain={[0, 5]}
                          ticks={[1, 2, 4]}
                          tick={<CustomYAxisTick />}
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
                        {CHART_KEYS.map(({ dataKey, name }) => (
                          <Bar
                            key={dataKey}
                            dataKey={name}
                            fill={SIGNAL_COLORS[name]}
                            hide={hiddenSeries.has(name)}
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
