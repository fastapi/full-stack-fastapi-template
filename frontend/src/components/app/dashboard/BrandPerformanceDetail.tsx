import { Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import {
  type BrandOverviewDataPoint,
  type BrandSegmentsResponse,
  dashboardAPI,
  type TimeRange,
} from "@/clients/dashboard"
import { DashboardPageLayout } from "@/components/app/dashboard/components/DashboardPageLayout"
import { PerformanceChart } from "@/components/app/dashboard/components/PerformanceChart"
import { PerformanceDetailTable } from "@/components/app/dashboard/components/PerformanceDetailTable"
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

interface PerformanceDetailContentProps {
  brandId: string
  brandName: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

function PerformanceDetailContent({
  brandId,
  brandName,
  timeRange,
  customStartDate,
  customEndDate,
}: PerformanceDetailContentProps) {
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null)
  const [isLoadingSegments, setIsLoadingSegments] = useState(false)
  const [chartData, setChartData] = useState<BrandOverviewDataPoint[]>([])
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
        console.error("[PerformanceDetail] Error fetching segments:", err)
        setSegments([])
        setSelectedSegment(null)
      } finally {
        setIsLoadingSegments(false)
      }
    }

    fetchSegments()
  }, [brandId])

  // Fetch chart data when segment, timeRange, or brandId changes
  useEffect(() => {
    if (!selectedSegment) {
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

        const data = await dashboardAPI.getBrandOverview({
          brandId,
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
  }, [brandId, selectedSegment, timeRange, customStartDate, customEndDate])

  return (
    <div className="space-y-6">
      {/* Segment Selector */}
      <div className="flex items-center gap-4">
        <h3 className="text-lg font-semibold text-slate-700">Segment</h3>
        {isLoadingSegments ? (
          <div className="flex items-center gap-2 text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading segments...</span>
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
          <span className="text-sm text-slate-500">No segments available</span>
        )}
      </div>

      {/* Chart Card */}
      {selectedSegment && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-bold">
              Performance Metrics
              <span className="ml-2 text-lg font-normal text-slate-500">
                - {brandName} / {selectedSegment}
              </span>
            </CardTitle>
            <CardDescription>
              Share of Visibility, Search Share Index, Position Strength, and
              Momentum over time
            </CardDescription>
            <div className="h-px w-full bg-slate-200" />
          </CardHeader>
          <CardContent>
            {isLoadingChart ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                <span className="ml-3 text-slate-500">
                  Loading chart data...
                </span>
              </div>
            ) : chartError ? (
              <div className="text-center py-16 text-red-500">
                <p>{chartError}</p>
              </div>
            ) : (
              <PerformanceChart dataPoints={chartData} />
            )}
          </CardContent>
        </Card>
      )}

      {/* Detail Table Card */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="text-xl font-bold">
            Segment Performance Details
            <span className="ml-2 text-lg font-normal text-slate-500">
              - {brandName}
            </span>
          </CardTitle>
          <CardDescription>
            All segment metrics with search dates. Highest scores highlighted in
            green, lowest in red.
          </CardDescription>
          <div className="h-px w-full bg-slate-200" />
        </CardHeader>
        <CardContent>
          <PerformanceDetailTable
            brandId={brandId}
            timeRange={timeRange}
            customStartDate={customStartDate}
            customEndDate={customEndDate}
          />
        </CardContent>
      </Card>
    </div>
  )
}

export function BrandPerformanceDetail() {
  return (
    <DashboardPageLayout
      title="Brand Performance Detail"
      description="Track your brand's search visibility rate and ranking trends"
    >
      {({
        selectedBrandId,
        selectedBrand,
        timeRange,
        customStartDate,
        customEndDate,
      }) => (
        <PerformanceDetailContent
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
