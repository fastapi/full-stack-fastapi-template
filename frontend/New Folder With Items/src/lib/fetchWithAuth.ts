import axios from "axios"
import { OpenAPI } from "@/client/core/OpenAPI"

async function getAuthHeaders(): Promise<Record<string, string>> {
  const token =
    typeof OpenAPI.TOKEN === "function"
      ? await OpenAPI.TOKEN({} as never)
      : OpenAPI.TOKEN
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * POST to a path and return the response as a Blob.
 * Used for binary file downloads where FilesService cannot be used
 * directly (it doesn't set responseType: 'blob').
 */
export async function fetchBlobWithAuth(path: string): Promise<Blob> {
  const base = OpenAPI.BASE || ""
  const headers = await getAuthHeaders()
  const response = await axios.post<Blob>(`${base}${path}`, null, {
    responseType: "blob",
    headers,
  })
  return response.data
}
