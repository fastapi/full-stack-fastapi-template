import { Loader2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import {
  type PerformanceDetailRow,
  type PerformanceDetailTableResponse,
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

interface PerformanceDetailTableProps {
  brandId: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

type NumericKey = "awareness_score" | "share_of_visibility" | "search_share_index" | "position_strength" | "search_momentum"

const METRIC_COLUMNS: { key: NumericKey; label: string; isRatio: boolean }[] = [
  { key: "awareness_score", label: "Awareness", isRatio: false },
  { key: "share_of_visibility", label: "Share of Visibility", isRatio: true },
  { key: "search_share_index", label: "Search Share Index", isRatio: true },
  { key: "position_strength", label: "Position Strength", isRatio: true },
  { key: "search_momentum", label: "Momentum", isRatio: true },
]

function formatValue(value: number, isRatio: boolean): string {
  if (isRatio) {
    return `${(value * 100).toFixed(1)}%`
  }
  return value.toFixed(1)
}

function getCellClassName(value: number, min: number, max: number): string {
  if (min === max) return "text-right"
  if (value === max) return "text-right bg-green-100 text-green-700 font-bold"
  if (value === min) return "text-right bg-red-100 text-red-700 font-bold"
  return "text-right"
}

export function PerformanceDetailTable({
  brandId,
  timeRange,
  customStartDate,
  customEndDate,
}: PerformanceDetailTableProps) {
  const [rows, setRows] = useState<PerformanceDetailRow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data: PerformanceDetailTableResponse =
          await dashboardAPI.getPerformanceDetailTable({
            brandId,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        setRows(data.rows)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load performance detail table",
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [brandId, timeRange, customStartDate, customEndDate])

  // Calculate min/max for each metric column across all rows
  const columnExtremes = useMemo(() => {
    if (rows.length === 0) return {}

    const extremes: Record<NumericKey, { min: number; max: number }> = {} as any

    for (const col of METRIC_COLUMNS) {
      const values = rows.map((r) => r[col.key])
      extremes[col.key] = {
        min: Math.min(...values),
        max: Math.max(...values),
      }
    }

    return extremes
  }, [rows])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        <span className="ml-2 text-slate-500">Loading performance data...</span>
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

  if (rows.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <p>No data available for the selected time range</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="font-semibold">Segment</TableHead>
            {METRIC_COLUMNS.map((col) => (
              <TableHead key={col.key} className="text-right font-semibold">
                {col.label}
              </TableHead>
            ))}
            <TableHead className="text-right font-semibold">Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, idx) => (
            <TableRow key={`${row.segment}-${row.date}-${idx}`}>
              <TableCell className="font-medium">{row.segment}</TableCell>
              {METRIC_COLUMNS.map((col) => {
                const value = row[col.key]
                const extremes = columnExtremes[col.key]
                const cellClass = extremes
                  ? getCellClassName(value, extremes.min, extremes.max)
                  : "text-right"
                return (
                  <TableCell key={col.key} className={cellClass}>
                    {formatValue(value, col.isRatio)}
                  </TableCell>
                )
              })}
              <TableCell className="text-right text-slate-600">
                {row.date}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
