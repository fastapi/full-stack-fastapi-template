import { Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import {
  type BrandSegmentsResponse,
  type CompetitorAwarenessDataPoint,
  type CompetitorBrand,
  type CompetitorListResponse,
  type TimeRange,
  type TopCompetitorResponse,
  dashboardAPI,
} from "@/clients/dashboard"
import { DashboardPageLayout } from "@/components/app/dashboard/components/DashboardPageLayout"
import { CompetitorAwarenessChart } from "@/components/app/dashboard/components/CompetitorAwarenessChart"
import { CompetitorDetailTable } from "@/components/app/dashboard/components/CompetitorDetailTable"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface CompetitiveAnalysisContentProps {
  brandId: string
  brandName: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

function CompetitiveAnalysisContent({
  brandId,
  brandName,
  timeRange,
  customStartDate,
  customEndDate,
}: CompetitiveAnalysisContentProps) {
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null)
  const [isLoadingSegments, setIsLoadingSegments] = useState(false)

  const [competitors, setCompetitors] = useState<CompetitorBrand[]>([])
  const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null)
  const [isLoadingCompetitors, setIsLoadingCompetitors] = useState(false)

  const [topCompetitorName, setTopCompetitorName] = useState<string | null>(null)
  const [isLoadingTopCompetitor, setIsLoadingTopCompetitor] = useState(false)

  const [chartData, setChartData] = useState<CompetitorAwarenessDataPoint[]>([])
  const [isLoadingChart, setIsLoadingChart] = useState(false)
  const [chartError, setChartError] = useState<string | null>(null)

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
        console.error("[CompetitiveAnalysis] Error fetching segments:", err)
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
    if (!brandId) {
      setCompetitors([])
      setSelectedCompetitor(null)
      return
    }

    const fetchCompetitors = async () => {
      try {
        setIsLoadingCompetitors(true)
        const data: CompetitorListResponse =
          await dashboardAPI.getCompetitors(brandId)
        setCompetitors(data.competitors)
        if (data.competitors.length > 0) {
          setSelectedCompetitor(data.competitors[0].competitor_brand_name)
        } else {
          setSelectedCompetitor(null)
        }
      } catch (err) {
        console.error("[CompetitiveAnalysis] Error fetching competitors:", err)
        setCompetitors([])
        setSelectedCompetitor(null)
      } finally {
        setIsLoadingCompetitors(false)
      }
    }

    fetchCompetitors()
  }, [brandId])

  // Fetch top competitor when segment, brandId, or timeRange changes
  useEffect(() => {
    if (!brandId || !selectedSegment) {
      setTopCompetitorName(null)
      return
    }
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) {
      return
    }

    const fetchTopCompetitor = async () => {
      try {
        setIsLoadingTopCompetitor(true)
        const data: TopCompetitorResponse =
          await dashboardAPI.getTopCompetitor({
            brandId,
            segment: selectedSegment,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        setTopCompetitorName(data.top_competitor_name)
      } catch (err) {
        console.error("[CompetitiveAnalysis] Error fetching top competitor:", err)
        setTopCompetitorName(null)
      } finally {
        setIsLoadingTopCompetitor(false)
      }
    }

    fetchTopCompetitor()
  }, [brandId, selectedSegment, timeRange, customStartDate, customEndDate])

  // Fetch chart data when segment, competitor, timeRange, or brandId changes
  useEffect(() => {
    if (!selectedSegment || !selectedCompetitor) {
      setChartData([])
      return
    }
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) {
      return
    }

    const fetchChartData = async () => {
      try {
        setIsLoadingChart(true)
        setChartError(null)

        const data = await dashboardAPI.getCompetitorAwareness({
          brandId,
          competitorBrandName: selectedCompetitor,
          timeRange,
          startDate: customStartDate,
          endDate: customEndDate,
          segment: selectedSegment,
        })

        setChartData(data.data_points)
      } catch (err) {
        setChartError(
          err instanceof Error ? err.message : "Failed to load chart data",
        )
      } finally {
        setIsLoadingChart(false)
      }
    }

    fetchChartData()
  }, [brandId, selectedSegment, selectedCompetitor, timeRange, customStartDate, customEndDate])

  return (
    <div className="space-y-6">
      {/* Segment, Competitor, and Top Competitor on one line */}
      <div className="flex items-center gap-6">
        {/* Segment Selector */}
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-slate-700">Segment</h3>
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
              <SelectTrigger className="w-[220px]">
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
            <span className="text-sm text-slate-500">No segments</span>
          )}
        </div>

        {/* Competitor Selector */}
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-slate-700">Competitor</h3>
          {isLoadingCompetitors ? (
            <div className="flex items-center gap-2 text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Loading...</span>
            </div>
          ) : competitors.length > 0 ? (
            <Select
              value={selectedCompetitor || undefined}
              onValueChange={setSelectedCompetitor}
            >
              <SelectTrigger className="w-[220px]">
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
          ) : (
            <span className="text-sm text-slate-500">No competitors</span>
          )}
        </div>

        {/* Top Competitor */}
        <div className="ml-auto flex items-center gap-2">
          {isLoadingTopCompetitor ? (
            <div className="flex items-center gap-2 text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Finding top competitor...</span>
            </div>
          ) : topCompetitorName ? (
            <span className="text-sm text-slate-600">
              Top Competitor: <span className="font-semibold text-slate-800">{topCompetitorName}</span>
            </span>
          ) : null}
        </div>
      </div>

      {/* Chart Card */}
      {selectedSegment && selectedCompetitor && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-bold">
              Competitor Performance
              <span className="ml-2 text-lg font-normal text-slate-500">
                - {selectedCompetitor} / {selectedSegment}
              </span>
            </CardTitle>
            <CardDescription>
              Awareness, Share of Visibility, Search Share Index, Position Strength, and Momentum over time
            </CardDescription>
            <div className="h-px w-full bg-slate-200" />
          </CardHeader>
          <CardContent>
            {isLoadingChart ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                <span className="ml-3 text-slate-500">Loading chart data...</span>
              </div>
            ) : chartError ? (
              <div className="text-center py-16 text-red-500">
                <p>{chartError}</p>
              </div>
            ) : (
              <CompetitorAwarenessChart dataPoints={chartData} />
            )}
          </CardContent>
        </Card>
      )}

      {/* Detail Table Card */}
      {selectedCompetitor && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-bold">
              Competitor Segment Details
              <span className="ml-2 text-lg font-normal text-slate-500">
                - {brandName} vs {selectedCompetitor}
              </span>
            </CardTitle>
            <CardDescription>
              All segment metrics with search dates. Segment Gap = {brandName} awareness - {selectedCompetitor} awareness. Green when your brand is ahead, red when behind.
            </CardDescription>
            <div className="h-px w-full bg-slate-200" />
          </CardHeader>
          <CardContent>
            <CompetitorDetailTable
              brandId={brandId}
              competitorBrandName={selectedCompetitor}
              timeRange={timeRange}
              customStartDate={customStartDate}
              customEndDate={customEndDate}
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export function CompetitiveAnalysis() {
  return (
    <DashboardPageLayout
      title="Competitive Analysis"
      description="Analyze competitor visibility and ranking in AI search results"
    >
      {({ selectedBrandId, selectedBrand, timeRange, customStartDate, customEndDate }) => (
        <CompetitiveAnalysisContent
          brandId={selectedBrandId}
          brandName={selectedBrand.brand_name}
          timeRange={timeRange}
          customStartDate={customStartDate}
          customEndDate={customEndDate}
        />
      )}
    </DashboardPageLayout>
  )
}
