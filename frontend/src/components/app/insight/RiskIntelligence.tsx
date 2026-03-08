import {
  AlertTriangle,
  Calendar,
  ChartColumnBig,
  ChartLine,
  Loader2,
  Shield,
  TrendingDown,
  Zap,
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
  type InsightSignalSeverity,
  type RiskHistoryDataPoint,
  type TimeRange,
  type UserBrand,
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

// ── Tab configuration ──────────────────────────────────────────

const TABS = [
  {
    id: "competitive",
    label: "Competitive Risk",
    icon: Shield,
    signalKeys: [
      "competitive_dominance_signal",
      "competitive_erosion_signal",
      "competitive_breakthrough_signal",
      "rank_displacement_signal",
    ],
    historyKeys: [
      { key: "competitive_dominance", label: "Dominance", color: "#3b82f6" },
      { key: "competitive_erosion", label: "Erosion", color: "#ef4444" },
      { key: "competitor_breakthrough", label: "Breakthrough", color: "#f97316" },
      { key: "rank_displacement", label: "Rank Displacement", color: "#8b5cf6" },
    ],
    hint: "These signals reflect how your brand's AI visibility compares to competitors. High severity means competitors are actively gaining ground in AI-generated responses. Monitor weekly to detect competitive pressure before it affects brand reach.",
  },
  {
    id: "growth",
    label: "Growth & Momentum",
    icon: TrendingDown,
    signalKeys: [
      "deceleration_warning_signal",
      "new_entrant_signal",
    ],
    historyKeys: [
      { key: "growth_deceleration", label: "Growth Deceleration", color: "#f97316" },
      { key: "new_entrant", label: "New Entrant", color: "#ec4899" },
    ],
    hint: "Track whether your AI visibility trajectory is accelerating or stalling, and watch for new competitors entering the AI search landscape. A new entrant with High severity has gained meaningful AI visibility quickly and warrants immediate attention.",
  },
  {
    id: "structural",
    label: "Structural Health",
    icon: Zap,
    signalKeys: [
      "weak_structural_position_signal",
      "fragile_leadership_signal",
      "volatility_spike_signal",
    ],
    historyKeys: [
      { key: "position_weakness", label: "Position Weakness", color: "#ef4444" },
      { key: "fragile_leadership", label: "Fragile Leadership", color: "#f97316" },
      { key: "volatility_spike", label: "Volatility Spike", color: "#8b5cf6" },
    ],
    hint: "Structural signals assess the stability and fundamentals of your AI presence. A weak or volatile structure means your brand appears inconsistently or at low positions — this is the foundation of long-term AI visibility.",
  },
]

const TIME_RANGES: { label: string; value: TimeRange }[] = [
  { label: "1M", value: "1month" },
  { label: "1Q", value: "1quarter" },
  { label: "1Y", value: "1year" },
  { label: "YTD", value: "ytd" },
]

// ── Sub-components ─────────────────────────────────────────────

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

function SignalCard({ signal }: { signal: InsightSignalSeverity }) {
  return (
    <div className="rounded-lg border bg-card p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">{signal.signal_name}</span>
        <SeverityBadge severity={signal.severity} />
      </div>
      <p className="text-xs text-slate-500 leading-relaxed">{signal.business_meaning}</p>
      {signal.signal_score !== undefined && (
        <p className="text-xs text-slate-400">Score: {signal.signal_score.toFixed(2)}</p>
      )}
    </div>
  )
}

function HintPanel({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-blue-100 bg-blue-50 p-4">
      <AlertTriangle className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
      <p className="text-sm text-blue-700 leading-relaxed">{text}</p>
    </div>
  )
}

type ChartDataPoint = Record<string, string | number | null>

function buildChartData(
  dataPoints: RiskHistoryDataPoint[],
  historyKeys: { key: string; label: string }[],
): ChartDataPoint[] {
  return dataPoints.map((pt) => {
    const row: ChartDataPoint = { date: pt.date }
    for (const { key, label } of historyKeys) {
      row[label] = (pt as unknown as Record<string, number | null>)[key]
    }
    return row
  })
}

// ── Main component ─────────────────────────────────────────────

export default function RiskIntelligence() {
  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState("All-Segment")

  const [allSignals, setAllSignals] = useState<InsightSignalSeverity[]>([])
  const [isLoadingOverview, setIsLoadingOverview] = useState(false)

  const [activeTab, setActiveTab] = useState("competitive")
  const [timeRange, setTimeRange] = useState<TimeRange>("1month")
  const [showCustomDate, setShowCustomDate] = useState(false)
  const [customDateRange, setCustomDateRange] = useState({ start: "", end: "" })
  const [customDateApplied, setCustomDateApplied] = useState<{ start: string; end: string } | null>(null)

  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [isLoadingChart, setIsLoadingChart] = useState(false)

  // Load brands on mount
  useEffect(() => {
    dashboardAPI.getUserBrands().then((res) => {
      setBrands(res.brands)
      if (res.brands.length > 0) setSelectedBrandId(res.brands[0].brand_id)
    })
  }, [])

  // Load segments when brand changes
  useEffect(() => {
    if (!selectedBrandId) return
    dashboardAPI.getBrandSegments(selectedBrandId).then((res) => {
      setSegments(res.segments)
      setSelectedSegment("All-Segment")
    })
  }, [selectedBrandId])

  // Load risk overview when brand or segment changes
  useEffect(() => {
    if (!selectedBrandId) return
    setIsLoadingOverview(true)
    dashboardAPI
      .getRiskOverview({ brandId: selectedBrandId, segment: selectedSegment })
      .then((res) => setAllSignals(res.signals))
      .catch(() => toast.error("Failed to load risk overview"))
      .finally(() => setIsLoadingOverview(false))
  }, [selectedBrandId, selectedSegment])

  // Load chart data when brand, segment, or time range changes
  const loadChart = useCallback(async () => {
    if (!selectedBrandId) return
    setIsLoadingChart(true)
    try {
      const params =
        timeRange === "custom" && customDateApplied
          ? {
              brandId: selectedBrandId,
              segment: selectedSegment,
              timeRange: "custom" as TimeRange,
              startDate: customDateApplied.start,
              endDate: customDateApplied.end,
            }
          : { brandId: selectedBrandId, segment: selectedSegment, timeRange }

      const res = await dashboardAPI.getRiskHistory(params)
      const tab = TABS.find((t) => t.id === activeTab)!
      setChartData(buildChartData(res.data_points, tab.historyKeys))
    } catch {
      toast.error("Failed to load risk history")
    } finally {
      setIsLoadingChart(false)
    }
  }, [selectedBrandId, selectedSegment, timeRange, customDateApplied, activeTab])

  useEffect(() => {
    loadChart()
  }, [loadChart])

  const currentTab = TABS.find((t) => t.id === activeTab)!
  const tabSignals = allSignals.filter((s) => currentTab.signalKeys.includes(s.signal_type))

  const handleApplyCustomDate = () => {
    if (customDateRange.start && customDateRange.end) {
      setCustomDateApplied({ start: customDateRange.start, end: customDateRange.end })
    }
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-slate-600" />
          <h1 className="text-xl font-semibold text-slate-800">Risk Intelligence</h1>
        </div>
        <Button variant="outline" size="sm" onClick={loadChart} disabled={isLoadingChart}>
          {isLoadingChart ? <Loader2 className="h-4 w-4 animate-spin" /> : "Refresh"}
        </Button>
      </div>

      {/* Brand + Segment selectors */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex gap-3 flex-wrap">
            <Select value={selectedBrandId ?? ""} onValueChange={setSelectedBrandId}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select brand" />
              </SelectTrigger>
              <SelectContent>
                {brands.map((b) => (
                  <SelectItem key={b.brand_id} value={b.brand_id}>
                    {b.brand_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedSegment} onValueChange={setSelectedSegment}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select segment" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All-Segment">All Segments</SelectItem>
                {segments.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Main content card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold text-slate-700">
            Risk Signal Overview
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          {/* Category tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              {TABS.map((tab) => (
                <TabsTrigger key={tab.id} value={tab.id} className="flex items-center gap-1.5">
                  <tab.icon className="h-3.5 w-3.5" />
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {/* Signal cards */}
          {isLoadingOverview ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {tabSignals.length > 0
                ? tabSignals.map((signal) => (
                    <SignalCard key={signal.signal_type} signal={signal} />
                  ))
                : <p className="text-sm text-slate-400 col-span-full">No signal data available.</p>
              }
            </div>
          )}

          {/* Hint panel */}
          <HintPanel text={currentTab.hint} />

          {/* Historical chart section */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-2">
                <Tabs value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
                  <TabsList>
                    {TIME_RANGES.map((r) => (
                      <TabsTrigger key={r.value} value={r.value}>
                        {r.label}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowCustomDate(!showCustomDate)}
                  className="flex items-center gap-1"
                >
                  <Calendar className="h-3.5 w-3.5" />
                  Custom
                </Button>
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant={chartType === "line" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartType("line")}
                >
                  <ChartLine className="h-4 w-4" />
                </Button>
                <Button
                  variant={chartType === "bar" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartType("bar")}
                >
                  <ChartColumnBig className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {showCustomDate && (
              <div className="flex items-center gap-2 flex-wrap">
                <input
                  type="date"
                  className="border rounded px-2 py-1 text-sm"
                  value={customDateRange.start}
                  onChange={(e) => setCustomDateRange((p) => ({ ...p, start: e.target.value }))}
                />
                <span className="text-sm text-slate-500">to</span>
                <input
                  type="date"
                  className="border rounded px-2 py-1 text-sm"
                  value={customDateRange.end}
                  onChange={(e) => setCustomDateRange((p) => ({ ...p, end: e.target.value }))}
                />
                <Button size="sm" onClick={handleApplyCustomDate}>
                  Apply
                </Button>
              </div>
            )}

            {isLoadingChart ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                {chartType === "line" ? (
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis domain={[0, 4]} ticks={[1, 2, 4]} tick={{ fontSize: 11 }}
                      tickFormatter={(v) => v === 1 ? "Low" : v === 2 ? "Med" : "High"} />
                    <Tooltip
                      formatter={(v: number | undefined) => v === 1 ? "Low" : v === 2 ? "Medium" : "High"}
                    />
                    <Legend />
                    {currentTab.historyKeys.map(({ label, color }) => (
                      <Line
                        key={label}
                        type="monotone"
                        dataKey={label}
                        stroke={color}
                        strokeWidth={2}
                        dot={false}
                        connectNulls
                      />
                    ))}
                  </LineChart>
                ) : (
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis domain={[0, 4]} ticks={[1, 2, 4]} tick={{ fontSize: 11 }}
                      tickFormatter={(v) => v === 1 ? "Low" : v === 2 ? "Med" : "High"} />
                    <Tooltip
                      formatter={(v: number | undefined) => v === 1 ? "Low" : v === 2 ? "Medium" : "High"}
                    />
                    <Legend />
                    {currentTab.historyKeys.map(({ label, color }) => (
                      <Bar key={label} dataKey={label} fill={color} />
                    ))}
                  </BarChart>
                )}
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
