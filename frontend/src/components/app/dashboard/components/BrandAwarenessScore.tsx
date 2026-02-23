import { Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { type BrandSegmentsResponse, type TimeRange, dashboardAPI } from "@/clients/dashboard"
import { BrandAwarenessScoreGaugeView } from "@/components/app/dashboard/components/BrandAwarenessScoreGaugeView"
import { BrandAwarenessScoreHistoricalView } from "@/components/app/dashboard/components/BrandAwarenessScoreHistoricalView"
import { BrandAwarenessScoreCurrentScore } from "@/components/app/dashboard/components/BrandAwarnessScoreCurrentScore"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface BrandAwarenessScoreProps {
  brandId?: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

export function BrandAwarenessScore({
  brandId,
  timeRange,
  customStartDate,
  customEndDate,
}: BrandAwarenessScoreProps) {
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null)
  const [isLoadingSegments, setIsLoadingSegments] = useState(false)

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
        const data: BrandSegmentsResponse = await dashboardAPI.getBrandSegments(brandId)
        setSegments(data.segments)
        // Default to first segment
        if (data.segments.length > 0) {
          setSelectedSegment(data.segments[0])
        } else {
          setSelectedSegment(null)
        }
      } catch (err) {
        console.error("[BrandAwarenessScore] Error fetching segments:", err)
        setSegments([])
        setSelectedSegment(null)
      } finally {
        setIsLoadingSegments(false)
      }
    }

    fetchSegments()
  }, [brandId])

  return (
    <div className="space-y-8">
      {/* Section 1: All-Segment Overview */}
      <div>
        <h3 className="text-lg font-semibold text-slate-700 mb-4">Overall Awareness (All Segments)</h3>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-8 items-stretch">
          <div className="md:col-span-6 flex">
            <BrandAwarenessScoreCurrentScore brandId={brandId} segment="All-Segment" />
          </div>
          <div className="md:col-span-6 flex">
            <BrandAwarenessScoreGaugeView brandId={brandId} segment="All-Segment" />
          </div>
          <div className="md:col-span-12">
            <BrandAwarenessScoreHistoricalView
              brandId={brandId}
              segment="All-Segment"
              timeRange={timeRange}
              customStartDate={customStartDate}
              customEndDate={customEndDate}
            />
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="h-px w-full bg-slate-200" />

      {/* Section 2: Per-Segment Detail */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-4">
          <h3 className="text-lg font-semibold text-slate-700">Segment Detail</h3>
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
              <SelectTrigger className="w-full sm:w-[300px]">
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

        {selectedSegment && (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-8 items-stretch">
            <div className="md:col-span-6 flex">
              <BrandAwarenessScoreCurrentScore brandId={brandId} segment={selectedSegment} />
            </div>
            <div className="md:col-span-6 flex">
              <BrandAwarenessScoreGaugeView brandId={brandId} segment={selectedSegment} />
            </div>
            <div className="md:col-span-12">
              <BrandAwarenessScoreHistoricalView
                brandId={brandId}
                segment={selectedSegment}
                timeRange={timeRange}
                customStartDate={customStartDate}
                customEndDate={customEndDate}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
