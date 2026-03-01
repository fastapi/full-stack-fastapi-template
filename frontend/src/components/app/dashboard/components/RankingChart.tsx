import { ChartColumnBig, ChartLine, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
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
  type BrandRankingTrendDataPoint,
  type TimeRange,
  dashboardAPI,
} from "@/clients/dashboard"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface RankingChartProps {
  brandId: string
  segment: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

// ── Chart config ───────────────────────────────────────────────────────────────

interface ChartPoint {
  date: string
  displayDate: string
  "Min (#)": number | null
  "Max (#)": number | null
  "Median (#)": number | null
  "Avg (#)": number | null
  is_interpolated: boolean
}

const METRIC_COLORS: Record<string, string> = {
  "Min (#)": "#10b981",   // emerald — best rank
  "Max (#)": "#f43f5e",   // rose    — worst rank
  "Median (#)": "#6366f1", // indigo  — median
  "Avg (#)": "#f59e0b",   // amber   — average
}

const METRIC_KEYS = Object.keys(METRIC_COLORS)

const formatDate = (isoDate: string): string => {
  const d = new Date(isoDate)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function buildChartData(points: BrandRankingTrendDataPoint[]): ChartPoint[] {
  return points.map((p) => ({
    date: p.date,
    displayDate: formatDate(p.date),
    "Min (#)": p.min_ranking,
    "Max (#)": p.max_ranking,
    "Median (#)": p.median_ranking,
    "Avg (#)": p.avg_ranking !== null ? +p.avg_ranking.toFixed(1) : null,
    is_interpolated: p.is_interpolated,
  }))
}

// ── Custom tooltip ─────────────────────────────────────────────────────────────

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null

  const isInterpolated = payload[0]?.payload?.is_interpolated ?? false

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-xl p-3 min-w-[190px]">
      <p className="text-[10px] font-semibold text-gray-400 mb-2 uppercase tracking-wide">{label}</p>
      {isInterpolated ? (
        <p className="text-[10px] italic text-gray-500">No ranking data (brand not found)</p>
      ) : (
        payload.map((entry: any) => {
          if (entry.value === null || entry.value === undefined) return null
          return (
            <div key={entry.name} className="flex items-center justify-between gap-4 text-[10px] py-0.5">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }} />
                <span className="text-gray-300">{entry.name}</span>
              </div>
              <span className="font-semibold text-white">#{entry.value}</span>
            </div>
          )
        })
      )}
    </div>
  )
}

// ── Custom legend ──────────────────────────────────────────────────────────────

interface CustomLegendProps {
  payload?: any[]
  hiddenSeries: Set<string>
  onToggle: (name: string) => void
}

const CustomLegend = ({ payload, hiddenSeries, onToggle }: CustomLegendProps) => {
  if (!payload) return null
  return (
    <div className="flex flex-wrap justify-center gap-x-3 gap-y-1 mt-2">
      {payload.map((entry: any) => {
        const isHidden = hiddenSeries.has(entry.value)
        return (
          <button
            key={entry.value}
            type="button"
            onClick={() => onToggle(entry.value)}
            className={`flex items-center gap-1.5 text-[10px] cursor-pointer transition-opacity ${
              isHidden ? "opacity-30" : "opacity-100"
            }`}
          >
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }} />
            <span className="text-gray-600">{entry.value}</span>
          </button>
        )
      })}
      <span className="text-[10px] text-slate-400 ml-1">· lower rank = better</span>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────────────────────

export function RankingChart({
  brandId,
  segment,
  timeRange,
  customStartDate,
  customEndDate,
}: RankingChartProps) {
  const [data, setData] = useState<ChartPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set())
  const [chartType, setChartType] = useState<"line" | "bar">("line")

  useEffect(() => {
    setIsLoading(true)
    setError(null)
    dashboardAPI
      .getBrandRankingTrend({
        brandId,
        segment: segment || "all-segment",
        timeRange,
        startDate: customStartDate,
        endDate: customEndDate,
      })
      .then((res) => setData(buildChartData(res.data_points)))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load ranking data"))
      .finally(() => setIsLoading(false))
  }, [brandId, segment, timeRange, customStartDate, customEndDate])

  const toggleSeries = (name: string) => {
    setHiddenSeries((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  if (isLoading) {
    return (
      <div className="w-full h-80 flex items-center justify-center gap-2 text-slate-400 text-xs">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading ranking data…
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full h-80 flex items-center justify-center text-red-400 text-xs">
        {error}
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="w-full h-80 flex items-center justify-center text-slate-400 text-sm">
        No ranking data available for the selected time range
      </div>
    )
  }

  const commonAxisProps = {
    tick: { fontSize: 10, fill: "#94a3b8" },
    axisLine: false,
    tickLine: false,
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <Tabs value={chartType} onValueChange={(v) => setChartType(v as "line" | "bar")}>
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

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "line" ? (
            <LineChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="displayDate" {...commonAxisProps} />
              {/* reversed: rank #1 at top (lower number = better) */}
              <YAxis
                {...commonAxisProps}
                reversed
                tickFormatter={(v) => `#${v}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend hiddenSeries={hiddenSeries} onToggle={toggleSeries} />} />
              {METRIC_KEYS.map((key) => (
                <Line
                  key={key}
                  type="linear"
                  dataKey={key}
                  stroke={METRIC_COLORS[key]}
                  strokeWidth={1.5}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 2, stroke: "#fff", fill: METRIC_COLORS[key] }}
                  hide={hiddenSeries.has(key)}
                  connectNulls
                />
              ))}
            </LineChart>
          ) : (
            <BarChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="displayDate" {...commonAxisProps} />
              <YAxis
                {...commonAxisProps}
                reversed
                tickFormatter={(v) => `#${v}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend hiddenSeries={hiddenSeries} onToggle={toggleSeries} />} />
              {METRIC_KEYS.map((key) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={METRIC_COLORS[key]}
                  radius={[3, 3, 0, 0]}
                  hide={hiddenSeries.has(key)}
                />
              ))}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
