import { useState } from "react"
import { type IngestionPublic, IngestionsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"

interface UploadResult {
  success: boolean
  data?: IngestionPublic
  error?: string
}

export function useFileUpload() {
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const upload = async (file: File): Promise<UploadResult> => {
    setIsUploading(true)
    setError(null)
    setProgress(0)

    try {
      // OpenAPI client handles FormData automatically
      const result = await IngestionsService.createIngestion({
        formData: { file },
      })

      setProgress(100)
      return { success: true, data: result }
    } catch (err) {
      const apiError = err as ApiError
      const errorMsg =
        (apiError.body as { detail?: string })?.detail ||
        "Upload failed. Please try again."
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setIsUploading(false)
    }
  }

  const reset = () => {
    setProgress(0)
    setIsUploading(false)
    setError(null)
  }

  return { upload, progress, isUploading, error, reset }
}
