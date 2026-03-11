import {
  Activity,
  AlertTriangle,
  Calendar,
  ChartColumnBig,
  ChartLine,
  Flag,
  Loader2,
  Shield,
  TrendingDown,
  TrendingUp,
  UserPlus,
  Zap,
} from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import {
  dashboardAPI,
  type InsightSignalSeverity,
  type RiskHistoryDataPoint,
  type TimeRange,
  type UserBrand,
} from "@/clients/dashboard"
import {
  axisProps,
  CHART_COLORS,
  formatShortDate,
  gridProps,
  tooltipClasses,
} from "@/components/app/dashboard/components/chartTheme"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

// ── Tab + signal configuration ────────────────────────────────

const TABS = [
  {
    id: "competitive",
    label: "Competitive Risk",
    Icon: Shield,
    pillText: "text-blue-700",
    pillBg: "bg-blue-50",
    iconColor: "text-blue-500",
    hint: "These signals reflect how your brand's AI visibility compares to competitors. High severity means competitors are actively gaining ground in AI-generated responses.",
    signals: [
      {
        key: "competitive_dominance_signal",
        histKey: "competitive_dominance",
        label: "Competitive Dominance",
        Icon: Shield,
        color: CHART_COLORS.blue,
      },
      {
        key: "competitive_erosion_signal",
        histKey: "competitive_erosion",
        label: "Competitive Erosion",
        Icon: TrendingDown,
        color: CHART_COLORS.red,
      },
      {
        key: "competitive_breakthrough_signal",
        histKey: "competitor_breakthrough",
        label: "Competitor Breakthrough",
        Icon: TrendingUp,
        color: CHART_COLORS.amber,
      },
      {
        key: "rank_displacement_signal",
        histKey: "rank_displacement",
        label: "Rank Displacement",
        Icon: AlertTriangle,
        color: CHART_COLORS.purple,
      },
    ],
  },
  {
    id: "growth",
    label: "Growth & Momentum",
    Icon: TrendingDown,
    pillText: "text-amber-700",
    pillBg: "bg-amber-50",
    iconColor: "text-amber-500",
    hint: "Track whether your AI visibility trajectory is accelerating or stalling, and watch for new competitors entering the AI search landscape. A new entrant with High severity has gained meaningful AI visibility quickly and warrants immediate attention.",
    signals: [
      {
        key: "deceleration_warning_signal",
        histKey: "growth_deceleration",
        label: "Growth Deceleration",
        Icon: TrendingDown,
        color: CHART_COLORS.amber,
      },
      {
        key: "new_entrant_signal",
        histKey: "new_entrant",
        label: "New Entrant",
        Icon: UserPlus,
        color: CHART_COLORS.teal,
      },
    ],
  },
  {
    id: "structural",
    label: "Structural Health",
    Icon: Zap,
    pillText: "text-purple-700",
    pillBg: "bg-purple-50",
    iconColor: "text-purple-500",
    hint: "Structural signals assess the stability and fundamentals of your AI presence. A weak or volatile structure means your brand appears inconsistently or at low positions — this is the foundation of long-term AI visibility.",
    signals: [
      {
        key: "weak_structural_position_signal",
        histKey: "position_weakness",
        label: "Position Weakness",
        Icon: AlertTriangle,
        color: CHART_COLORS.red,
      },
      {
        key: "fragile_leadership_signal",
        histKey: "fragile_leadership",
        label: "Fragile Leadership",
        Icon: Flag,
        color: CHART_COLORS.amber,
      },
      {
        key: "volatility_spike_signal",
        histKey: "volatility_spike",
        label: "Volatility Spike",
        Icon: Activity,
        color: CHART_COLORS.purple,
      },
    ],
  },
] as const

type TabId = (typeof TABS)[number]["id"]

// ── Helpers ───────────────────────────────────────────────────

type ChartRow = Record<string, string | number | null>

