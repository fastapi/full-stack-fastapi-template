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
  dashboardAPI,
  type SegmentMetricsResponse,
  type SegmentMetricsRow,
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

interface SegmentMetricsTableProps {
  brandId: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
}

function SortIcon({ sorted }: { sorted: false | "asc" | "desc" }) {
  if (sorted === "asc") return <ArrowUp className="h-3 w-3" />
  if (sorted === "desc") return <ArrowDown className="h-3 w-3" />
  return <ArrowUpDown className="h-3 w-3 opacity-40" />
}

const PAGE_SIZE = 8

export function SegmentMetricsTable({
  brandId,
  timeRange,
  customStartDate,
  customEndDate,
}: SegmentMetricsTableProps) {
  const [segments, setSegments] = useState<SegmentMetricsRow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sorting, setSorting] = useState<SortingState>([])

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

  const columns = useMemo<ColumnDef<SegmentMetricsRow>[]>(
    () => [
      {
        accessorKey: "segment",
        header: "Segment",
        enableSorting: true,
      },
      {
        accessorKey: "awareness_score",
        header: "Awareness",
        cell: ({ getValue }) => (getValue() as number).toFixed(1),
        enableSorting: true,
      },
      {
        accessorKey: "share_of_visibility",
        header: "Visibility",
        cell: ({ getValue }) => `${((getValue() as number) * 100).toFixed(1)}%`,
        enableSorting: true,
      },
      {
        accessorKey: "search_share_index",
        header: "Share Index",
        cell: ({ getValue }) => `${((getValue() as number) * 100).toFixed(1)}%`,
        enableSorting: true,
      },
      {
        accessorKey: "position_strength",
        header: "Position",
        cell: ({ getValue }) => `${((getValue() as number) * 100).toFixed(1)}%`,
        enableSorting: true,
      },
      {
        accessorKey: "search_momentum",
        header: "Momentum",
        cell: ({ getValue }) => `${((getValue() as number) * 100).toFixed(1)}%`,
        enableSorting: true,
      },
      {
        accessorKey: "consistency_index",
        header: "Consistency",
        cell: ({ getValue }) => (getValue() as number).toFixed(1),
        enableSorting: true,
      },
    ],
    [],
  )

  const table = useReactTable({
    data: segments,
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
        <Loader2 className="h-5 w-5 animate-spin text-slate-400" />
        <span className="ml-2 text-xs text-slate-500">Loading...</span>
      </div>
    )
  }

  if (error) {
    return <div className="text-center py-8 text-xs text-red-500">{error}</div>
  }

  if (segments.length === 0) {
    return (
      <div className="text-center py-8 text-xs text-slate-400">
        No segment data available for the selected time range
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {/* Scrollable table */}
      <div className={`w-full overflow-auto ${tableClasses.wrapper}`}>
        <Table className={`min-w-max ${tableClasses.table}`}>
          <TableHeader
            className={`sticky top-0 z-30 ${tableClasses.headerRow}`}
          >
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow
                key={headerGroup.id}
                className="border-b border-slate-100 hover:bg-transparent"
              >
                {headerGroup.headers.map((header, idx) => (
                  <TableHead
                    key={header.id}
                    className={[
                      "text-xs font-semibold uppercase tracking-wide text-slate-500 py-2 whitespace-nowrap select-none",
                      idx === 0
                        ? "sticky left-0 z-20 bg-slate-50 pl-3"
                        : "text-right pr-3",
                      header.column.getCanSort() ? "cursor-pointer" : "",
                    ].join(" ")}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div
                      className={`flex items-center gap-1 ${idx > 0 ? "justify-end" : ""}`}
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                      <SortIcon sorted={header.column.getIsSorted()} />
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
                {row.getVisibleCells().map((cell, idx) => (
                  <TableCell
                    key={cell.id}
                    className={[
                      "text-xs py-1.5 text-slate-700",
                      idx === 0
                        ? "sticky left-0 z-10 font-medium whitespace-nowrap pl-3"
                        : "text-right pr-3 tabular-nums",
                      idx === 0
                        ? rowIdx % 2 === 0
                          ? "bg-white"
                          : "bg-slate-50/40"
                        : "",
                    ].join(" ")}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-between px-1">
          <span className="text-xs text-slate-500">
            Page {table.getState().pagination.pageIndex + 1} of{" "}
            {table.getPageCount()}
            <span className="ml-2 text-slate-400">
              ({segments.length} rows)
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
  )
}
