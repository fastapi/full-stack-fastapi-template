/**
 * BrandAwarenessScoreHistoricalView Component
 *
 * Displays historical trends for brand awareness score and consistency index.
 * Features:
 * - Time range selection (1 Month, 1 Quarter, 1 Year, YTD, Custom)
 * - Line and Bar chart visualizations
 * - Statistical summaries for both metrics
 * - Data caching with 10-hour expiration
 */

import { Calendar, ChartColumnBig, ChartLine, Loader2 } from "lucide-react"
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
  type HistoricalTrendsResponse,
  type MetricStatistics,
  type TimeRange,
} from "@/clients/dashboard"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

/**
 * Chart data point format for Recharts
 */
interface ChartDataPoint {
  date: string
  displayDate: string
  awarenessScore: number
  consistencyIndex: number
}

/**
 * Format ISO date string to display format (MM/DD)
 */
const formatDateForDisplay = (isoDate: string): string => {
  const date = new Date(isoDate)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

/**
 * Transform API response to chart-friendly format
 */
const transformDataForChart = (
  response: HistoricalTrendsResponse,
): ChartDataPoint[] => {
  return response.data_points.map((point) => ({
    date: point.date,
    displayDate: formatDateForDisplay(point.date),
    awarenessScore: point.awareness_score,
    consistencyIndex: point.consistency_index,
  }))
}

export function BrandAwarenessScoreHistoricalView() {
  // ============================================================================
  // State Management
  // ============================================================================

  const [customDateRange, setCustomDateRange] = useState({
    start: "",
    end: "",
  })
  const [showCustomDate, setShowCustomDate] = useState(false)
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [timeRange, setTimeRange] = useState<TimeRange>("1month")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [awarenessStats, setAwarenessStats] = useState<MetricStatistics | null>(
    null,
  )
  const [consistencyStats, setConsistencyStats] =
    useState<MetricStatistics | null>(null)

  // ============================================================================
  // Data Fetching
  // ============================================================================

  /**
   * Fetch historical trends data when time range changes
   */
  useEffect(() => {
    const fetchHistoricalTrends = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const data = await dashboardAPI.getHistoricalTrends({
          timeRange,
        })

        // Transform data for chart
        const chartPoints = transformDataForChart(data)
        setChartData(chartPoints)

        // Set statistics
        setAwarenessStats(data.awareness_stats)
        setConsistencyStats(data.consistency_stats)

        console.log("[HistoricalView] Data loaded:", {
          points: chartPoints.length,
          awarenessStats: data.awareness_stats,
          consistencyStats: data.consistency_stats,
        })
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to load historical trends"
        setError(errorMessage)
        console.error("[HistoricalView] Error:", err)
      } finally {
        setIsLoading(false)
      }
    }

    // Only fetch for preset time ranges
    if (timeRange !== "custom") {
      fetchHistoricalTrends()
    }
  }, [timeRange])

  /**
   * Handle custom date range submission
   */
  const handleCustomDateApply = async () => {
    if (!customDateRange.start || !customDateRange.end) {
      setError("Please select both start and end dates")
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const data = await dashboardAPI.getHistoricalTrends({
        timeRange: "custom",
        startDate: customDateRange.start,
        endDate: customDateRange.end,
      })

      const chartPoints = transformDataForChart(data)
      setChartData(chartPoints)
      setAwarenessStats(data.awareness_stats)
      setConsistencyStats(data.consistency_stats)

      console.log(
        "[HistoricalView] Custom range data loaded:",
        chartPoints.length,
      )
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load historical trends"
      setError(errorMessage)
      console.error("[HistoricalView] Error:", err)
    } finally {
      setIsLoading(false)
    }
  }

  // ============================================================================
  // Custom Tooltip Component
  // ============================================================================

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
              {entry.dataKey === "awarenessScore"
                ? "Awareness Score"
                : "Consistency Index"}
              : <span className="font-bold">{entry.value.toFixed(2)}</span>
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  // ============================================================================
  // Statistics Display Component
  // ============================================================================

  const StatisticsRow = ({
    title,
    stats,
    color,
  }: {
    title: string
    stats: MetricStatistics | null
    color: string
  }) => {
    if (!stats) return null

    return (
      <div className="mt-4">
        <h4 className={`text-sm font-semibold mb-2 ${color}`}>{title}</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <div>
            <div className="text-xs text-gray-500">Average</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.average.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Highest</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.highest.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Lowest</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.lowest.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Median</div>
            <div className="text-lg font-bold text-gray-600">
              {stats.median.toFixed(2)}
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

  // ============================================================================
  // Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
        <h3 className="text-md font-semibold mb-4">Historical Trends</h3>
        <div className="flex flex-col items-center justify-center h-96">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-sm text-gray-500">
            Loading historical trends...
          </p>
        </div>
      </div>
    )
  }

  // ============================================================================
  // Error State
  // ============================================================================

  if (error && chartData.length === 0) {
    return (
      <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
        <h3 className="text-md font-semibold mb-4">Historical Trends</h3>
        <div className="flex flex-col items-center justify-center h-96">
          <div className="text-red-500 text-center">
            <p className="font-medium">Failed to load data</p>
            <p className="text-sm mt-2">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  // ============================================================================
  // Main Render
  // ============================================================================

  return (
    <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
      <h3 className="text-md font-semibold mb-4">Historical Trends</h3>

      {/* Time Range Selection */}
      <div className="space-y-4 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <Tabs
            value={showCustomDate ? "custom" : timeRange}
            onValueChange={(value) => {
              if (value === "custom") {
                setShowCustomDate(true)
              } else {
                setTimeRange(value as TimeRange)
                setShowCustomDate(false)
              }
            }}
          >
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="1month">1M</TabsTrigger>
              <TabsTrigger value="1quarter">1Q</TabsTrigger>
              <TabsTrigger value="1year">1Y</TabsTrigger>
              <TabsTrigger value="ytd">YTD</TabsTrigger>
            </TabsList>
          </Tabs>
          <Button
            variant={showCustomDate ? "default" : "outline"}
            onClick={() => setShowCustomDate(!showCustomDate)}
            size="sm"
            type="button"
          >
            <Calendar className="h-4 w-4 mr-2" />
            Custom Range
          </Button>

          {/* Chart Type Selection */}
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

        {/* Custom Date Range Inputs */}
        {showCustomDate && (
          <div className="flex gap-3 items-center p-4 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-700 block mb-1">
                Start Date
              </label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={customDateRange.start}
                onChange={(e) =>
                  setCustomDateRange({
                    ...customDateRange,
                    start: e.target.value,
                  })
                }
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-700 block mb-1">
                End Date
              </label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={customDateRange.end}
                onChange={(e) =>
                  setCustomDateRange({
                    ...customDateRange,
                    end: e.target.value,
                  })
                }
              />
            </div>
            <Button
              className="self-end"
              onClick={handleCustomDateApply}
              type="button"
            >
              Apply
            </Button>
          </div>
        )}

        {/* Error message for inline errors */}
        {error && chartData.length > 0 && (
          <div className="text-red-500 text-sm p-2 bg-red-50 rounded">
            {error}
          </div>
        )}

        {/* Chart Display */}
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
                    domain={[0, 10]}
                    stroke="#6b7280"
                    style={{ fontSize: "12px" }}
                    label={{
                      value: "Score (0-10)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fontSize: "12px" },
                    }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="awarenessScore"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: "#3b82f6", r: 4 }}
                    activeDot={{ r: 6 }}
                    name="Awareness Score"
                  />
                  <Line
                    type="monotone"
                    dataKey="consistencyIndex"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={{ fill: "#8b5cf6", r: 4 }}
                    activeDot={{ r: 6 }}
                    name="Consistency Index"
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
                    domain={[0, 10]}
                    stroke="#6b7280"
                    style={{ fontSize: "12px" }}
                    label={{
                      value: "Score (0-10)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fontSize: "12px" },
                    }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar
                    dataKey="awarenessScore"
                    fill="#3b82f6"
                    name="Awareness Score"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="consistencyIndex"
                    fill="#8b5cf6"
                    name="Consistency Index"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              )}
            </ResponsiveContainer>
          )}
        </div>

        {/* Statistics Summary */}
        <div className="border-t pt-4 mt-4">
          <StatisticsRow
            title="Brand Awareness Score Statistics"
            stats={awarenessStats}
            color="text-blue-600"
          />
          <StatisticsRow
            title="Brand Stability Index Statistics"
            stats={consistencyStats}
            color="text-purple-600"
          />
        </div>
      </div>
    </div>
  )
}
