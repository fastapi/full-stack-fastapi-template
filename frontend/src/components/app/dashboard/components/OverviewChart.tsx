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
import type { BrandOverviewDataPoint } from "@/clients/dashboard"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface OverviewChartProps {
  dataPoints: BrandOverviewDataPoint[]
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
  "Awareness Score": "#3b82f6",
  "Share of Visibility": "#8b5cf6",
  "Search Share Index": "#f97316",
  "Position Strength": "#22c55e",
  "Search Momentum": "#ec4899",
}

const formatDateForDisplay = (isoDate: string): string => {
  const date = new Date(isoDate)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function transformData(dataPoints: BrandOverviewDataPoint[]): ChartDataPoint[] {
  return dataPoints.map((point) => ({
    date: point.date,
    displayDate: formatDateForDisplay(point.date),
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
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-gray-700 mb-2">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2 text-sm">
          <span
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-gray-600">{entry.name}:</span>
          <span className="font-medium">{entry.value}</span>
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

export function OverviewChart({ dataPoints }: OverviewChartProps) {
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
      <div className="w-full h-96 bg-gray-50 rounded-lg flex items-center justify-center">
        <p className="text-slate-500">No data available for the selected time range</p>
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
                tick={{ fontSize: 12, fill: "#64748b" }}
                domain={[0, 100]}
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
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="displayDate"
                tick={{ fontSize: 12, fill: "#64748b" }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: "#64748b" }}
                domain={[0, 100]}
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
