/**
 * DetailMetricsView Component
 *
 * Displays historical trends for brand visibility rate and ranking.
 * Features:
 * - Time range selection (1 Month, 1 Quarter, 1 Year, YTD, Custom)
 * - Line and Bar chart visualizations
 * - Dual Y-axis: visibility (left, %), ranking (right, inverted)
 * - Click legend to toggle individual metrics
 * - Statistical summaries for both metrics
 */

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
  dashboardAPI,
  type DetailMetricsResponse,
  type MetricStatistics,
  type TimeRange,
} from "@/clients/dashboard"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface ChartDataPoint {
  date: string
  displayDate: string
  visibilityRate: number
  avgRanking: number
}

const formatDateForDisplay = (isoDate: string): string => {
  const date = new Date(isoDate)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const transformDataForChart = (
  response: DetailMetricsResponse,
): ChartDataPoint[] => {
  return response.data_points.map((point) => ({
    date: point.date,
    displayDate: formatDateForDisplay(point.date),
    visibilityRate: point.visibility_rate,
    avgRanking: point.avg_ranking,
  }))
}

interface DetailMetricsViewProps {
  brandId: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

export function DetailMetricsView({
  brandId,
  timeRange,
  customStartDate,
  customEndDate,
}: DetailMetricsViewProps) {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [visibilityStats, setVisibilityStats] =
    useState<MetricStatistics | null>(null)
  const [rankingStats, setRankingStats] = useState<MetricStatistics | null>(
    null,
  )
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) {
      return
    }

    const fetchDetailMetrics = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const data = await dashboardAPI.getDetailMetrics({
          timeRange,
          brandId,
          startDate: customStartDate,
          endDate: customEndDate,
        })

        const chartPoints = transformDataForChart(data)
        setChartData(chartPoints)
        setVisibilityStats(data.visibility_stats)
        setRankingStats(data.ranking_stats)

        console.log("[DetailMetrics] Data loaded:", {
          points: chartPoints.length,
        })
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to load detail metrics"
        setError(errorMessage)
        console.error("[DetailMetrics] Error:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDetailMetrics()
  }, [timeRange, brandId, customStartDate, customEndDate])

  const handleLegendClick = (dataKey: string) => {
    setHiddenSeries((prev) => {
      const next = new Set(prev)
      if (next.has(dataKey)) {
        next.delete(dataKey)
      } else {
        next.add(dataKey)
      }
      return next
    })
  }

  // Compute max ranking for Y-axis domain
  const maxRanking = chartData.length > 0
    ? Math.ceil(Math.max(...chartData.map((d) => d.avgRanking), 1))
    : 10

  const CustomTooltip = ({
    active,
    payload,
  }: {
    active?: boolean
    payload?: Array<{
      value: number
      dataKey: string
      color: string
      payload: ChartDataPoint
    }>
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium mb-2">{payload[0].payload.date}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.dataKey === "visibilityRate"
                ? "Visibility Rate"
                : "Avg Ranking"}
              :{" "}
              <span className="font-bold">
                {entry.dataKey === "visibilityRate"
                  ? `${entry.value.toFixed(1)}%`
                  : entry.value.toFixed(1)}
              </span>
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  const legendItems = [
    { dataKey: "visibilityRate", label: "Visibility Rate", color: "#3b82f6" },
    { dataKey: "avgRanking", label: "Avg Ranking", color: "#f97316" },
  ]

  const CustomLegend = () => {
    return (
      <div className="flex justify-center gap-6 mt-2">
        {legendItems.map((item) => {
          const isHidden = hiddenSeries.has(item.dataKey)
          return (
            <button
              key={item.dataKey}
              type="button"
              className="flex items-center gap-2 text-sm cursor-pointer transition-colors"
              onClick={() => handleLegendClick(item.dataKey)}
            >
              <span
                className="inline-block w-3 h-3 rounded-full"
                style={{ backgroundColor: isHidden ? "#d1d5db" : item.color }}
              />
              <span style={{ color: isHidden ? "#9ca3af" : "#374151" }}>
                {item.label}
              </span>
            </button>
          )
        })}
      </div>
    )
  }

  const StatisticsRow = ({
    title,
    stats,
    color,
    unit,
  }: {
    title: string
    stats: MetricStatistics | null
    color: string
    unit?: string
  }) => {
    if (!stats) return null
    const suffix = unit || ""

    return (
      <div className="mt-4">
        <h4 className={`text-sm font-semibold mb-2 ${color}`}>{title}</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <div>
            <div className="text-xs text-gray-500">Average</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.average.toFixed(2)}{suffix}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Highest</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.highest.toFixed(2)}{suffix}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Lowest</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.lowest.toFixed(2)}{suffix}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Median</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.median.toFixed(2)}{suffix}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Avg Growth</div>
            <div
              className={`text-lg font-bold ${
                stats.average_growth >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {stats.average_growth >= 0 ? "+" : ""}
              {stats.average_growth.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
        <h3 className="text-md font-semibold mb-4">
          Visibility &amp; Ranking Trends
        </h3>
        <div className="flex flex-col items-center justify-center h-96">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-sm text-gray-500">
            Loading detail metrics...
          </p>
        </div>
      </div>
    )
  }

  if (error && chartData.length === 0) {
    return (
      <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
        <h3 className="text-md font-semibold mb-4">
          Visibility &amp; Ranking Trends
        </h3>
        <div className="flex flex-col items-center justify-center h-96">
          <div className="text-red-500 text-center">
            <p className="font-medium">Failed to load data</p>
            <p className="text-sm mt-2">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  const showVisibility = !hiddenSeries.has("visibilityRate")
  const showRanking = !hiddenSeries.has("avgRanking")

  return (
    <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
      <h3 className="text-md font-semibold mb-4">
        Visibility &amp; Ranking Trends
      </h3>

      <div className="space-y-4 mb-6">
        {/* Chart Type Selection */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="ml-auto">
            <Tabs
              value={chartType}
              onValueChange={(value) => setChartType(value as "line" | "bar")}
            >
              <TabsList className="bg-transparent rounded-none border-b w-full justify-start h-auto p-0">
                <TabsTrigger
                  value="line"
                  className="bg-transparent rounded-none shadow-none px-4 py-2
                    data-[state=active]:bg-transparent data-[state=active]:shadow-none
                    border-b-2 border-transparent data-[state=active]:border-primary"
                >
                  <ChartLine className="h-4 w-4 mr-2" />
                  Line
                </TabsTrigger>
                <TabsTrigger
                  value="bar"
                  className="bg-transparent rounded-none shadow-none px-4 py-2
                    data-[state=active]:bg-transparent data-[state=active]:shadow-none
                    border-b-2 border-transparent data-[state=active]:border-primary"
                >
                  <ChartColumnBig className="h-4 w-4 mr-2" />
                  Bar
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>

        {/* Inline error */}
        {error && chartData.length > 0 && (
          <div className="text-red-500 text-sm p-2 bg-red-50 rounded">
            {error}
          </div>
        )}

        {/* Chart */}
        <div className="w-full h-96 bg-gray-50 rounded-lg p-4">
          {chartData.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              No data available for the selected time range
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              {chartType === "line" ? (
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="displayDate"
                    stroke="#6b7280"
                    style={{ fontSize: "12px" }}
                  />
                  <YAxis
                    yAxisId="left"
                    domain={[0, 100]}
                    stroke="#3b82f6"
                    style={{ fontSize: "12px" }}
                    label={{
                      value: "Visibility (%)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fontSize: "12px", fill: "#3b82f6" },
                    }}
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    domain={[1, maxRanking + 1]}
                    reversed
                    stroke="#f97316"
                    style={{ fontSize: "12px" }}
                    label={{
                      value: "Ranking",
                      angle: 90,
                      position: "insideRight",
                      style: { fontSize: "12px", fill: "#f97316" },
                    }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend content={<CustomLegend />} />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="visibilityRate"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: "#3b82f6", r: 3 }}
                    activeDot={{ r: 5 }}
                    name="Visibility Rate"
                    hide={!showVisibility}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="avgRanking"
                    stroke="#f97316"
                    strokeWidth={3}
                    dot={{ fill: "#f97316", r: 3 }}
                    activeDot={{ r: 5 }}
                    name="Avg Ranking"
                    hide={!showRanking}
                  />
                </LineChart>
              ) : (
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="displayDate"
                    stroke="#6b7280"
                    style={{ fontSize: "12px" }}
                  />
                  <YAxis
                    yAxisId="left"
                    domain={[0, 100]}
                    stroke="#3b82f6"
                    style={{ fontSize: "12px" }}
                    label={{
                      value: "Visibility (%)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fontSize: "12px", fill: "#3b82f6" },
                    }}
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    domain={[1, maxRanking + 1]}
                    reversed
                    stroke="#f97316"
                    style={{ fontSize: "12px" }}
                    label={{
                      value: "Ranking",
                      angle: 90,
                      position: "insideRight",
                      style: { fontSize: "12px", fill: "#f97316" },
                    }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend content={<CustomLegend />} />
                  <Bar
                    yAxisId="left"
                    dataKey="visibilityRate"
                    fill="#3b82f6"
                    name="Visibility Rate"
                    radius={[4, 4, 0, 0]}
                    hide={!showVisibility}
                  />
                  <Bar
                    yAxisId="right"
                    dataKey="avgRanking"
                    fill="#f97316"
                    name="Avg Ranking"
                    radius={[4, 4, 0, 0]}
                    hide={!showRanking}
                  />
                </BarChart>
              )}
            </ResponsiveContainer>
          )}
        </div>

        {/* Statistics Summary */}
        <div className="border-t pt-4 mt-4">
          <StatisticsRow
            title="Visibility Rate Statistics"
            stats={visibilityStats}
            color="text-blue-600"
            unit="%"
          />
          <StatisticsRow
            title="Ranking Statistics"
            stats={rankingStats}
            color="text-orange-600"
          />
        </div>
      </div>
    </div>
  )
}
