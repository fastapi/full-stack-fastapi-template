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
  type HistoricalTrendsResponse,
  type MetricStatistics,
  type TimeRange,
} from "@/clients/dashboard"
import {
  axisProps,
  CHART_COLORS,
  formatShortDate,
  gridProps,
  tooltipClasses,
} from "@/components/app/dashboard/components/chartTheme"
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
/**
 * Transform API response to chart-friendly format
 */
const transformDataForChart = (
  response: HistoricalTrendsResponse,
): ChartDataPoint[] => {
  return response.data_points.map((point) => ({
    date: point.date,
    displayDate: formatShortDate(point.date),
    awarenessScore: point.awareness_score,
    consistencyIndex: point.consistency_index,
  }))
}

interface BrandAwarenessScoreHistoricalViewProps {
  brandId?: string
  segment?: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

export function BrandAwarenessScoreHistoricalView({
  brandId,
  segment = "All-Segment",
  timeRange,
  customStartDate,
  customEndDate,
}: BrandAwarenessScoreHistoricalViewProps) {
  // ============================================================================
  // State Management
  // ============================================================================

  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [chartType, setChartType] = useState<"line" | "bar">("line")
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
   * Fetch historical trends data when time range or brand changes
   */
  useEffect(() => {
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) {
      return
    }

    const fetchHistoricalTrends = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const data = await dashboardAPI.getHistoricalTrends({
          timeRange,
          brandId,
          segment,
          startDate: customStartDate,
          endDate: customEndDate,
        })

        const chartPoints = transformDataForChart(data)
        setChartData(chartPoints)
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

    fetchHistoricalTrends()
  }, [timeRange, brandId, segment, customStartDate, customEndDate])

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
      const label =
        payload[0]?.payload?.displayDate ?? payload[0]?.payload?.date
      return (
        <div className={tooltipClasses.container}>
          <p className={tooltipClasses.label}>{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className={tooltipClasses.row}>
              <div className="flex items-center gap-1.5">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className={tooltipClasses.name}>
                  {entry.dataKey === "awarenessScore"
                    ? "Awareness Score"
                    : "Consistency Index"}
                </span>
              </div>
              <span className={tooltipClasses.value}>
                {entry.value.toFixed(2)}
              </span>
            </div>
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
            <div className="text-xs text-slate-500">Average</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.average.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Highest</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.highest.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Lowest</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.lowest.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Median</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.median.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Avg Growth</div>
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
      <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
        <h3 className="text-base font-semibold mb-4 text-slate-900">
          Historical Trends
        </h3>
        <div className="flex flex-col items-center justify-center h-96">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-sm text-slate-500">
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
      <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
        <h3 className="text-base font-semibold mb-4 text-slate-900">
          Historical Trends
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

  // ============================================================================
  // Main Render
  // ============================================================================

  return (
    <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
      <h3 className="text-base font-semibold mb-4 text-slate-900">
        Historical Trends
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

        {/* Error message for inline errors */}
        {error && chartData.length > 0 && (
          <div className="text-red-500 text-sm p-2 bg-red-50 rounded">
            {error}
          </div>
        )}

        {/* Chart Display */}
        <div className="w-full h-96 bg-white rounded-2xl border border-slate-200 p-4">
          {chartData.length === 0 ? (
            <div className="flex items-center justify-center h-full text-slate-500">
              No data available for the selected time range
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              {chartType === "line" ? (
                <LineChart data={chartData}>
                  <CartesianGrid {...gridProps} />
                  <XAxis dataKey="displayDate" {...axisProps} />
                  <YAxis
                    domain={[0, 10]}
                    {...axisProps}
                    label={{
                      value: "Score (0-10)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fontSize: "11px", fill: "#94a3b8" },
                    }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="awarenessScore"
                    stroke={CHART_COLORS.blue}
                    strokeWidth={3}
                    dot={{ fill: CHART_COLORS.blue, r: 4 }}
                    activeDot={{ r: 6 }}
                    name="Awareness Score"
                  />
                  <Line
                    type="monotone"
                    dataKey="consistencyIndex"
                    stroke={CHART_COLORS.purple}
                    strokeWidth={3}
                    dot={{ fill: CHART_COLORS.purple, r: 4 }}
                    activeDot={{ r: 6 }}
                    name="Consistency Index"
                  />
                </LineChart>
              ) : (
                <BarChart data={chartData}>
                  <CartesianGrid {...gridProps} />
                  <XAxis dataKey="displayDate" {...axisProps} />
                  <YAxis
                    domain={[0, 10]}
                    {...axisProps}
                    label={{
                      value: "Score (0-10)",
                      angle: -90,
                      position: "insideLeft",
                      style: { fontSize: "11px", fill: "#94a3b8" },
                    }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar
                    dataKey="awarenessScore"
                    fill={CHART_COLORS.blue}
                    name="Awareness Score"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="consistencyIndex"
                    fill={CHART_COLORS.purple}
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
