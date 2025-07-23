import { client } from "@/client/client.gen"

// Configure the API client
export function configureApiClient() {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  
  // Set base URL and default headers
  client.setConfig({
    baseUrl: baseUrl,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

// Get auth token for requests
export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("access_token")
}

// Set auth token
export function setAuthToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", token)
  }
}

// Remove auth token
export function removeAuthToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token")
  }
}

// Initialize API client
if (typeof window !== "undefined") {
  configureApiClient()
}