function buildChartData(
  dataPoints: RiskHistoryDataPoint[],
  tab: (typeof TABS)[number],
): ChartRow[] {
  return dataPoints.map((pt) => {
    const row: ChartRow = {
      date: pt.date,
      displayDate: formatShortDate(pt.date),
    }
    for (const sig of tab.signals) {
      row[sig.label] = (pt as unknown as Record<string, number | null>)[
        sig.histKey
      ]
    }
    return row
  })
}

// ── Dark tooltip (matches MarketDynamic) ──────────────────────

function RiskChartTooltip({ active, payload, label }: any) {
  if (!active || !payload || payload.length === 0) return null
  const severityLabel = (v: number | null) =>
    v === 4 ? "High" : v === 2 ? "Medium" : v === 1 ? "Low" : "—"
  return (
    <div className={tooltipClasses.container}>
      <p className={tooltipClasses.label}>{label}</p>
      {payload
        .filter((e: any) => e.value !== null && e.value !== undefined)
        .map((entry: any) => (
          <div key={entry.name} className={tooltipClasses.row}>
            <div className="flex items-center gap-1.5">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: entry.color }}
              />
              <span className={tooltipClasses.name}>{entry.name}</span>
            </div>
            <span className={tooltipClasses.value}>
              {severityLabel(entry.value)}
            </span>
          </div>
        ))}
    </div>
  )
}

// ── Signal row ────────────────────────────────────────────────

function SignalRow({
  signal,
  tab,
}: {
  signal: InsightSignalSeverity
  tab: (typeof TABS)[number]
}) {
  const sev = signal.severity?.toLowerCase()
  const SigIcon =
    tab.signals.find((s) => s.key === signal.signal_type)?.Icon ?? AlertTriangle

  const severityText =
    sev === "high"
      ? "text-red-600"
      : sev === "medium"
        ? "text-orange-500"
        : "text-emerald-600"
  const severityBg =
    sev === "high"
      ? "bg-red-50"
      : sev === "medium"
        ? "bg-orange-50"
        : "bg-emerald-50"

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-1.5">
        <SigIcon className={`h-3.5 w-3.5 ${tab.iconColor}`} />
        <span
          className={`text-xs font-semibold ${tab.pillText} ${tab.pillBg} px-2 py-0.5 rounded-full`}
        >
          {signal.signal_name}
        </span>
        <span
          className={`ml-auto text-xs font-semibold px-2 py-0.5 rounded-full ${severityText} ${severityBg}`}
        >
          {signal.severity}
        </span>
      </div>
      <p className="text-xs text-slate-500 leading-relaxed">
        {signal.business_meaning}
      </p>
      {signal.signal_score !== undefined && (
        <p className="text-xs text-slate-400">
          Score: {signal.signal_score.toFixed(2)}
        </p>
      )}
    </div>
  )
}

// ── Loading / empty helpers ───────────────────────────────────

const renderLoading = (h = "h-52") => (
  <div className={`flex items-center justify-center ${h}`}>
    <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
  </div>
)

const renderEmpty = (msg = "No data available", h = "h-52") => (
  <div
    className={`flex items-center justify-center ${h} bg-white rounded-2xl border border-slate-200`}
  >
    <p className="text-sm text-slate-400">{msg}</p>
  </div>
)

// ── Main component ────────────────────────────────────────────

const ALL_SEGMENT = "All-Segment"

