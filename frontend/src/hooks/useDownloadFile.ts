import { useMutation } from "@tanstack/react-query"
import type { ApiError } from "@/client"
import { fetchBlobWithAuth } from "@/lib/fetchWithAuth"
import useCustomToast from "./useCustomToast"

function triggerBlobDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export type DownloadFormat = "xlsx" | "xlsx-acc-code" | "csv" | "json" | "html"

export interface DownloadFileParams {
  fileId: string
  filename: string
  format: DownloadFormat
}

export function useDownloadFile() {
  const { showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: async ({ fileId, filename, format }: DownloadFileParams) => {
      const safeName = filename.replace(/\.[^.]+$/, "")

      if (format === "xlsx-acc-code") {
        const blob = await fetchBlobWithAuth(
          `/api/v1/files/${fileId}/download/new`,
        )
        triggerBlobDownload(blob, `${safeName}_tables_with_acc_codes.xlsx`)
      } else {
        const blob = await fetchBlobWithAuth(
          `/api/v1/files/${fileId}/download?type=${format}`,
        )
        triggerBlobDownload(blob, `${safeName}_tables.${format}`)
      }
    },
    onError: (err: ApiError) => {
      console.log("Download error:", err)
      showErrorToast(err instanceof Error ? err.message : "Download failed")
    },
  })
}
