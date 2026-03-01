import {
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table"
import { ArrowDown, ArrowUp, ArrowUpDown, ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import {
  type ReferenceSourceItem,
  type ReferenceSourcesResponse,
  type TimeRange,
  dashboardAPI,
} from "@/clients/dashboard"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface AIReferenceSourceTableProps {
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

const PAGE_SIZE = 8

export function AIReferenceSourceTable({
  brandId,
  segment,
  allSegments,
  timeRange,
  customStartDate,
  customEndDate,
}: AIReferenceSourceTableProps) {
  const [sources, setSources] = useState<ReferenceSourceItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sorting, setSorting] = useState<SortingState>([])

  const allSegmentsKey = allSegments?.join(",") ?? ""

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        let data: ReferenceSourcesResponse
        if (allSegments && allSegments.length > 0) {
          data = await dashboardAPI.getBrandReferenceSourcesAllSegments({
            brandId,
            segments: allSegments,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        } else {
          data = await dashboardAPI.getBrandReferenceSources({
            brandId,
            segment,
            timeRange,
            startDate: customStartDate,
            endDate: customEndDate,
          })
        }
        setSources(data.sources)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load reference sources")
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [brandId, segment, allSegmentsKey, timeRange, customStartDate, customEndDate])

  const columns = useMemo<ColumnDef<ReferenceSourceItem>[]>(
    () => [
      {
        accessorKey: "seq",
        header: "#",
        enableSorting: false,
        size: 40,
        cell: ({ getValue }) => (
          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] text-slate-400 border border-transparent">
            {getValue() as number}
          </span>
        ),
      },
      {
        accessorKey: "source",
        header: "Source",
        enableSorting: true,
      },
    ],
    [],
  )

  const table = useReactTable({
    data: sources,
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

  if (sources.length === 0) {
    return (
      <div className="text-center py-6 text-xs text-slate-400">
        No reference sources found for the selected period
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="w-full overflow-auto rounded-lg border border-slate-100">
        <Table className="text-xs">
          <TableHeader className="sticky top-0 z-30 bg-indigo-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="border-b border-indigo-100 hover:bg-transparent">
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    className={[
                      "text-[10px] font-semibold text-indigo-700 py-2 whitespace-nowrap select-none",
                      header.column.id === "seq" ? "w-10 pl-3" : "pr-3",
                      header.column.getCanSort() ? "cursor-pointer" : "",
                    ].join(" ")}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getCanSort() && <SortIcon sorted={header.column.getIsSorted()} />}
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
                className={rowIdx % 2 === 0 ? "bg-white hover:bg-slate-50" : "bg-slate-50/50 hover:bg-slate-100/60"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    className={[
                      "text-xs py-1.5",
                      cell.column.id === "seq" ? "w-10 pl-3 text-slate-400" : "pr-3 break-all",
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

      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-between px-1">
          <span className="text-[10px] text-slate-400">
            Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
            <span className="ml-2 text-slate-300">({sources.length} rows)</span>
          </span>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="sm" className="h-6 w-6 p-0"
              onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
              <ChevronLeft className="h-3 w-3" />
            </Button>
            <Button variant="outline" size="sm" className="h-6 w-6 p-0"
              onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
              <ChevronRight className="h-3 w-3" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
