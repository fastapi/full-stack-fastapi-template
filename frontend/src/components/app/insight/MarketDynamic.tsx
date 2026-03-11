import {
  BarChart2,
  Calendar,
  ChartColumnBig,
  ChartLine,
  Crosshair,
  Eye,
  Loader2,
  Target,
  Zap,
} from "lucide-react"
import { useEffect, useState } from "react"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts"
import {
  dashboardAPI,
  type MarketDynamicBrandData,
  type MarketDynamicResponse,
  type TimeRange,
  type UserBrand,
} from "@/clients/dashboard"
import {
  axisProps,
  CHART_COLORS,
  CHART_PALETTE,
  formatShortDate,
  gridProps,
  legendClasses,
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

// ── Brand colour palette ──────────────────────────────────────────────────────

const BRAND_COLORS = [
  ...CHART_PALETTE,
  CHART_COLORS.indigoLight,
  CHART_COLORS.greenLight,
  CHART_COLORS.orangeLight,
  "#ec4899",
  "#f43f5e",
]

function brandColor(index: number): string {
  return BRAND_COLORS[index % BRAND_COLORS.length]
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const formatPct = (v: number): string => `${(v * 100).toFixed(1)}%`

/** Pivot brands × dates into [{date, BrandA: value, ...}] for area/line charts */
function pivotTimeSeries(
  brands: MarketDynamicBrandData[],
  field: "visibility_share" | "search_momentum" | "position_strength",
): Record<string, string | number | null>[] {
  const dateMap = new Map<string, Record<string, string | number | null>>()
  for (const brand of brands) {
    for (const pt of brand.data_points) {
      if (!dateMap.has(pt.date)) {
        dateMap.set(pt.date, {
          date: pt.date,
          displayDate: formatShortDate(pt.date),
        })
      }
      const row = dateMap.get(pt.date)!
      row[brand.brand_name] = pt[field] ?? null
    }
  }
  return Array.from(dateMap.values()).sort((a, b) =>
    (a.date as string).localeCompare(b.date as string),
  )
}

/** Get latest-date visibility share for pie chart */
function latestVisibilitySlices(brands: MarketDynamicBrandData[]) {
  // find the most recent date available across all brands
  let latestDate = ""
  for (const brand of brands) {
    for (const pt of brand.data_points) {
      if (pt.date > latestDate) latestDate = pt.date
    }
  }
  if (!latestDate) return []
  return brands
    .map((brand, i) => {
      const pt = brand.data_points.find((p) => p.date === latestDate)
      return {
        name: brand.brand_name,
        value: pt?.visibility_share ?? 0,
        color: brandColor(i),
        isTarget: brand.is_target,
      }
    })
    .filter((s) => s.value > 0)
}

// ── Custom tooltip ─────────────────────────────────────────────────────────────

const TimeSeriesCustomTooltip = ({
  active,
  payload,
  label,
  formatter,
}: {
  active?: boolean
  payload?: any[]
  label?: string
  formatter?: (v: number) => string
}) => {
  if (!active || !payload || payload.length === 0) return null
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
              {formatter ? formatter(entry.value) : entry.value?.toFixed(2)}
            </span>
          </div>
        ))}
    </div>
  )
}

const PieCustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload || payload.length === 0) return null
  const entry = payload[0]
  return (
    <div className={tooltipClasses.container}>
      <p
        className={tooltipClasses.label}
        style={{ color: entry.payload.color }}
      >
        {entry.name}
      </p>
      <p className={tooltipClasses.value}>{formatPct(entry.value)}</p>
    </div>
  )
}

const QuadrantTooltip = ({ active, payload }: any) => {
  if (!active || !payload || payload.length === 0) return null
  const d = payload[0]?.payload
  if (!d) return null
  return (
    <div className={tooltipClasses.container}>
      <p className={tooltipClasses.label} style={{ color: d.color }}>
        {d.name}
        {d.isTarget && " (target)"}
      </p>
      <p className={tooltipClasses.name}>Avg Visibility: {formatPct(d.x)}</p>
      <p className={tooltipClasses.name}>Position Strength: {d.y.toFixed(2)}</p>
    </div>
  )
}

// ── Custom legend (toggle-able) ────────────────────────────────────────────────

