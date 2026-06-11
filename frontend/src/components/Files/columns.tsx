import type { ColumnDef } from "@tanstack/react-table"
import dayjs from "dayjs"
import { DownloadIcon, Loader2, RefreshCcw } from "lucide-react"
import { type FileWithJobPublic, FilesService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { type DownloadFormat, useDownloadFile } from "@/hooks/useDownloadFile"
import { cn } from "@/lib/utils"
import { DateTimeFormat } from "@/utils"
import { StatusBadge } from "../StatusBadge"
import { FilePreviewModal } from "./FilePreviewModal"

function DownloadMenu({ file }: { file: FileWithJobPublic }) {
  const { mutate: download, isPending } = useDownloadFile()

  const handleSelect = (format: DownloadFormat) => {
    download({ fileId: file.id, filename: file.filename, format })
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="w-8 h-8 p-0"
          title="Download"
          disabled={isPending}
        >
          {isPending ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <DownloadIcon className="w-4 h-4" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleSelect("xlsx")}>
          Excel (.xlsx)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("xlsx-acc-code")}>
          Included Accounting Code (.xlsx)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("csv")}>
          CSV (.csv)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("json")}>
          JSON (.json)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleSelect("html")}>
          HTML (.html)
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export const columns: ColumnDef<FileWithJobPublic>[] = [
  {
    accessorKey: "id",
    header: "File ID",
    cell: ({ row }) => <span className="font-medium">{row.original.id.slice(0,8)}</span>,
  },
  {
    accessorKey: "filename",
    header: "File Name",
    cell: ({ row }) => (
      <span
        className="font-medium block max-w-55 truncate"
        title={row.original.filename}
      >
        {row.original.filename}
      </span>
    ),
  },
  {
    accessorKey: "content_type",
    header: "Content Type",
    cell: ({ row }) => {
      const contentType = row.original.content_type
      return (
        <span
          className={cn(
            "max-w-xs truncate block text-muted-foreground",
            !contentType && "italic",
          )}
        >
          {contentType || "No content type provided"}
        </span>
      )
    },
  },
  {
    id: "state",
    header: "State",
    cell: ({ row }) => {
      const state = row.original.job?.state as
        | "pending"
        | "running"
        | "done"
        | "failed"
        | undefined

      return <StatusBadge status={state || "pending"} />
    },
  },
  {
    id: "created_at",
    header: "Uploaded At",
    cell: ({ row }) => {
      const file = row.original
      return (
        <div className="flex justify-between text-muted-foreground">
          {file.created_at
            ? dayjs(file.created_at).format(DateTimeFormat)
            : "Unknown"}
        </div>
      )
    },
  },
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const file = row.original
      const jobState = file.job?.state
      return (
        <div className="flex justify-end gap-2">
          {(jobState === "running" || jobState === "pending" || !jobState) && (
            <Button
              variant="ghost"
              size="sm"
              className="w-8 h-8 p-0"
              title="Refresh status"
              onClick={() => {
                FilesService.getFileStatus({ fileId: file.id })
              }}
            >
              <RefreshCcw className="w-4 h-4 text-green-300" />
            </Button>
          )}
          {jobState === "done" && (
            <>
              <FilePreviewModal file={file} />
              <DownloadMenu file={file} />
            </>
          )}
        </div>
      )
    },
  },
]
