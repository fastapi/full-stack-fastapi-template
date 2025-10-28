import axios, { type AxiosProgressEvent } from "axios"
import { useCallback, useRef, useState } from "react"
import { OpenAPI, type IngestionPublic } from "@/client"

interface UploadResult {
  success: boolean
  data?: IngestionPublic
  error?: string
}

export function useFileUpload() {
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Use ref to track last progress update time for throttling
  const lastUpdateTimeRef = useRef<number>(0)
  const THROTTLE_MS = 500 // Update UI at most every 500ms per PRD

  // Throttled progress update function
  const updateProgress = useCallback((newProgress: number) => {
    const now = Date.now()
    const timeSinceLastUpdate = now - lastUpdateTimeRef.current

    // Only update if enough time has passed or if we've reached 100%
    if (timeSinceLastUpdate >= THROTTLE_MS || newProgress === 100) {
      setProgress(newProgress)
      lastUpdateTimeRef.current = now
    }
  }, [])

  const upload = async (file: File): Promise<UploadResult> => {
    setIsUploading(true)
    setError(null)
    setProgress(0)
    lastUpdateTimeRef.current = 0

    try {
      // Create FormData
      const formData = new FormData()
      formData.append("file", file)

      // Get auth token
      const token = typeof OpenAPI.TOKEN === "function"
        ? await (OpenAPI.TOKEN as () => Promise<string>)()
        : OpenAPI.TOKEN

      // Use axios directly for progress tracking
      const result = await axios.post<IngestionPublic>(
        `${OpenAPI.BASE}/api/v1/ingestions`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            ...(token && { Authorization: `Bearer ${token}` })
          },
          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            // Calculate percentage, handle undefined total
            const total = progressEvent.total || 1
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / total,
            )

            // Cap at 100%
            const cappedProgress = Math.min(percentCompleted, 100)

            // Update with throttling
            updateProgress(cappedProgress)
          },
        },
      )

      // Ensure progress shows 100% at completion
      setProgress(100)
      return { success: true, data: result.data }
    } catch (err: unknown) {
      // Extract error message from axios error response
      const axiosError = err as {
        response?: {
          data?: {
            detail?: string
          }
        }
      }

      const errorMsg =
        axiosError.response?.data?.detail || "Upload failed. Please try again."
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
    lastUpdateTimeRef.current = 0
  }

  return { upload, progress, isUploading, error, reset }
}
