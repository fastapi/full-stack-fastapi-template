import { OpenAPI } from "@/client"

export type MediaKind = "cover" | "banner" | "gallery"

export interface MediaAsset {
  id: string
  content_type: string
  content_id: string
  kind: string
  alt_text?: string | null
  display_order: number
  is_primary: boolean
  is_public: boolean
  original_filename: string
  file_name: string
  file_url: string
  mime_type: string
  size_bytes: number
  uploaded_by_id?: string | null
  created_at: string
  updated_at: string
}

interface MediaAssetsResponse {
  data: MediaAsset[]
  count: number
}

function getBaseUrl() {
  return OpenAPI.BASE || ""
}

async function authHeaders() {
  const token = localStorage.getItem("access_token") || ""
  return {
    Authorization: `Bearer ${token}`,
  }
}

function withBase(url: string) {
  const base = getBaseUrl().replace(/\/$/, "")
  return `${base}${url}`
}

async function parseError(response: Response): Promise<never> {
  let message = "Request failed"
  try {
    const body = await response.json()
    const detail = body?.detail
    if (typeof detail === "string") {
      message = detail
    } else if (Array.isArray(detail) && detail.length > 0) {
      message = detail[0]?.msg || message
    }
  } catch {
    // No-op fallback
  }
  throw new Error(message)
}

export async function listMediaAssets(params: {
  contentType: string
  contentId: string
}): Promise<MediaAssetsResponse> {
  const search = new URLSearchParams({
    content_type: params.contentType,
    content_id: params.contentId,
    is_public: "true",
    limit: "500",
  })

  const response = await fetch(withBase(`/api/v1/media/?${search.toString()}`), {
    method: "GET",
  })

  if (!response.ok) {
    return parseError(response)
  }

  return response.json()
}

export async function uploadMediaAsset(params: {
  file: File
  contentType: string
  contentId: string
  kind: MediaKind
  altText?: string
  isPrimary?: boolean
  displayOrder?: number
  onProgress?: (percent: number) => void
}): Promise<MediaAsset> {
  const formData = new FormData()
  formData.append("file", params.file)
  formData.append("content_type", params.contentType)
  formData.append("content_id", params.contentId)
  formData.append("kind", params.kind)
  if (params.altText) {
    formData.append("alt_text", params.altText)
  }
  formData.append("display_order", String(params.displayOrder ?? 0))
  formData.append("is_primary", String(Boolean(params.isPrimary)))

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open("POST", withBase("/api/v1/media/upload"))

    void authHeaders()
      .then((headers) => {
        if (headers.Authorization) {
          xhr.setRequestHeader("Authorization", headers.Authorization)
        }
      })
      .then(() => {
        xhr.send(formData)
      })
      .catch((error: unknown) => {
        reject(error instanceof Error ? error : new Error("Upload failed"))
      })

    xhr.upload.onprogress = (event) => {
      if (!params.onProgress || !event.lengthComputable) return
      const percent = Math.round((event.loaded / event.total) * 100)
      params.onProgress(percent)
    }

    xhr.onerror = () => reject(new Error("Upload failed"))

    xhr.onload = async () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const payload = JSON.parse(xhr.responseText) as MediaAsset
          params.onProgress?.(100)
          resolve(payload)
        } catch {
          reject(new Error("Invalid upload response"))
        }
        return
      }

      try {
        const detail = JSON.parse(xhr.responseText)
        const message =
          typeof detail?.detail === "string"
            ? detail.detail
            : "Upload failed"
        reject(new Error(message))
      } catch {
        reject(new Error("Upload failed"))
      }
    }

  })
}

export async function updateMediaAsset(
  mediaId: string,
  payload: {
    kind?: MediaKind
    alt_text?: string
    is_primary?: boolean
    display_order?: number
  }
): Promise<MediaAsset> {
  const response = await fetch(withBase(`/api/v1/media/${mediaId}`), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...(await authHeaders()),
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    return parseError(response)
  }

  return response.json()
}

export async function deleteMediaAsset(mediaId: string): Promise<void> {
  const response = await fetch(withBase(`/api/v1/media/${mediaId}`), {
    method: "DELETE",
    headers: await authHeaders(),
  })

  if (!response.ok) {
    return parseError(response)
  }
}
