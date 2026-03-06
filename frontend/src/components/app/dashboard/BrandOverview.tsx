import { Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import {
  type BrandOverviewResponse,
  type TimeRange,
  dashboardAPI,
} from "@/clients/dashboard"
import { DashboardPageLayout } from "@/components/app/dashboard/components/DashboardPageLayout"
import { MetricCard } from "@/components/app/dashboard/components/MetricCard"
import { PerformanceChart } from "@/components/app/dashboard/components/PerformanceChart"
import { SegmentMetricsTable } from "@/components/app/dashboard/components/SegmentMetricsTable"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

interface BrandOverviewContentProps {
  brandId: string
  brandName: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

function BrandOverviewContent({
  brandId,
  brandName,
  timeRange,
  customStartDate,
  customEndDate,
}: BrandOverviewContentProps) {
  const [overviewData, setOverviewData] =
    useState<BrandOverviewResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await dashboardAPI.getBrandOverview({
          brandId,
          timeRange,
          startDate: customStartDate,
          endDate: customEndDate,
        })
        setOverviewData(data)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load brand overview data",
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [brandId, timeRange, customStartDate, customEndDate])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
        <span className="ml-3 text-slate-500">Loading brand overview...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-16 text-red-500">
        <p>{error}</p>
      </div>
    )
  }

  if (!overviewData) {
    return (
      <div className="text-center py-16 text-slate-500">
        <p>No data available</p>
      </div>
    )
  }

  const { summary, data_points } = overviewData

  return (
    <div className="space-y-8">
      {/* Metric Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Awareness Score"
          currentValue={summary.awareness_score.current_value}
          previousValue={summary.awareness_score.previous_value}
          change={summary.awareness_score.change}
          hasPrevious={summary.awareness_score.has_previous}
          format="score"
        />
        <MetricCard
          title="Share of Visibility"
          currentValue={summary.share_of_visibility.current_value}
          previousValue={summary.share_of_visibility.previous_value}
          change={summary.share_of_visibility.change}
          hasPrevious={summary.share_of_visibility.has_previous}
          format="percentage"
        />
        <MetricCard
          title="Search Share Index"
          currentValue={summary.search_share_index.current_value}
          previousValue={summary.search_share_index.previous_value}
          change={summary.search_share_index.change}
          hasPrevious={summary.search_share_index.has_previous}
          format="percentage"
        />
        <MetricCard
          title="Position Strength"
          currentValue={summary.position_strength.current_value}
          previousValue={summary.position_strength.previous_value}
          change={summary.position_strength.change}
          hasPrevious={summary.position_strength.has_previous}
          format="percentage"
        />
        <MetricCard
          title="Search Momentum"
          currentValue={summary.search_momentum.current_value}
          previousValue={summary.search_momentum.previous_value}
          change={summary.search_momentum.change}
          hasPrevious={summary.search_momentum.has_previous}
          format="percentage"
        />
      </div>

      {/* Time Series Chart */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="text-xl font-bold">
            Performance Trends
            <span className="ml-2 text-lg font-normal text-slate-500">
              - {brandName}
            </span>
          </CardTitle>
          <CardDescription>
            Awareness score and sub-metrics over time
          </CardDescription>
          <div className="h-px w-full bg-slate-200" />
        </CardHeader>
        <CardContent>
          <PerformanceChart dataPoints={data_points} />
        </CardContent>
      </Card>

      {/* Segment Metrics Table */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="text-xl font-bold">
            Segment Breakdown
            <span className="ml-2 text-lg font-normal text-slate-500">
              - {brandName}
            </span>
          </CardTitle>
          <CardDescription>
            Latest metrics per segment for the selected time range
          </CardDescription>
          <div className="h-px w-full bg-slate-200" />
        </CardHeader>
        <CardContent>
          <SegmentMetricsTable
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

export function BrandOverview() {
  return (
    <DashboardPageLayout
      title="Brand Overview"
      description="Monitor your brand's AI awareness performance at a glance"
    >
      {({ selectedBrandId, selectedBrand, timeRange, customStartDate, customEndDate }) => (
        <BrandOverviewContent
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
