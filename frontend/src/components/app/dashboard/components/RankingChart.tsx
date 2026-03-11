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
  dashboardAPI,
  type TimeRange,
} from "@/clients/dashboard"
import {
  axisProps,
  CHART_COLORS,
  formatShortDate,
  gridProps,
  legendClasses,
  tooltipClasses,
} from "@/components/app/dashboard/components/chartTheme"
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
  "Min (#)": CHART_COLORS.green,
  "Max (#)": CHART_COLORS.red,
  "Median (#)": CHART_COLORS.blue,
  "Avg (#)": CHART_COLORS.amber,
}

const METRIC_KEYS = Object.keys(METRIC_COLORS)

function buildChartData(points: BrandRankingTrendDataPoint[]): ChartPoint[] {
  return points.map((p) => ({
    date: p.date,
    displayDate: formatShortDate(p.date),
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
    <div className={tooltipClasses.container}>
      <p className={tooltipClasses.label}>{label}</p>
      {isInterpolated ? (
        <p className={tooltipClasses.note}>No ranking data (brand not found)</p>
      ) : (
        payload.map((entry: any) => {
          if (entry.value === null || entry.value === undefined) return null
          return (
            <div key={entry.name} className={tooltipClasses.row}>
              <div className="flex items-center gap-1.5">
                <span
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: entry.color }}
                />
                <span className={tooltipClasses.name}>{entry.name}</span>
              </div>
              <span className={tooltipClasses.value}>#{entry.value}</span>
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

const CustomLegend = ({
  payload,
  hiddenSeries,
  onToggle,
}: CustomLegendProps) => {
  if (!payload) return null
  return (
    <div className={legendClasses.container}>
      {payload.map((entry: any) => {
        const isHidden = hiddenSeries.has(entry.value)
        return (
          <button
            key={entry.value}
            type="button"
            onClick={() => onToggle(entry.value)}
            className={`${legendClasses.item} ${
              isHidden ? "opacity-30" : "opacity-100"
            }`}
          >
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: entry.color }}
            />
            <span className={legendClasses.label}>{entry.value}</span>
          </button>
        )
      })}
      <span className="text-xs text-slate-400 ml-1">· lower rank = better</span>
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
      .catch((err) =>
        setError(
          err instanceof Error ? err.message : "Failed to load ranking data",
        ),
      )
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

  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <Tabs
          value={chartType}
          onValueChange={(v) => setChartType(v as "line" | "bar")}
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

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "line" ? (
            <LineChart
              data={data}
              margin={{ top: 4, right: 4, left: -16, bottom: 0 }}
            >
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="displayDate" {...axisProps} />
              {/* reversed: rank #1 at top (lower number = better) */}
              <YAxis {...axisProps} reversed tickFormatter={(v) => `#${v}`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                content={
                  <CustomLegend
                    hiddenSeries={hiddenSeries}
                    onToggle={toggleSeries}
                  />
                }
              />
              {METRIC_KEYS.map((key) => (
                <Line
                  key={key}
                  type="linear"
                  dataKey={key}
                  stroke={METRIC_COLORS[key]}
                  strokeWidth={1.5}
                  dot={false}
                  activeDot={{
                    r: 4,
                    strokeWidth: 2,
                    stroke: "#fff",
                    fill: METRIC_COLORS[key],
                  }}
                  hide={hiddenSeries.has(key)}
                  connectNulls
                />
              ))}
            </LineChart>
          ) : (
            <BarChart
              data={data}
              margin={{ top: 4, right: 4, left: -16, bottom: 0 }}
              barCategoryGap="30%"
            >
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="displayDate" {...axisProps} />
              <YAxis {...axisProps} reversed tickFormatter={(v) => `#${v}`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                content={
                  <CustomLegend
                    hiddenSeries={hiddenSeries}
                    onToggle={toggleSeries}
                  />
                }
              />
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