export default function RiskIntelligence() {
  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [isLoadingBrands, setIsLoadingBrands] = useState(true)
  const [segments, setSegments] = useState<string[]>([ALL_SEGMENT])
  const [selectedSegment, setSelectedSegment] = useState(ALL_SEGMENT)

  const [activeTab, setActiveTab] = useState<TabId>("competitive")

  const [allSignals, setAllSignals] = useState<InsightSignalSeverity[]>([])
  const [isLoadingOverview, setIsLoadingOverview] = useState(false)
  const [overviewError, setOverviewError] = useState<string | null>(null)

  const [timeRange, setTimeRange] = useState<TimeRange>("1month")
  const [showCustomDate, setShowCustomDate] = useState(false)
  const [customDateRange, setCustomDateRange] = useState({ start: "", end: "" })
  const [customDateApplied, setCustomDateApplied] = useState<{
    start: string
    end: string
  } | null>(null)

  const [chartData, setChartData] = useState<ChartRow[]>([])
  const [isLoadingChart, setIsLoadingChart] = useState(false)
  const [chartError, setChartError] = useState<string | null>(null)
  const [chartType, setChartType] = useState<"line" | "bar">("line")

  // ── Load brands ──
  useEffect(() => {
    setIsLoadingBrands(true)
    dashboardAPI
      .getUserBrands()
      .then((res) => {
        setBrands(res.brands)
        if (res.brands.length > 0) setSelectedBrandId(res.brands[0].brand_id)
      })
      .catch(() => {})
      .finally(() => setIsLoadingBrands(false))
  }, [])

  // ── Load segments ──
  useEffect(() => {
    if (!selectedBrandId) return
    dashboardAPI
      .getBrandSegments(selectedBrandId)
      .then((res) => {
        setSegments([
          ALL_SEGMENT,
          ...res.segments.filter((s) => s !== ALL_SEGMENT),
        ])
        setSelectedSegment(ALL_SEGMENT)
      })
      .catch(() => setSegments([ALL_SEGMENT]))
  }, [selectedBrandId])

  // ── Load risk overview ──
  useEffect(() => {
    if (!selectedBrandId) return
    setIsLoadingOverview(true)
    setOverviewError(null)
    dashboardAPI
      .getRiskOverview({ brandId: selectedBrandId, segment: selectedSegment })
      .then((res) => setAllSignals(res.signals))
      .catch(() => setOverviewError("Failed to load risk signals"))
      .finally(() => setIsLoadingOverview(false))
  }, [selectedBrandId, selectedSegment])

  // ── Load chart history ──
  useEffect(() => {
    if (!selectedBrandId) return
    if (
      timeRange === "custom" &&
      (!customDateApplied?.start || !customDateApplied?.end)
    )
      return
    setIsLoadingChart(true)
    setChartError(null)
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
    dashboardAPI
      .getRiskHistory(params)
      .then((res) => {
        const tab = TABS.find((t) => t.id === activeTab)!
        setChartData(buildChartData(res.data_points, tab))
      })
      .catch(() => setChartError("Failed to load risk history"))
      .finally(() => setIsLoadingChart(false))
  }, [
    selectedBrandId,
    selectedSegment,
    timeRange,
    customDateApplied,
    activeTab,
  ])

  const currentTab = TABS.find((t) => t.id === activeTab)!
  const tabSignals = allSignals.filter((s) =>
    currentTab.signals.some((cs) => cs.key === s.signal_type),
  )
  const CurrentTabIcon = currentTab.Icon

  const kpiStats = useMemo(() => {
    let high = 0
    let medium = 0
    let low = 0
    let scoreSum = 0
    let scoreCount = 0

    for (const signal of allSignals) {
      const sev = signal.severity?.toLowerCase()
      if (sev === "high") high += 1
      if (sev === "medium") medium += 1
      if (sev === "low") low += 1
      if (signal.signal_score !== undefined) {
        scoreSum += signal.signal_score
        scoreCount += 1
      }
    }

    return {
      high,
      medium,
      low,
      avgScore: scoreCount > 0 ? scoreSum / scoreCount : null,
    }
  }, [allSignals])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 px-4 py-4">
      <div className="space-y-4">
        {/* ── Header ── */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Risk Intelligence
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Monitor competitive, growth, and structural risks in your AI search
            presence
          </p>
        </div>

        {/* ── KPI strip ── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "High Risk", value: kpiStats.high, tone: "text-red-600" },
            {
              label: "Medium Risk",
              value: kpiStats.medium,
              tone: "text-amber-600",
            },
            { label: "Low Risk", value: kpiStats.low, tone: "text-emerald-600" },
            {
              label: "Avg Score",
              value:
                kpiStats.avgScore === null
                  ? "—"
                  : kpiStats.avgScore.toFixed(2),
              tone: "text-slate-900",
            },
          ].map((item) => (
            <div
              key={item.label}
              className="rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm"
            >
              <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                {item.label}
              </p>
              <p className={`text-lg font-semibold ${item.tone} tabular-nums`}>
                {item.value}
              </p>
            </div>
          ))}
        </div>

        {/* ── Main card ── */}
        <Card className="shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-semibold">
              Risk Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Controls row */}
            <div className="flex items-center gap-3 flex-wrap rounded-2xl border border-slate-200 bg-white px-4 py-3">
              {/* Brand selector */}
              {isLoadingBrands ? (
                <div className="flex items-center gap-2 text-slate-500 text-xs">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Loading brands…
                </div>
              ) : (
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-500 font-medium whitespace-nowrap">
                    Brand
                  </span>
                  <Select
                    value={selectedBrandId ?? undefined}
                    onValueChange={setSelectedBrandId}
                  >
                    <SelectTrigger className="w-[180px] !h-8 !py-0 px-2 text-xs [&_svg:last-child]:size-3">
                      <SelectValue placeholder="Select brand" />
                    </SelectTrigger>
                    <SelectContent className="max-h-40">
                      {brands.map((b) => (
                        <SelectItem
                          key={b.brand_id}
                          value={b.brand_id}
                          className="text-xs !py-1 px-2"
                        >
                          <span className="font-medium">{b.brand_name}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Segment selector */}
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-500 font-medium whitespace-nowrap">
                  Segment
                </span>
                <Select
                  value={selectedSegment}
                  onValueChange={setSelectedSegment}
                >
                  <SelectTrigger className="w-[180px] !h-8 !py-0 px-2 text-xs [&_svg:last-child]:size-3">
                    <SelectValue placeholder="Select segment" />
                  </SelectTrigger>
                  <SelectContent className="max-h-40">
                    {segments.map((seg) => (
                      <SelectItem
                        key={seg}
                        value={seg}
                        className="text-xs !py-1 px-2"
                      >
                        {seg}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Time range — pushed to right */}
              <div className="ml-auto flex items-center gap-2">
                <Tabs
                  value={showCustomDate ? "custom" : timeRange}
                  onValueChange={(v) => {
                    if (v === "custom") {
                      setShowCustomDate(true)
                    } else {
                      setTimeRange(v as TimeRange)
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
                    ).map(([val, lbl]) => (
                      <TabsTrigger
                        key={val}
                        value={val}
                        className="bg-transparent rounded-none shadow-none px-3 py-1 text-xs
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        {lbl}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                </Tabs>
                <Button
                  variant={showCustomDate ? "default" : "outline"}
                  size="sm"
                  className="h-7 text-xs px-2"
                  onClick={() => setShowCustomDate((v) => !v)}
                >
                  <Calendar className="h-3 w-3 mr-1" />
                  Custom
                </Button>
              </div>
            </div>

            {/* Custom date panel */}
            {showCustomDate && (
              <div className="flex flex-col sm:flex-row gap-3 sm:items-end p-4 bg-white border border-slate-200 rounded-2xl">
                {(["start", "end"] as const).map((key) => (
                  <div key={key} className="flex-1">
                    <label
                      htmlFor={`risk-intelligence-${key}-date`}
                      className="text-sm font-medium text-slate-700 block mb-1 capitalize"
                    >
                      {key} Date
                    </label>
                    <input
                      id={`risk-intelligence-${key}-date`}
                      type="date"
                      className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={customDateRange[key]}
                      onChange={(e) =>
                        setCustomDateRange((r) => ({
                          ...r,
                          [key]: e.target.value,
                        }))
                      }
                    />
                  </div>
                ))}
                <Button
                  size="sm"
                  onClick={() => {
                    if (customDateRange.start && customDateRange.end) {
                      setTimeRange("custom")
                      setCustomDateApplied({
                        start: customDateRange.start,
                        end: customDateRange.end,
                      })
                    }
                  }}
                >
                  Apply
                </Button>
              </div>
            )}

            {/* Category tabs */}
            <Tabs
              value={activeTab}
              onValueChange={(v) => setActiveTab(v as TabId)}
            >
              <TabsList className="rounded-full border border-slate-200 bg-white p-1">
                {TABS.map(({ id, label, Icon: TabIcon }) => (
                  <TabsTrigger
                    key={id}
                    value={id}
                    className="flex items-center gap-1.5"
                  >
                    <TabIcon className="h-3.5 w-3.5" />
                    {label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>

            {/* Hint */}
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <p className="text-xs text-slate-500 leading-relaxed">
                {currentTab.hint}
              </p>
            </div>

            {/* ── Main grid ── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Historical chart */}
              <div className="lg:col-span-2 space-y-3">
                <div className="flex items-center gap-1.5">
                  <CurrentTabIcon
                    className={`h-3.5 w-3.5 ${currentTab.iconColor}`}
                  />
                  <span
                    className={`text-xs font-semibold ${currentTab.pillText} ${currentTab.pillBg} px-2 py-0.5 rounded-full`}
                  >
                    {currentTab.label} — Severity History
                  </span>
                  <Tabs
                    value={chartType}
                    onValueChange={(v) => setChartType(v as "line" | "bar")}
                    className="ml-auto"
                  >
                    <TabsList className="h-7">
                      <TabsTrigger value="line" className="h-5 px-2">
                        <ChartLine size={13} />
                      </TabsTrigger>
                      <TabsTrigger value="bar" className="h-5 px-2">
                        <ChartColumnBig size={13} />
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>

                {chartError ? (
                  <div className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-lg p-3">
                    {chartError}
                  </div>
                ) : isLoadingChart ? (
                  renderLoading("h-72")
                ) : chartData.length === 0 ? (
                  renderEmpty("No history data for this period", "h-72")
                ) : (
                  <div className="h-72 bg-white rounded-2xl border border-slate-200 p-2">
                    <ResponsiveContainer width="100%" height="100%">
                      {chartType === "line" ? (
                        <LineChart
                          data={chartData}
                          margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
                        >
                          <CartesianGrid {...gridProps} />
                          <XAxis dataKey="displayDate" {...axisProps} />
                          <YAxis
                            domain={[0, 5]}
                            ticks={[1, 2, 4]}
                            {...axisProps}
                            tickFormatter={(v) =>
                              v === 1
                                ? "Low"
                                : v === 2
                                  ? "Med"
                                  : v === 4
                                    ? "High"
                                    : ""
                            }
                          />
                          <Tooltip content={<RiskChartTooltip />} />
                          {currentTab.signals.map(({ label, color }) => (
                            <Line
                              key={label}
                              type="monotone"
                              dataKey={label}
                              stroke={color}
                              strokeWidth={2}
                              dot={false}
                              activeDot={{ r: 3 }}
                              connectNulls
                            />
                          ))}
                        </LineChart>
                      ) : (
                        <BarChart
                          data={chartData}
                          margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
                        >
                          <CartesianGrid {...gridProps} />
                          <XAxis dataKey="displayDate" {...axisProps} />
                          <YAxis
                            domain={[0, 5]}
                            ticks={[1, 2, 4]}
                            {...axisProps}
                            tickFormatter={(v) =>
                              v === 1
                                ? "Low"
                                : v === 2
                                  ? "Med"
                                  : v === 4
                                    ? "High"
                                    : ""
                            }
                          />
                          <Tooltip content={<RiskChartTooltip />} />
                          {currentTab.signals.map(({ label, color }) => (
                            <Bar key={label} dataKey={label} fill={color} />
                          ))}
                        </BarChart>
                      )}
                    </ResponsiveContainer>
                  </div>
                )}
              </div>

              {/* Signals list */}
              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-slate-900">
                    Signals
                  </span>
                  <span className="text-xs text-slate-400">
                    {tabSignals.length} total
                  </span>
                </div>
                {overviewError ? (
                  <div className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-lg p-3">
                    {overviewError}
                  </div>
                ) : isLoadingOverview ? (
                  renderLoading("h-40")
                ) : tabSignals.length === 0 ? (
                  renderEmpty("No signal data available", "h-40")
                ) : (
                  <div className="space-y-4">
                    {tabSignals.map((signal) => (
                      <SignalRow
                        key={signal.signal_type}
                        signal={signal}
                        tab={currentTab}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