function BrandLegend({
  brands,
  hidden,
  onToggle,
}: {
  brands: { name: string; color: string }[]
  hidden: Set<string>
  onToggle: (name: string) => void
}) {
  return (
    <div className={legendClasses.container}>
      {brands.map(({ name, color }) => (
        <button
          key={name}
          type="button"
          onClick={() => onToggle(name)}
          className={`${legendClasses.item} ${hidden.has(name) ? "opacity-30" : "opacity-100"}`}
        >
          <span
            className="w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{ backgroundColor: color }}
          />
          <span className={`${legendClasses.label} max-w-[100px] truncate`}>
            {name}
          </span>
        </button>
      ))}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

const ALL_SEGMENT_VALUE = "All-Segment"

export default function MarketDynamic() {
  // Brand / segment selection
  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [isLoadingBrands, setIsLoadingBrands] = useState(true)
  const [segments, setSegments] = useState<string[]>([ALL_SEGMENT_VALUE])
  const [selectedSegment, setSelectedSegment] =
    useState<string>(ALL_SEGMENT_VALUE)

  // Time range
  const [timeRange, setTimeRange] = useState<TimeRange>("1month")
  const [showCustomDate, setShowCustomDate] = useState(false)
  const [customDateRange, setCustomDateRange] = useState({ start: "", end: "" })
  const [customDateApplied, setCustomDateApplied] = useState<{
    start: string
    end: string
  } | null>(null)

  // Data
  const [data, setData] = useState<MarketDynamicResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Legend toggles per chart section
  const [hiddenBrands, setHiddenBrands] = useState<Set<string>>(new Set())

  // Chart type toggles for SM and PS
  const [smChartType, setSmChartType] = useState<"line" | "bar">("line")
  const [psChartType, setPsChartType] = useState<"line" | "bar">("line")

  // ── Fetch brands ──
  useEffect(() => {
    const fetch = async () => {
      try {
        setIsLoadingBrands(true)
        const res = await dashboardAPI.getUserBrands()
        setBrands(res.brands)
        if (res.brands.length > 0) setSelectedBrandId(res.brands[0].brand_id)
      } catch {
        // ignore
      } finally {
        setIsLoadingBrands(false)
      }
    }
    fetch()
  }, [])

  // ── Fetch segments ──
  useEffect(() => {
    if (!selectedBrandId) return
    const fetch = async () => {
      try {
        const res = await dashboardAPI.getBrandSegments(selectedBrandId)
        setSegments([
          ALL_SEGMENT_VALUE,
          ...res.segments.filter((s) => s !== ALL_SEGMENT_VALUE),
        ])
        setSelectedSegment(ALL_SEGMENT_VALUE)
      } catch {
        setSegments([ALL_SEGMENT_VALUE])
      }
    }
    fetch()
  }, [selectedBrandId])

  // ── Fetch market dynamic data ──
  useEffect(() => {
    if (!selectedBrandId || !selectedSegment) return
    if (
      timeRange === "custom" &&
      (!customDateApplied?.start || !customDateApplied?.end)
    )
      return

    const fetch = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const res = await dashboardAPI.getMarketDynamic(
          selectedBrandId,
          selectedSegment,
          timeRange,
          customDateApplied?.start,
          customDateApplied?.end,
        )
        setData(res)
        setHiddenBrands(new Set())
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load market data")
        setData(null)
      } finally {
        setIsLoading(false)
      }
    }
    fetch()
  }, [selectedBrandId, selectedSegment, timeRange, customDateApplied])

  const toggleBrand = (name: string) => {
    setHiddenBrands((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  // ── Derived chart data ──
  const allBrands = data?.brands ?? []

  // Assign colours once, keyed by original index so colours stay stable
  const brandMeta = allBrands.map((b, i) => ({
    name: b.brand_name,
    color: brandColor(i),
    isTarget: b.is_target,
  }))

  // Target brand + top-5 competitors by avg visibility share
  const top5Names = new Set<string>([
    ...allBrands.filter((b) => b.is_target).map((b) => b.brand_name),
    ...allBrands
      .filter((b) => !b.is_target)
      .sort((a, b) => b.avg_visibility_share - a.avg_visibility_share)
      .slice(0, 5)
      .map((b) => b.brand_name),
  ])
  const brandsTop = allBrands.filter((b) => top5Names.has(b.brand_name))
  const brandMetaTop = brandMeta.filter((b) => top5Names.has(b.name))

  // Pie: all brands (full picture of latest visibility)
  const visibilitySlices = data ? latestVisibilitySlices(allBrands) : []

  // Other charts: target + top-5 only
  const stackedData = data ? pivotTimeSeries(brandsTop, "visibility_share") : []
  const smData = data ? pivotTimeSeries(brandsTop, "search_momentum") : []
  const psData = data ? pivotTimeSeries(brandsTop, "position_strength") : []
  const quadrantData = brandMeta
    .filter((bm) => top5Names.has(bm.name))
    .map((bm) => {
      const b = allBrands.find((x) => x.brand_name === bm.name)!
      return {
        x: b.avg_visibility_share,
        y: b.median_position_strength,
        name: bm.name,
        color: bm.color,
        isTarget: bm.isTarget,
      }
    })

  // ── Render helpers ──
  const renderEmptyState = (msg = "No data available") => (
    <div className="flex items-center justify-center h-52 bg-white rounded-2xl border border-slate-200">
      <p className="text-sm text-slate-400">{msg}</p>
    </div>
  )

  const renderLoading = () => (
    <div className="flex items-center justify-center h-52">
      <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
    </div>
  )

  const hasData = data && data.brands.length > 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 px-4 py-4">
      <div className="space-y-4">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Market Dynamic
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Competitive visibility, momentum, and position landscape
          </p>
        </div>

        {/* Main card */}
        <Card className="shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-semibold">
              Market Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Controls row */}
            <div className="flex items-center gap-3 flex-wrap">
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
                    onValueChange={(v) => setSelectedBrandId(v)}
                  >
                    <SelectTrigger className="w-[180px] !h-8 !py-0 px-2 text-xs [&_svg:last-child]:size-3">
                      <SelectValue placeholder="Select a brand" />
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

              {/* Time range — pushed to the right */}
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
                    ).map(([val, label]) => (
                      <TabsTrigger
                        key={val}
                        value={val}
                        className="bg-transparent rounded-none shadow-none px-3 py-1 text-xs
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
                  size="sm"
                  className="h-7 text-xs px-2"
                  onClick={() => setShowCustomDate((v) => !v)}
                >
                  <Calendar className="h-3 w-3 mr-1" />
                  Custom
                </Button>
              </div>
            </div>

            {/* Custom date inputs */}
            {showCustomDate && (
              <div className="flex flex-col sm:flex-row gap-3 sm:items-end p-4 bg-white rounded-2xl border border-slate-200">
                {(["start", "end"] as const).map((key) => (
                  <div key={key} className="flex-1">
                    <label
                      htmlFor={`market-dynamic-${key}-date`}
                      className="text-sm font-medium text-slate-700 block mb-1 capitalize"
                    >
                      {key} Date
                    </label>
                    <input
                      id={`market-dynamic-${key}-date`}
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

            {/* Error state */}
            {error && (
              <div className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-lg p-3">
                {error}
              </div>
            )}

            {/* ── Row 1: Pie + Stacked Area ── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Pie chart */}
              <div>
                <div className="flex items-center gap-1.5 mb-3">
                  <Eye className="h-3.5 w-3.5 text-blue-500" />
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
                    Current Visibility Share
                  </span>
                </div>
                {isLoading ? (
                  renderLoading()
                ) : !hasData || visibilitySlices.length === 0 ? (
                  renderEmptyState()
                ) : (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={visibilitySlices}
                          cx="50%"
                          cy="50%"
                          innerRadius={55}
                          outerRadius={90}
                          dataKey="value"
                          nameKey="name"
                          label={({ value }) =>
                            value > 0.03 ? `${(value * 100).toFixed(0)}%` : ""
                          }
                          labelLine={false}
                        >
                          {visibilitySlices.map((entry) => (
                            <Cell key={entry.name} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip content={<PieCustomTooltip />} />
                        <Legend
                          formatter={(value) => (
                            <span className="text-xs text-slate-600">
                              {value}
                            </span>
                          )}
                          iconType="circle"
                          iconSize={8}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>

              {/* Stacked Area chart */}
              <div>
                <div className="flex items-center gap-1.5 mb-3">
                  <BarChart2 className="h-3.5 w-3.5 text-blue-500" />
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
                    Visibility Share History
                  </span>
                </div>
                {isLoading ? (
                  renderLoading()
                ) : !hasData || stackedData.length === 0 ? (
                  renderEmptyState()
                ) : (
                  <>
                    <div className="h-80 bg-white rounded-2xl border border-slate-200 p-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={stackedData}
                          margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
                        >
                          <CartesianGrid {...gridProps} />
                          <XAxis dataKey="displayDate" {...axisProps} />
                          <YAxis
                            {...axisProps}
                            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                          />
                          <Tooltip
                            content={
                              <TimeSeriesCustomTooltip formatter={formatPct} />
                            }
                          />
                          {brandMetaTop.map(({ name, color }) => (
                            <Area
                              key={name}
                              type="monotone"
                              dataKey={name}
                              stackId="1"
                              stroke={color}
                              fill={color}
                              fillOpacity={0.6}
                              hide={hiddenBrands.has(name)}
                              connectNulls
                            />
                          ))}
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                    <BrandLegend
                      brands={brandMetaTop}
                      hidden={hiddenBrands}
                      onToggle={toggleBrand}
                    />
                  </>
                )}
              </div>
            </div>

            <hr className="border-slate-200" />

            {/* ── Row 2: SM + PS ── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Search Momentum */}
              <div>
                <div className="flex items-center gap-1.5 mb-3">
                  <Zap className="h-3.5 w-3.5 text-blue-500" />
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
                    Search Momentum
                  </span>
                  <Tabs
                    value={smChartType}
                    onValueChange={(v) => setSmChartType(v as "line" | "bar")}
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
                {isLoading ? (
                  renderLoading()
                ) : !hasData || smData.length === 0 ? (
                  renderEmptyState()
                ) : (
                  <>
                    <div className="h-72 bg-white rounded-2xl border border-slate-200 p-2">
                      <ResponsiveContainer width="100%" height="100%">
                        {smChartType === "line" ? (
                          <LineChart
                            data={smData}
                            margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
                          >
                            <CartesianGrid {...gridProps} />
                            <XAxis dataKey="displayDate" {...axisProps} />
                            <YAxis {...axisProps} domain={[-0.25, 1.25]} />
                            <Tooltip content={<TimeSeriesCustomTooltip />} />
                            {brandMetaTop.map(({ name, color, isTarget }) => (
                              <Line
                                key={name}
                                type="monotone"
                                dataKey={name}
                                stroke={color}
                                strokeWidth={isTarget ? 3 : 1.5}
                                dot={false}
                                activeDot={{ r: 3 }}
                                hide={hiddenBrands.has(name)}
                                connectNulls
                              />
                            ))}
                          </LineChart>
                        ) : (
                          <BarChart
                            data={smData}
                            margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
                          >
                            <CartesianGrid {...gridProps} />
                            <XAxis dataKey="displayDate" {...axisProps} />
                            <YAxis {...axisProps} domain={[0, 1.25]} />
                            <Tooltip content={<TimeSeriesCustomTooltip />} />
                            {brandMetaTop.map(({ name, color }) => (
                              <Bar
                                key={name}
                                dataKey={name}
                                fill={color}
                                hide={hiddenBrands.has(name)}
                              />
                            ))}
                          </BarChart>
                        )}
                      </ResponsiveContainer>
                    </div>
                    <BrandLegend
                      brands={brandMetaTop}
                      hidden={hiddenBrands}
                      onToggle={toggleBrand}
                    />
                  </>
                )}
              </div>

              {/* Position Strength */}
              <div>
                <div className="flex items-center gap-1.5 mb-3">
                  <Target className="h-3.5 w-3.5 text-blue-500" />
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
                    Position Strength
                  </span>
                  <Tabs
                    value={psChartType}
                    onValueChange={(v) => setPsChartType(v as "line" | "bar")}
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
                {isLoading ? (
                  renderLoading()
                ) : !hasData || psData.length === 0 ? (
                  renderEmptyState()
                ) : (
                  <>
                    <div className="h-72 bg-white rounded-2xl border border-slate-200 p-2">
                      <ResponsiveContainer width="100%" height="100%">
                        {psChartType === "line" ? (
                          <LineChart
                            data={psData}
                            margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
                          >
                            <CartesianGrid {...gridProps} />
                            <XAxis dataKey="displayDate" {...axisProps} />
                            <YAxis {...axisProps} domain={[-0.25, 1.25]} />
                            <Tooltip content={<TimeSeriesCustomTooltip />} />
                            {brandMetaTop.map(({ name, color, isTarget }) => (
                              <Line
                                key={name}
                                type="monotone"
                                dataKey={name}
                                stroke={color}
                                strokeWidth={isTarget ? 3 : 1.5}
                                dot={false}
                                activeDot={{ r: 3 }}
                                hide={hiddenBrands.has(name)}
                                connectNulls
                              />
                            ))}
                          </LineChart>
                        ) : (
                          <BarChart
                            data={psData}
                            margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
                          >
                            <CartesianGrid {...gridProps} />
                            <XAxis dataKey="displayDate" {...axisProps} />
                            <YAxis {...axisProps} domain={[0, 1.25]} />
                            <Tooltip content={<TimeSeriesCustomTooltip />} />
                            {brandMetaTop.map(({ name, color }) => (
                              <Bar
                                key={name}
                                dataKey={name}
                                fill={color}
                                hide={hiddenBrands.has(name)}
                              />
                            ))}
                          </BarChart>
                        )}
                      </ResponsiveContainer>
                    </div>
                    <BrandLegend
                      brands={brandMetaTop}
                      hidden={hiddenBrands}
                      onToggle={toggleBrand}
                    />
                  </>
                )}
              </div>
            </div>

            <hr className="border-slate-200" />

            {/* ── Row 3: Competitive Matrix ── */}
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <Crosshair className="h-3.5 w-3.5 text-blue-500" />
                <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full">
                  Competitive Matrix
                </span>
              </div>
              <p className="text-xs text-slate-400 mb-3">
                X: Average visibility share · Y: Position strength (0–1)
              </p>
              {isLoading
                ? renderLoading()
                : !hasData || quadrantData.length === 0
                  ? renderEmptyState()
                  : (() => {
                      const PAD_X = 0.05
                      const xs = quadrantData.map((d) => d.x)
                      const xMin = Math.max(0, Math.min(...xs) - PAD_X)
                      const xMax = Math.min(1, Math.max(...xs) + PAD_X)
                      return (
                        <div className="h-96 bg-white rounded-2xl border border-slate-200 p-3">
                          <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart
                              margin={{
                                top: 8,
                                right: 16,
                                bottom: 28,
                                left: 16,
                              }}
                            >
                              <CartesianGrid {...gridProps} />
                              <XAxis
                                type="number"
                                dataKey="x"
                                name="Avg Visibility"
                                domain={[xMin, xMax]}
                                {...axisProps}
                                tickFormatter={(v) =>
                                  `${(v * 100).toFixed(0)}%`
                                }
                                label={{
                                  value: "Avg Visibility Share",
                                  position: "insideBottom",
                                  offset: -14,
                                  fontSize: 11,
                                  fill: "#94a3b8",
                                }}
                              />
                              <YAxis
                                type="number"
                                dataKey="y"
                                name="Position Strength"
                                domain={[-0.5, 1.5]}
                                {...axisProps}
                                tickFormatter={(v) => v.toFixed(2)}
                                label={{
                                  value: "Position Strength",
                                  angle: -90,
                                  position: "insideLeft",
                                  offset: 10,
                                  fontSize: 11,
                                  fill: "#94a3b8",
                                }}
                              />
                              <ZAxis range={[60, 60]} />
                              <Tooltip content={<QuadrantTooltip />} />
                              {quadrantData.map((d) => (
                                <Scatter
                                  key={d.name}
                                  name={d.name}
                                  data={[d]}
                                  fill={d.color}
                                  shape={(props: any) => {
                                    const { cx, cy } = props
                                    return (
                                      <g>
                                        <circle
                                          cx={cx}
                                          cy={cy}
                                          r={d.isTarget ? 10 : 7}
                                          fill={d.color}
                                          fillOpacity={0.8}
                                          stroke={
                                            d.isTarget ? "#1e293b" : "none"
                                          }
                                          strokeWidth={d.isTarget ? 2 : 0}
                                        />
                                        <text
                                          x={cx}
                                          y={cy - 14}
                                          textAnchor="middle"
                                          fontSize={9}
                                          fill="#334155"
                                        >
                                          {d.name.length > 12
                                            ? `${d.name.slice(0, 11)}…`
                                            : d.name}
                                        </text>
                                      </g>
                                    )
                                  }}
                                />
                              ))}
                            </ScatterChart>
                          </ResponsiveContainer>
                        </div>
                      )
                    })()}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
