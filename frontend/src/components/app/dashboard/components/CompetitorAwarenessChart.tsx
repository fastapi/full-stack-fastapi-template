import { ChartColumnBig, ChartLine } from "lucide-react"
import { useState } from "react"
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
import type { CompetitorAwarenessDataPoint } from "@/clients/dashboard"
import {
  axisProps,
  CHART_COLORS,
  formatShortDate,
  gridProps,
  legendClasses,
  tooltipClasses,
} from "@/components/app/dashboard/components/chartTheme"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface CompetitorAwarenessChartProps {
  dataPoints: CompetitorAwarenessDataPoint[]
}

interface ChartDataPoint {
  date: string
  displayDate: string
  "Awareness Score": number
  "Share of Visibility": number
  "Search Share Index": number
  "Position Strength": number
  "Search Momentum": number
}

const METRIC_COLORS: Record<string, string> = {
  "Awareness Score": CHART_COLORS.blue,
  "Share of Visibility": CHART_COLORS.purple,
  "Search Share Index": CHART_COLORS.amber,
  "Position Strength": CHART_COLORS.green,
  "Search Momentum": CHART_COLORS.red,
}

function transformData(
  dataPoints: CompetitorAwarenessDataPoint[],
): ChartDataPoint[] {
  return dataPoints.map((point) => ({
    date: point.date,
    displayDate: formatShortDate(point.date),
    "Awareness Score": point.awareness_score,
    "Share of Visibility": +(point.share_of_visibility * 100).toFixed(1),
    "Search Share Index": +(point.search_share_index * 100).toFixed(1),
    "Position Strength": +(point.position_strength * 100).toFixed(1),
    "Search Momentum": +(point.search_momentum * 100).toFixed(1),
  }))
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null

  return (
    <div className={tooltipClasses.container}>
      <p className={tooltipClasses.label}>{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className={tooltipClasses.row}>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className={tooltipClasses.name}>{entry.name}</span>
          </div>
          <span className={tooltipClasses.value}>{entry.value}</span>
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
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className={legendClasses.label}>{entry.value}</span>
          </button>
        )
      })}
    </div>
  )
}

export function CompetitorAwarenessChart({
  dataPoints,
}: CompetitorAwarenessChartProps) {
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set())

  const chartData = transformData(dataPoints)

  const toggleSeries = (name: string) => {
    setHiddenSeries((prev) => {
      const next = new Set(prev)
      if (next.has(name)) {
        next.delete(name)
      } else {
        next.add(name)
      }
      return next
    })
  }

  const metricKeys = Object.keys(METRIC_COLORS)

  if (chartData.length === 0) {
    return (
      <div className="w-full h-96 bg-white rounded-2xl border border-slate-200 flex items-center justify-center">
        <p className="text-slate-500">
          No data available for the selected time range
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Chart type toggle */}
      <div className="flex justify-end">
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

      <div className="w-full h-96 bg-white rounded-2xl border border-slate-200 p-4">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "line" ? (
            <LineChart data={chartData}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="displayDate" {...axisProps} />
              <YAxis
                {...axisProps}
                domain={[0, 100]}
                label={{
                  value: "Score",
                  angle: -90,
                  position: "insideLeft",
                  style: { fontSize: "11px", fill: "#94a3b8" },
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
              {metricKeys.map((key) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={METRIC_COLORS[key]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                  hide={hiddenSeries.has(key)}
                />
              ))}
            </LineChart>
          ) : (
            <BarChart data={chartData}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="displayDate" {...axisProps} />
              <YAxis
                {...axisProps}
                domain={[0, 100]}
                label={{
                  value: "Score",
                  angle: -90,
                  position: "insideLeft",
                  style: { fontSize: "11px", fill: "#94a3b8" },
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
              {metricKeys.map((key) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={METRIC_COLORS[key]}
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
