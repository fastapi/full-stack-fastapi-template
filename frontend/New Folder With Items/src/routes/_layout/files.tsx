import { useQueryClient, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useEffect, useRef } from "react"

import { type FileWithJobPublic, FilesService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { columns } from "@/components/Files/columns"
import PendingItems from "@/components/Pending/PendingItems"

function getFilesQueryOptions(limit = 0) {
  return {
    queryFn: () => FilesService.listFiles({ skip: 0, limit }),
    queryKey: ["files"],
    //refetchInterval: 3000,
  }
}

export const Route = createFileRoute("/_layout/files")({
  component: Files,
  head: () => ({
    meta: [
      {
        title: "Files - FastAPI Template",
      },
    ],
  }),
})

export function FilesTableContent({ limit = 0 }: { limit?: number }) {
  const queryClient = useQueryClient()
  const { data: files } = useSuspenseQuery(getFilesQueryOptions(limit))
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    const pollPendingFiles = async () => {
      const pendingFiles = files.filter(
        (f) => f.job?.state !== "done" && f.job?.state !== "failed",
      )

      if (pendingFiles.length === 0) {
        if (pollingRef.current) {
          clearInterval(pollingRef.current)
          pollingRef.current = null
        }
        return
      }

      const result = await FilesService.getFilesBatchStatus({
        requestBody: { file_ids: pendingFiles.map((f) => f.id) },
      })

      queryClient.setQueryData(
        ["files"],
        (old: FileWithJobPublic[] | undefined) => {
          if (!old) return old
          const updatedMap = new Map(result.map((job) => [job.file_id, job]))
          return old.map((f) => {
            const updatedJob = updatedMap.get(f.id)
            return updatedJob ? { ...f, job: updatedJob } : f
          })
        },
      )
    }

    pollingRef.current = setInterval(pollPendingFiles, 3000)

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [files, queryClient])

  if (files.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any items yet</h3>
        <p className="text-muted-foreground">Add a new item to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={files} />
}

function FilesTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <FilesTableContent />
    </Suspense>
  )
}

function Files() {
  return (
    <div className="flex flex-col gap-6">
      <FilesTable />
    </div>
  )
}
