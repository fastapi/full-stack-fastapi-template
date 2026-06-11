import { useSuspenseQuery } from "@tanstack/react-query"
import dayjs from "dayjs"
import { Download, Eye, FileText } from "lucide-react"
import { FilesService } from "@/client"
import { Button } from "@/components/ui/button"
import { Empty } from "@/components/ui/empty"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { DateTimeFormat } from "@/utils"
import { StatusBadge } from "./StatusBadge"

function getRecentUploadFilesQueryOptions() {
  return {
    queryFn: () => FilesService.listFiles({ skip: 0, limit: 5 }),
    queryKey: ["files-recent-upload"],
  }
}

const fileSizeInMB = (sizeInBytes: number | null | undefined) => {
  if (sizeInBytes == null) return "N/A"
  return `${(sizeInBytes / (1024 * 1024)).toFixed(2)} MB`
}

export function FileHistoryTable() {
  const { data: recentFiles } = useSuspenseQuery(
    getRecentUploadFilesQueryOptions(),
  )

  if (recentFiles.count === 0) {
    return (
      <Empty>
        <FileText className="w-12 h-12 text-muted-foreground mb-2" />
        <p className="font-medium">No files uploaded yet</p>
        <p className="text-sm text-muted-foreground">
          Start by uploading a bank statement to get started
        </p>
      </Empty>
    )
  }

  return (
    <div className="rounded-lg border border-border overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Filename</TableHead>
            <TableHead>Size</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {recentFiles.data.map((file) => (
            <TableRow key={file.id}>
              <TableCell>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-primary/60" />
                  <span className="truncate font-medium">{file.filename}</span>
                </div>
              </TableCell>
              <TableCell className="text-foreground/70">
                {fileSizeInMB(file.size)}
              </TableCell>
              <TableCell>
                <StatusBadge
                  status={
                    file.job_status as
                      | "pending"
                      | "running"
                      | "done"
                      | "failed"
                      | undefined
                  }
                />
              </TableCell>
              <TableCell className="text-foreground/70">
                {dayjs(file.created_at).format(DateTimeFormat)}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  {file.job_status === "done" && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-8 h-8 p-0"
                        title="View"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-8 h-8 p-0"
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
