import {
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table"
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import {
  type ReferenceSourceComparisonRow,
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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface ReferenceSourceComparisonTableProps {
  brandId: string
  segment: string
  competitorBrandName: string
  timeRange: TimeRange
  customStartDate?: string
  customEndDate?: string
  brandName: string
  competitorName: string
}

type SourceFilterKey = "all" | "common" | "brand_only" | "comp_only"

interface FilterOption {
  key: SourceFilterKey
  label: string
  category: string | null
}

const PAGE_SIZE = 8

function SourceCell({ url }: { url: string }) {
  if (!url) return <span className="text-slate-300">—</span>
  // Show just the hostname as visible label, full URL in tooltip
  let label = url
  try {
    label = new URL(url).hostname.replace(/^www\./, "")
  } catch {
    // keep full url as label if not a valid URL
  }
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-600 hover:underline truncate block"
          onClick={(e) => e.stopPropagation()}
        >
          {label}
        </a>
      </TooltipTrigger>
      <TooltipContent side="bottom" className="max-w-[360px] text-xs break-all">
        {url}
      </TooltipContent>
    </Tooltip>
  )
}

export function ReferenceSourceComparisonTable({
  brandId,
  segment,
  competitorBrandName,
  timeRange,
  customStartDate,
  customEndDate,
  brandName,
  competitorName,
}: ReferenceSourceComparisonTableProps) {
  const filterOptions = useMemo<FilterOption[]>(
    () => [
      { key: "all",        label: "All",                          category: null },
      { key: "common",     label: "Common Source",                category: "common" },
      { key: "brand_only", label: `Addition - ${brandName}`,      category: "brand_only" },
      { key: "comp_only",  label: `Addition - ${competitorName}`, category: "comp_only" },
    ],
    [brandName, competitorName],
  )

  const [rows, setRows] = useState<ReferenceSourceComparisonRow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sourceFilterKey, setSourceFilterKey] = useState<SourceFilterKey>("all")
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: PAGE_SIZE })

  useEffect(() => {
    if (!competitorBrandName) return
    if (timeRange === "custom" && (!customStartDate || !customEndDate)) return

    setIsLoading(true)
    setError(null)
    dashboardAPI
      .getReferenceSourceComparison(brandId, segment, competitorBrandName, timeRange, customStartDate, customEndDate)
      .then((data) => setRows(data.rows))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load reference source comparison"))
      .finally(() => setIsLoading(false))
  }, [brandId, segment, competitorBrandName, timeRange, customStartDate, customEndDate])

  // Reset page when filter changes
  useEffect(() => {
    setPagination((prev) => ({ ...prev, pageIndex: 0 }))
  }, [sourceFilterKey])

  const filteredRows = useMemo(() => {
    const option = filterOptions.find((o) => o.key === sourceFilterKey)
    if (!option?.category) return rows
    return rows.filter((r) => r.category === option.category)
  }, [rows, sourceFilterKey, filterOptions])

  const columns = useMemo<ColumnDef<ReferenceSourceComparisonRow>[]>(
    () => [
      {
        id: "seq",
        header: "#",
        size: 36,
        cell: ({ row }) => (
          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] text-slate-400 border border-transparent">
            {row.index + 1}
          </span>
        ),
      },
      {
        accessorKey: "brand_source",
        header: `Source · ${brandName}`,
        cell: ({ getValue }) => <SourceCell url={getValue() as string} />,
      },
      {
        accessorKey: "comp_source",
        header: `Source · ${competitorName}`,
        cell: ({ getValue }) => <SourceCell url={getValue() as string} />,
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
        {/* Source filter buttons */}
        <div className="flex flex-wrap items-center gap-1">
          {filterOptions.map((opt) => (
            <button
              key={opt.key}
              type="button"
              onClick={() => setSourceFilterKey(opt.key)}
              className={[
                "px-2 py-0.5 rounded text-[10px] font-medium transition-colors whitespace-nowrap",
                sourceFilterKey === opt.key
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200",
              ].join(" ")}
            >
              {opt.label}
            </button>
          ))}
          <span className="ml-auto text-[10px] text-slate-400">
            {filteredRows.length} row{filteredRows.length !== 1 ? "s" : ""}
          </span>
        </div>

        {filteredRows.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-400">
            No reference sources found for the selected period
          </div>
        ) : (
          <>
            <div className="w-full overflow-hidden rounded-lg border border-slate-100">
              <Table className="text-xs table-fixed w-full">
                <colgroup>
                  <col className="w-8" />
                  <col />
                  <col />
                </colgroup>
                <TableHeader className="sticky top-0 z-30 bg-indigo-50">
                  {table.getHeaderGroups().map((headerGroup) => (
                    <TableRow
                      key={headerGroup.id}
                      className="border-b border-indigo-100 hover:bg-transparent"
                    >
                      {headerGroup.headers.map((header) => (
                        <TableHead
                          key={header.id}
                          className="text-[10px] font-semibold text-indigo-700 py-2 pl-2 whitespace-nowrap"
                        >
                          {flexRender(header.column.columnDef.header, header.getContext())}
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
                          : "bg-slate-50/50 hover:bg-slate-100/60"
                      }
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell
                          key={cell.id}
                          className={[
                            "text-xs py-1.5 pl-2",
                            cell.column.id === "brand_source" || cell.column.id === "comp_source"
                              ? "max-w-0 pr-2"
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

            {table.getPageCount() > 1 && (
              <div className="flex items-center justify-between px-1">
                <span className="text-[10px] text-slate-400">
                  Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
                  <span className="ml-2 text-slate-300">({filteredRows.length} rows)</span>
                </span>
                <div className="flex items-center gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                  >
                    <ChevronLeft className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-6 w-6 p-0"
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
