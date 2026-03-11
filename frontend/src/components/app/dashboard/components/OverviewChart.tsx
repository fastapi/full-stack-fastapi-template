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
import type { BrandImpressionTrendDataPoint } from "@/clients/dashboard"
import {
  axisProps,
  CHART_COLORS,
  formatShortDate,
  gridProps,
  legendClasses,
  tooltipClasses,
} from "@/components/app/dashboard/components/chartTheme"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface OverviewChartProps {
  dataPoints: BrandImpressionTrendDataPoint[]
}

interface ChartDataPoint {
  date: string
  displayDate: string
  "Visibility (%)": number | null
  "Position (#)": number | null
  Sentiment: number | null
}

const METRIC_COLORS: Record<string, string> = {
  "Visibility (%)": CHART_COLORS.blue,
  "Position (#)": CHART_COLORS.purple,
  Sentiment: CHART_COLORS.green,
}

// Units shown in the tooltip per metric key
const METRIC_UNITS: Record<string, string> = {
  "Visibility (%)": "%",
  "Position (#)": "",
  Sentiment: "",
}

// Prefix shown before the value in the tooltip
const METRIC_PREFIX: Record<string, string> = {
  "Visibility (%)": "",
  "Position (#)": "#",
  Sentiment: "",
}

function transformData(
  dataPoints: BrandImpressionTrendDataPoint[],
): ChartDataPoint[] {
  return dataPoints.map((point) => ({
    date: point.date,
    displayDate: formatShortDate(point.date),
    "Visibility (%)":
      point.visibility !== null ? +point.visibility.toFixed(1) : null,
    "Position (#)": point.position !== null ? +point.position.toFixed(1) : null,
    Sentiment: point.sentiment !== null ? +point.sentiment.toFixed(1) : null,
  }))
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null
  return (
    <div className={tooltipClasses.container}>
      <p className={tooltipClasses.label}>{label}</p>
      {payload.map((entry: any) => {
        if (entry.value === null || entry.value === undefined) return null
        const prefix = METRIC_PREFIX[entry.name] ?? ""
        const unit = METRIC_UNITS[entry.name] ?? ""
        return (
          <div key={entry.name} className={tooltipClasses.row}>
            <div className="flex items-center gap-1.5">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: entry.color }}
              />
              <span className={tooltipClasses.name}>{entry.name}</span>
            </div>
            <span className={tooltipClasses.value}>
              {prefix}
              {entry.value}
              {unit}
            </span>
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
    </div>
  )
}

export function OverviewChart({ dataPoints }: OverviewChartProps) {
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set())

  const chartData = transformData(dataPoints)
  const metricKeys = Object.keys(METRIC_COLORS)

  const toggleSeries = (name: string) => {
    setHiddenSeries((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  if (chartData.length === 0) {
    return (
      <div className="w-full h-80 flex items-center justify-center text-slate-400 text-sm">
        No data available for the selected time range
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Chart type toggle */}
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

      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "line" ? (
            <LineChart
              data={chartData}
              margin={{ top: 4, right: 4, left: -16, bottom: 0 }}
            >
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="displayDate" {...axisProps} />
              <YAxis {...axisProps} />
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
                  dot={false}
                  connectNulls={false}
                  activeDot={{
                    r: 4,
                    strokeWidth: 2,
                    stroke: "#fff",
                    fill: METRIC_COLORS[key],
                  }}
                  hide={hiddenSeries.has(key)}
                />
              ))}
            </LineChart>
          ) : (
            <BarChart
              data={chartData}
              margin={{ top: 4, right: 4, left: -16, bottom: 0 }}
              barCategoryGap="30%"
            >
              <CartesianGrid {...gridProps} />
              <XAxis dataKey="displayDate" {...axisProps} />
              <YAxis {...axisProps} />
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
