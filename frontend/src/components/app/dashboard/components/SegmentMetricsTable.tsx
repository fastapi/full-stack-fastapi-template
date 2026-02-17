import { Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import {
  type SegmentMetricsResponse,
  type SegmentMetricsRow,
  type TimeRange,
  dashboardAPI,
} from "@/clients/dashboard"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface SegmentMetricsTableProps {
  brandId: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

export function SegmentMetricsTable({
  brandId,
  timeRange,
  customStartDate,
  customEndDate,
}: SegmentMetricsTableProps) {
  const [segments, setSegments] = useState<SegmentMetricsRow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data: SegmentMetricsResponse =
          await dashboardAPI.getSegmentMetrics({
            brandId,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        setSegments(data.segments)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load segment metrics",
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [brandId, timeRange, customStartDate, customEndDate])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        <span className="ml-2 text-slate-500">Loading segment metrics...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-500">
        <p>{error}</p>
      </div>
    )
  }

  if (segments.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <p>No segment data available for the selected time range</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="font-semibold">Segment</TableHead>
            <TableHead className="text-right font-semibold">
              Awareness Score
            </TableHead>
            <TableHead className="text-right font-semibold">
              Share of Visibility
            </TableHead>
            <TableHead className="text-right font-semibold">
              Search Share Index
            </TableHead>
            <TableHead className="text-right font-semibold">
              Position Strength
            </TableHead>
            <TableHead className="text-right font-semibold">
              Search Momentum
            </TableHead>
            <TableHead className="text-right font-semibold">
              Consistency Index
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {segments.map((seg) => (
            <TableRow key={seg.segment}>
              <TableCell className="font-medium">{seg.segment}</TableCell>
              <TableCell className="text-right">
                {seg.awareness_score.toFixed(1)}
              </TableCell>
              <TableCell className="text-right">
                {(seg.share_of_visibility * 100).toFixed(1)}%
              </TableCell>
              <TableCell className="text-right">
                {(seg.search_share_index * 100).toFixed(1)}%
              </TableCell>
              <TableCell className="text-right">
                {(seg.position_strength * 100).toFixed(1)}%
              </TableCell>
              <TableCell className="text-right">
                {(seg.search_momentum * 100).toFixed(1)}%
              </TableCell>
              <TableCell className="text-right">
                {seg.consistency_index.toFixed(1)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
