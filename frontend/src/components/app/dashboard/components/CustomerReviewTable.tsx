import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable,
} from "@tanstack/react-table"
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import {
  type CustomerReviewItem,
  type CustomerReviewsResponse,
  dashboardAPI,
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

interface CustomerReviewTableProps {
  brandId: string
  segment?: string
  /** When provided, fetches all segments in parallel and merges results */
  allSegments?: string[]
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

function SortIcon({ sorted }: { sorted: false | "asc" | "desc" }) {
  if (sorted === "asc") return <ArrowUp className="h-3 w-3" />
  if (sorted === "desc") return <ArrowDown className="h-3 w-3" />
  return <ArrowUpDown className="h-3 w-3 opacity-40" />
}

const SENTIMENT_STYLES: Record<string, string> = {
  Positive: "bg-emerald-50 text-emerald-700 border border-emerald-200",
  Neutral: "bg-slate-50 text-slate-600 border border-slate-200",
  Negative: "bg-red-50 text-red-600 border border-red-200",
  Unknown: "bg-slate-50 text-slate-400 border border-slate-200",
}

const PAGE_SIZE = 8

export function CustomerReviewTable({
  brandId,
  segment,
  allSegments,
  timeRange,
  customStartDate,
  customEndDate,
}: CustomerReviewTableProps) {
  const [reviews, setReviews] = useState<CustomerReviewItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sorting, setSorting] = useState<SortingState>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        let data: CustomerReviewsResponse
        if (allSegments && allSegments.length > 0) {
          data = await dashboardAPI.getBrandCustomerReviewsAllSegments({
            brandId,
            segments: allSegments,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        } else {
          data = await dashboardAPI.getBrandCustomerReviews({
            brandId,
            segment,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        }
        setReviews(data.reviews)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load customer reviews",
        )
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [brandId, segment, timeRange, customStartDate, customEndDate, allSegments])

  const columns = useMemo<ColumnDef<CustomerReviewItem>[]>(
    () => [
      {
        accessorKey: "seq",
        header: "Seq No.",
        enableSorting: false,
        size: 40,
      },
      {
        accessorKey: "review",
        header: "Customer Review",
        enableSorting: false,
        cell: ({ getValue }) => {
          const text = getValue() as string
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
        },
      },
      {
        accessorKey: "sentiment",
        header: "Sentiment",
        enableSorting: true,
        size: 80,
        cell: ({ getValue }) => {
          const s = getValue() as string
          if (!s || s === "Unknown") return null
          return (
            <span
              className={`inline-block px-1.5 py-0.5 rounded text-xs font-medium ${SENTIMENT_STYLES[s] ?? ""}`}
            >
              {s}
            </span>
          )
        },
      },
    ],
    [],
  )

  const table = useReactTable({
    data: reviews,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: PAGE_SIZE } },
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

  if (reviews.length === 0) {
    return (
      <div className="text-center py-6 text-xs text-slate-400">
        No customer reviews found for the selected period
      </div>
    )
  }

  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex flex-col gap-2">
        <div className={`w-full overflow-hidden ${tableClasses.wrapper}`}>
          <Table className={`${tableClasses.table} table-fixed`}>
            <colgroup>
              <col className="w-10" />
              <col />
              <col className="w-20" />
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
                      className={[
                        "text-xs font-semibold uppercase tracking-wide text-slate-500 py-2 whitespace-nowrap select-none",
                        header.column.id === "seq" ? "pl-3" : "",
                        header.column.id === "sentiment"
                          ? "text-right pr-3"
                          : "",
                        header.column.getCanSort() ? "cursor-pointer" : "",
                      ].join(" ")}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <div
                        className={`flex items-center gap-1 ${header.column.id === "sentiment" ? "justify-end" : ""}`}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                        {header.column.getCanSort() && (
                          <SortIcon sorted={header.column.getIsSorted()} />
                        )}
                      </div>
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
                        "text-xs py-1.5 text-slate-700",
                        cell.column.id === "seq" ? "pl-3 text-slate-400" : "",
                        cell.column.id === "review" ? "max-w-0 pr-2" : "",
                        cell.column.id === "sentiment"
                          ? "text-right pr-3 tabular-nums"
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
                ({reviews.length} rows)
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
      </div>
    </TooltipProvider>
  )
}
