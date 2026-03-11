import { Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import {
  type CompetitorDetailRow,
  type CompetitorDetailTableResponse,
  dashboardAPI,
  type TimeRange,
} from "@/clients/dashboard"
import { tableClasses } from "@/components/app/dashboard/components/tableTheme"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface CompetitorDetailTableProps {
  brandId: string
  competitorBrandName: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

type MetricKey =
  | "awareness_score"
  | "share_of_visibility"
  | "search_share_index"
  | "position_strength"
  | "search_momentum"

const METRIC_COLUMNS: { key: MetricKey; label: string; isRatio: boolean }[] = [
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

function getGapClassName(gap: number | null): string {
  if (gap === null || gap === undefined) return "text-right text-slate-500"
  if (gap > 0) return "text-right text-green-700 font-bold"
  if (gap < 0) return "text-right text-red-700 font-bold"
  return "text-right"
}

function formatGap(gap: number | null): string {
  if (gap === null || gap === undefined) return "—"
  const sign = gap > 0 ? "+" : ""
  return `${sign}${gap.toFixed(1)}`
}

export function CompetitorDetailTable({
  brandId,
  competitorBrandName,
  timeRange,
  customStartDate,
  customEndDate,
}: CompetitorDetailTableProps) {
  const [rows, setRows] = useState<CompetitorDetailRow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!competitorBrandName) {
      setRows([])
      setIsLoading(false)
      return
    }

    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data: CompetitorDetailTableResponse =
          await dashboardAPI.getCompetitorDetailTable({
            brandId,
            competitorBrandName,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        setRows(data.rows)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load competitor detail table",
        )
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [brandId, competitorBrandName, timeRange, customStartDate, customEndDate])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        <span className="ml-2 text-slate-500">Loading competitor data...</span>
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
        <p>No data available for the selected competitor and time range</p>
      </div>
    )
  }

  return (
    <div className={`overflow-x-auto ${tableClasses.wrapper}`}>
      <Table className={tableClasses.table}>
        <TableHeader className={tableClasses.headerRow}>
          <TableRow>
            <TableHead className={tableClasses.head}>Segment</TableHead>
            {METRIC_COLUMNS.map((col) => (
              <TableHead
                key={col.key}
                className={`${tableClasses.head} ${tableClasses.cellRight}`}
              >
                {col.label}
              </TableHead>
            ))}
            <TableHead
              className={`${tableClasses.head} ${tableClasses.cellRight}`}
            >
              Date
            </TableHead>
            <TableHead
              className={`${tableClasses.head} ${tableClasses.cellRight}`}
            >
              Segment Gap
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, idx) => (
            <TableRow
              key={`${row.segment}-${row.date}-${idx}`}
              className={tableClasses.row}
            >
              <TableCell className="font-medium text-slate-800">
                {row.segment}
              </TableCell>
              {METRIC_COLUMNS.map((col) => (
                <TableCell
                  key={col.key}
                  className={`${tableClasses.cell} ${tableClasses.cellRight}`}
                >
                  {formatValue(row[col.key], col.isRatio)}
                </TableCell>
              ))}
              <TableCell
                className={`${tableClasses.cellMuted} ${tableClasses.cellRight}`}
              >
                {row.date}
              </TableCell>
              <TableCell className={getGapClassName(row.segment_gap)}>
                {formatGap(row.segment_gap)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
