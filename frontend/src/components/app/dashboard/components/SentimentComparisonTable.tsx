import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import {
  dashboardAPI,
  type SentimentComparisonRow,
  type TimeRange,
} from "@/clients/dashboard"
import { tableClasses } from "@/components/app/dashboard/components/tableTheme"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface SentimentComparisonTableProps {
  brandId: string
  segment: string
  competitorBrandName: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
  brandName: string
  competitorName: string
}

const SENTIMENT_STYLES: Record<string, string> = {
  Positive: "bg-emerald-50 text-emerald-700 border border-emerald-200",
  Neutral: "bg-slate-50 text-slate-600 border border-slate-200",
  Negative: "bg-red-50 text-red-600 border border-red-200",
  Unknown: "bg-slate-50 text-slate-400 border border-slate-200",
}

const SENTIMENT_FILTERS = ["All", "Positive", "Neutral", "Negative"] as const
type SentimentFilter = (typeof SENTIMENT_FILTERS)[number]

const PAGE_SIZE = 8

function ReviewCell({ text }: { text: string }) {
  if (!text) return <span className="text-slate-300">—</span>
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="truncate cursor-default">{text}</div>
      </TooltipTrigger>
      <TooltipContent
        side="bottom"
        className="max-w-[320px] text-xs whitespace-normal break-words"
      >
        {text}
      </TooltipContent>
    </Tooltip>
  )
}

export function SentimentComparisonTable({
  brandId,
  segment,
  competitorBrandName,
  timeRange,
  customStartDate,
  customEndDate,
  brandName,
  competitorName,
}: SentimentComparisonTableProps) {
  const [rows, setRows] = useState<SentimentComparisonRow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sentimentFilter, setSentimentFilter] = useState<SentimentFilter>("All")
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: PAGE_SIZE,
  })

  useEffect(() => {
    if (!competitorBrandName) return
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) return

    setIsLoading(true)
    setError(null)
    dashboardAPI
      .getSentimentComparison(
        brandId,
        segment,
        competitorBrandName,
        timeRange,
        customStartDate,
        customEndDate,
      )
      .then((data) => setRows(data.rows))
      .catch((err) =>
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load sentiment comparison",
        ),
      )
      .finally(() => setIsLoading(false))
  }, [
    brandId,
    segment,
    competitorBrandName,
    timeRange,
    customStartDate,
    customEndDate,
  ])

  // Reset page when filter changes
  useEffect(() => {
    setPagination((prev) => ({ ...prev, pageIndex: 0 }))
  }, [])

  const filteredRows = useMemo(() => {
    if (sentimentFilter === "All") return rows
    return rows.filter((r) => r.sentiment === sentimentFilter)
  }, [rows, sentimentFilter])

  const columns = useMemo<ColumnDef<SentimentComparisonRow>[]>(
    () => [
      {
        accessorKey: "sentiment",
        header: "Sentiment",
        size: 80,
        cell: ({ getValue }) => {
          const s = getValue() as string
          return (
            <span
              className={`inline-block px-1.5 py-0.5 rounded text-xs font-medium ${SENTIMENT_STYLES[s] ?? ""}`}
            >
              {s}
            </span>
          )
        },
      },
      {
        accessorKey: "brand_review",
        header: `Customer Review · ${brandName}`,
        cell: ({ getValue }) => <ReviewCell text={getValue() as string} />,
      },
      {
        accessorKey: "comp_review",
        header: `Customer Review · ${competitorName}`,
        cell: ({ getValue }) => <ReviewCell text={getValue() as string} />,
      },
    ],
    [brandName, competitorName],
  )

  const table = useReactTable({
    data: filteredRows,
    columns,
    state: { pagination },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-10">
        <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
        <span className="ml-2 text-xs text-slate-500">Loading...</span>
      </div>
    )
  }

  if (error) {
    return <div className="text-center py-6 text-xs text-red-500">{error}</div>
  }

  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex flex-col gap-2">
        {/* Sentiment filter buttons */}
        <div className="flex items-center gap-1">
          {SENTIMENT_FILTERS.map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => setSentimentFilter(f)}
              className={[
                "px-2 py-0.5 rounded text-xs font-medium transition-colors",
                sentimentFilter === f
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200",
              ].join(" ")}
            >
              {f}
            </button>
          ))}
          <span className="ml-auto text-xs text-slate-400">
            {filteredRows.length} row{filteredRows.length !== 1 ? "s" : ""}
          </span>
        </div>

        {filteredRows.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-400">
            No reviews found for the selected period
          </div>
        ) : (
          <>
            <div className={`w-full overflow-hidden ${tableClasses.wrapper}`}>
              <Table className={`${tableClasses.table} table-fixed`}>
                <colgroup>
                  <col className="w-20" />
                  <col />
                  <col />
                </colgroup>
                <TableHeader
                  className={`sticky top-0 z-30 ${tableClasses.headerRow}`}
                >
                  {table.getHeaderGroups().map((headerGroup) => (
                    <TableRow
                      key={headerGroup.id}
                      className="border-b border-slate-100 hover:bg-transparent"
                    >
                      {headerGroup.headers.map((header) => (
                        <TableHead
                          key={header.id}
                          className="text-xs font-semibold uppercase tracking-wide text-slate-500 py-2 pl-2 whitespace-nowrap"
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                        </TableHead>
                      ))}
                    </TableRow>
                  ))}
                </TableHeader>
                <TableBody>
                  {table.getRowModel().rows.map((row, rowIdx) => (
                    <TableRow
                      key={row.id}
                      className={
                        rowIdx % 2 === 0
                          ? "bg-white hover:bg-slate-50"
                          : "bg-slate-50/40 hover:bg-slate-100/60"
                      }
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell
                          key={cell.id}
                          className={[
                            "text-xs py-1.5 pl-2 text-slate-700",
                            cell.column.id === "brand_review" ||
                            cell.column.id === "comp_review"
                              ? "max-w-0 pr-2"
                              : "",
                          ].join(" ")}
                        >
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext(),
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {table.getPageCount() > 1 && (
              <div className="flex items-center justify-between px-1">
                <span className="text-xs text-slate-500">
                  Page {table.getState().pagination.pageIndex + 1} of{" "}
                  {table.getPageCount()}
                  <span className="ml-2 text-slate-400">
                    ({filteredRows.length} rows)
                  </span>
                </span>
                <div className="flex items-center gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 w-7 p-0"
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                  >
                    <ChevronLeft className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 w-7 p-0"
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage()}
                  >
                    <ChevronRight className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </TooltipProvider>
  )
}
