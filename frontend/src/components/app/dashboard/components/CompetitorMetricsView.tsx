/**
 * CompetitorMetricsView Component
 *
 * Displays competitor visibility rate and ranking score trends.
 * Features:
 * - Segment selector dropdown to filter by segment
 * - Dropdown to select a competitor brand
 * - Line and Bar chart visualizations
 * - Dual Y-axis: visibility (left, %), ranking score (right, 0-10)
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
  type BrandSegmentsResponse,
  type CompetitorBrand,
  type CompetitorMetricsResponse,
  dashboardAPI,
  type MetricStatistics,
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface ChartDataPoint {
  date: string
  displayDate: string
  visibilityRate: number
  avgRanking: number
}

const transformDataForChart = (
  response: CompetitorMetricsResponse,
): ChartDataPoint[] => {
  return response.data_points.map((point) => ({
    date: point.date,
    displayDate: formatShortDate(point.date),
    visibilityRate: point.visibility_rate,
    avgRanking: point.avg_ranking,
  }))
}

interface CompetitorMetricsViewProps {
  brandId: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

export function CompetitorMetricsView({
  brandId,
  timeRange,
  customStartDate,
  customEndDate,
}: CompetitorMetricsViewProps) {
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null)
  const [isLoadingSegments, setIsLoadingSegments] = useState(false)

  const [competitors, setCompetitors] = useState<CompetitorBrand[]>([])
  const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(
    null,
  )
  const [isLoadingCompetitors, setIsLoadingCompetitors] = useState(true)
  const [competitorsError, setCompetitorsError] = useState<string | null>(null)

  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [chartType, setChartType] = useState<"line" | "bar">("line")
  const [isLoadingMetrics, setIsLoadingMetrics] = useState(false)
  const [metricsError, setMetricsError] = useState<string | null>(null)
  const [visibilityStats, setVisibilityStats] =
    useState<MetricStatistics | null>(null)
  const [rankingStats, setRankingStats] = useState<MetricStatistics | null>(
    null,
  )
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set())

  // Fetch segments when brandId changes
  useEffect(() => {
    if (!brandId) {
      setSegments([])
      setSelectedSegment(null)
      return
    }

    const fetchSegments = async () => {
      try {
        setIsLoadingSegments(true)
        const data: BrandSegmentsResponse =
          await dashboardAPI.getBrandSegments(brandId)
        setSegments(data.segments)
        if (data.segments.length > 0) {
          setSelectedSegment(data.segments[0])
        } else {
          setSelectedSegment(null)
        }
      } catch (err) {
        console.error("[CompetitorMetrics] Error fetching segments:", err)
        setSegments([])
        setSelectedSegment(null)
      } finally {
        setIsLoadingSegments(false)
      }
    }

    fetchSegments()
  }, [brandId])

  // Fetch competitors when brandId changes
  useEffect(() => {
    const fetchCompetitors = async () => {
      try {
        setIsLoadingCompetitors(true)
        setCompetitorsError(null)
        setSelectedCompetitor(null)
        setChartData([])

        const data = await dashboardAPI.getCompetitors(brandId)
        setCompetitors(data.competitors)

        // Auto-select the first competitor
        if (data.competitors.length > 0) {
          setSelectedCompetitor(data.competitors[0].competitor_brand_name)
        }

        console.log("[CompetitorMetrics] Loaded competitors:", data.total_count)
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load competitors"
        setCompetitorsError(errorMessage)
        console.error("[CompetitorMetrics] Error loading competitors:", err)
      } finally {
        setIsLoadingCompetitors(false)
      }
    }

    fetchCompetitors()
  }, [brandId])

  // Fetch metrics when competitor, segment, or time range changes
  useEffect(() => {
    if (!selectedCompetitor) return
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) return

    const fetchMetrics = async () => {
      try {
        setIsLoadingMetrics(true)
        setMetricsError(null)

        const data = await dashboardAPI.getCompetitorMetrics({
          brandId,
          competitorBrandName: selectedCompetitor,
          timeRange,
          startDate: customStartDate,
          endDate: customEndDate,
          segment: selectedSegment || undefined,
        })

        const chartPoints = transformDataForChart(data)
        setChartData(chartPoints)
        setVisibilityStats(data.visibility_stats)
        setRankingStats(data.ranking_stats)

        console.log("[CompetitorMetrics] Data loaded:", {
          points: chartPoints.length,
        })
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to load competitor metrics"
        setMetricsError(errorMessage)
        console.error("[CompetitorMetrics] Error:", err)
      } finally {
        setIsLoadingMetrics(false)
      }
    }

    fetchMetrics()
  }, [
    selectedCompetitor,
    selectedSegment,
    timeRange,
    brandId,
    customStartDate,
    customEndDate,
  ])

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
                  {entry.dataKey === "visibilityRate"
                    ? "Visibility Rate"
                    : "Ranking Score"}
                </span>
              </div>
              <span className={tooltipClasses.value}>
                {entry.dataKey === "visibilityRate"
                  ? `${entry.value.toFixed(1)}%`
                  : entry.value.toFixed(1)}
              </span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  const legendItems = [
    {
      dataKey: "visibilityRate",
      label: "Visibility Rate",
      color: CHART_COLORS.blue,
    },
    {
      dataKey: "avgRanking",
      label: "Ranking Score",
      color: CHART_COLORS.purple,
    },
  ]

  const CustomLegend = () => {
    return (
      <div className={legendClasses.container}>
        {legendItems.map((item) => {
          const isHidden = hiddenSeries.has(item.dataKey)
          return (
            <button
              key={item.dataKey}
              type="button"
              className={legendClasses.item}
              onClick={() => handleLegendClick(item.dataKey)}
            >
              <span
                className="inline-block w-2 h-2 rounded-full"
                style={{ backgroundColor: isHidden ? "#cbd5f5" : item.color }}
              />
              <span
                className={legendClasses.label}
                style={{ opacity: isHidden ? 0.5 : 1 }}
              >
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
            <div className="text-xs text-slate-500">Average</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.average.toFixed(2)}
              {suffix}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Highest</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.highest.toFixed(2)}
              {suffix}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Lowest</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.lowest.toFixed(2)}
              {suffix}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Median</div>
            <div className="text-lg font-bold text-slate-700">
              {stats.median.toFixed(2)}
              {suffix}
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

  const showVisibility = !hiddenSeries.has("visibilityRate")
  const showRanking = !hiddenSeries.has("avgRanking")

  return (
    <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
      <h3 className="text-base font-semibold mb-4 text-slate-900">
        Competitor Visibility &amp; Ranking Trends
      </h3>

      {/* Segment & Competitor Selectors */}
      <div className="flex flex-wrap items-center gap-6 mb-6">
        {/* Segment Selector */}
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-slate-700">Segment:</span>
          {isLoadingSegments ? (
            <div className="flex items-center gap-2 text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Loading...</span>
            </div>
          ) : segments.length > 0 ? (
            <Select
              value={selectedSegment || undefined}
              onValueChange={setSelectedSegment}
            >
              <SelectTrigger className="w-[300px]">
                <SelectValue placeholder="Select a segment" />
              </SelectTrigger>
              <SelectContent>
                {segments.map((seg) => (
                  <SelectItem key={seg} value={seg}>
                    {seg}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <span className="text-sm text-slate-500">
              No segments available
            </span>
          )}
        </div>

        {/* Competitor Selector */}
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-slate-700">
            Competitor:
          </span>
          {isLoadingCompetitors ? (
            <div className="flex items-center gap-2 text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Loading...</span>
            </div>
          ) : competitorsError ? (
            <div className="text-red-500 text-sm">{competitorsError}</div>
          ) : competitors.length === 0 ? (
            <span className="text-sm text-slate-500">No competitors found</span>
          ) : (
            <Select
              value={selectedCompetitor || undefined}
              onValueChange={setSelectedCompetitor}
            >
              <SelectTrigger className="w-[300px]">
                <SelectValue placeholder="Select a competitor" />
              </SelectTrigger>
              <SelectContent>
                {competitors.map((comp) => (
                  <SelectItem
                    key={comp.competitor_brand_name}
                    value={comp.competitor_brand_name}
                  >
                    {comp.competitor_brand_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </div>

      {/* Loading state for metrics */}
      {isLoadingMetrics && (
        <div className="flex flex-col items-center justify-center h-96">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-sm text-slate-500">
            Loading competitor metrics...
          </p>
        </div>
      )}

      {/* Error state for metrics */}
      {!isLoadingMetrics &&
        metricsError &&
        chartData.length === 0 &&
        selectedCompetitor && (
          <div className="flex flex-col items-center justify-center h-96">
            <div className="text-red-500 text-center">
              <p className="font-medium">Failed to load data</p>
              <p className="text-sm mt-2">{metricsError}</p>
            </div>
          </div>
        )}

      {/* Chart and stats - show when we have a selected competitor and not loading */}
      {!isLoadingMetrics && selectedCompetitor && (
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
          {metricsError && chartData.length > 0 && (
            <div className="text-red-500 text-sm p-2 bg-red-50 rounded">
              {metricsError}
            </div>
          )}

          {/* Chart */}
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
                      yAxisId="left"
                      domain={[0, 100]}
                      stroke={CHART_COLORS.blue}
                      {...axisProps}
                      label={{
                        value: "Visibility (%)",
                        angle: -90,
                        position: "insideLeft",
                        style: { fontSize: "11px", fill: CHART_COLORS.blue },
                      }}
                    />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      domain={[0, 10]}
                      stroke={CHART_COLORS.purple}
                      {...axisProps}
                      label={{
                        value: "Ranking Score (0-10)",
                        angle: 90,
                        position: "insideRight",
                        style: { fontSize: "11px", fill: CHART_COLORS.purple },
                      }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend content={<CustomLegend />} />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="visibilityRate"
                      stroke={CHART_COLORS.blue}
                      strokeWidth={3}
                      dot={{ fill: CHART_COLORS.blue, r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Visibility Rate"
                      hide={!showVisibility}
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="avgRanking"
                      stroke={CHART_COLORS.purple}
                      strokeWidth={3}
                      dot={{ fill: CHART_COLORS.purple, r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Ranking Score"
                      hide={!showRanking}
                    />
                  </LineChart>
                ) : (
                  <BarChart data={chartData}>
                    <CartesianGrid {...gridProps} />
                    <XAxis dataKey="displayDate" {...axisProps} />
                    <YAxis
                      yAxisId="left"
                      domain={[0, 100]}
                      stroke={CHART_COLORS.blue}
                      {...axisProps}
                      label={{
                        value: "Visibility (%)",
                        angle: -90,
                        position: "insideLeft",
                        style: { fontSize: "11px", fill: CHART_COLORS.blue },
                      }}
                    />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      domain={[0, 10]}
                      stroke={CHART_COLORS.purple}
                      {...axisProps}
                      label={{
                        value: "Ranking Score (0-10)",
                        angle: 90,
                        position: "insideRight",
                        style: { fontSize: "11px", fill: CHART_COLORS.purple },
                      }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend content={<CustomLegend />} />
                    <Bar
                      yAxisId="left"
                      dataKey="visibilityRate"
                      fill={CHART_COLORS.blue}
                      name="Visibility Rate"
                      radius={[4, 4, 0, 0]}
                      hide={!showVisibility}
                    />
                    <Bar
                      yAxisId="right"
                      dataKey="avgRanking"
                      fill={CHART_COLORS.purple}
                      name="Ranking Score"
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
              title="Ranking Score Statistics"
              stats={rankingStats}
              color="text-purple-600"
            />
          </div>
        </div>
      )}
    </div>
  )
}
