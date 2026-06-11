import { ChevronDown, DownloadIcon, Eye, Loader2 } from "lucide-react"
import { useState } from "react"
import { type FileWithJobPublic, FilesService } from "@/client"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { type DownloadFormat, useDownloadFile } from "@/hooks/useDownloadFile"

async function fetchPreviewJson(
  fileId: string,
): Promise<Record<string, unknown>[]> {
  return FilesService.downloadTableExcelFile({
    fileId,
    type: "json",
  }) as Promise<Record<string, unknown>[]>
}

export function FilePreviewModal({ file }: { file: FileWithJobPublic }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [rows, setRows] = useState<Record<string, unknown>[]>([])
  const { mutate: download, isPending: isDownloading } = useDownloadFile()

  const handleOpen = async () => {
    setOpen(true)
    if (rows.length > 0) return
    setLoading(true)
    setError(null)
    try {
      const data = await fetchPreviewJson(file.id)
      setRows(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load preview")
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = (format: DownloadFormat) => {
    download({ fileId: file.id, filename: file.filename, format })
  }

  const cols = rows.length > 0 ? Object.keys(rows[0]) : []

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        className="w-8 h-8 p-0"
        title="Preview"
        onClick={handleOpen}
      >
        <Eye className="w-4 h-4" />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="flex flex-col max-w-full sm:max-w-[70vw] h-[70vh] max-h-[95vh] p-4 gap-0 rounded-xl overflow-hidden">
          <DialogTitle className="sr-only">File Preview</DialogTitle>
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b shrink-0">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold">Transaction List</h2>
              {!loading && rows.length > 0 && (
                <span className="text-sm text-muted-foreground bg-muted px-2.5 py-0.5 rounded-full">
                  {rows.length} rows × {cols.length} columns
                </span>
              )}
            </div>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1.5"
                  disabled={isDownloading || rows.length === 0}
                >
                  {isDownloading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <DownloadIcon className="w-4 h-4" />
                  )}
                  Download
                  <ChevronDown className="w-3.5 h-3.5 opacity-60" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handleDownload("xlsx")}>
                  Excel (.xlsx)
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => handleDownload("xlsx-acc-code")}
                >
                  Analyze Account Code then Excel (.xlsx)
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDownload("csv")}>
                  CSV (.csv)
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDownload("json")}>
                  JSON (.json)
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDownload("html")}>
                  HTML (.html)
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-auto">
            {loading && (
              <div className="flex items-center justify-center h-full gap-2 text-muted-foreground">
                <Loader2 className="w-5 h-5 animate-spin" />
                Loading preview…
              </div>
            )}

            {error && (
              <div className="flex items-center justify-center h-full text-destructive">
                {error}
              </div>
            )}

            {!loading && !error && rows.length === 0 && (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                No data available.
              </div>
            )}

            {!loading && !error && rows.length > 0 && (
              <table className="w-full text-sm border-collapse">
                <thead className="sticky top-0 z-10 bg-background border-b">
                  <tr>
                    {rows.length > 0 &&
                      Object.values(rows[0]).map((col) => (
                        <th
                          key={String(col)}
                          className="px-4 py-3 text-left font-medium text-muted-foreground whitespace-nowrap"
                        >
                          {String(col ?? "")}
                        </th>
                      ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.length > 1 &&
                    rows.slice(1).map((row, i) => (
                      <tr
                        key={`row-${row.id ?? i}`} // use index as fallback key if no id
                        className="border-b last:border-0 hover:bg-muted/40 transition-colors"
                      >
                        {cols.map((col) => {
                          const val = row[col]
                          let display: string
                          if (val == null || String(val).trim() === "") {
                            display = "—"
                          } else {
                            const str = String(val).trim()
                            // strip thousands separators then check if it's a pure number string
                            const stripped = str.replace(/,/g, "")
                            const num = Number(stripped)
                            if (
                              !Number.isNaN(num) &&
                              /^-?\d+(\.\d+)?$/.test(stripped)
                            ) {
                              display = num.toLocaleString()
                            } else {
                              display = str
                            }
                          }
                          return (
                            <td
                              key={col}
                              className="px-4 py-3 whitespace-nowrap text-sm"
                            >
                              {display}
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                </tbody>
              </table>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
