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
  "Awareness Score": "#6366f1",
  "Share of Visibility": "#f43f5e",
  "Search Share Index": "#f59e0b",
  "Position Strength": "#10b981",
  "Search Momentum": "#06b6d4",
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
    <div className="bg-white border border-gray-100 rounded-xl shadow-xl p-3 min-w-[160px]">
      <p className="text-[10px] font-semibold text-gray-500 mb-2 uppercase tracking-wide">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center justify-between gap-4 text-[10px] py-0.5">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }} />
            <span className="text-gray-500">{entry.name}</span>
          </div>
          <span className="font-semibold text-gray-800">{entry.value}</span>
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
    <div className="flex flex-wrap justify-center gap-2 mt-2">
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
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
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

  const commonAxisProps = {
    tick: { fontSize: 10, fill: "#94a3b8" },
    axisLine: false,
    tickLine: false,
  }

  return (
    <div className="space-y-3">
      {/* Chart type toggle */}
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

      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === "line" ? (
            <LineChart data={chartData} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="displayDate" {...commonAxisProps} />
              <YAxis {...commonAxisProps} domain={[0, 100]} />
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend hiddenSeries={hiddenSeries} onToggle={toggleSeries} />} />
              {metricKeys.map((key) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={METRIC_COLORS[key]}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 2, stroke: "#fff", fill: METRIC_COLORS[key] }}
                  hide={hiddenSeries.has(key)}
                />
              ))}
            </LineChart>
          ) : (
            <BarChart data={chartData} margin={{ top: 4, right: 4, left: -16, bottom: 0 }} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="displayDate" {...commonAxisProps} />
              <YAxis {...commonAxisProps} domain={[0, 100]} />
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend hiddenSeries={hiddenSeries} onToggle={toggleSeries} />} />
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
