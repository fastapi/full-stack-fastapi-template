import { getAuthToken } from "./auth-helper"

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
const API_PREFIX: string = "/api/v1"

export interface ProfileSetupRequest {
  first_name: string
  middle_name?: string
  last_name: string
  phone?: string
  email: string
  company_name: string
  job_title?: string
}

export interface CompanyResponse {
  company_id: string
  company_name: string
}

export interface ProfileResponse {
  user_id: string
  first_name: string
  middle_name?: string
  last_name: string
  email: string
  phone?: string
  job_title?: string
  company?: CompanyResponse
  created_at: string
  updated_at?: string
}

export interface CompanySearchResult {
  company_id: string
  company_name: string
}

export interface ApiError {
  detail: string
}

class ProfileAPI {
  private readonly baseUrl: string
  private readonly apiPrefix: string

  constructor(baseUrl: string = API_BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl
    this.apiPrefix = apiPrefix
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken()
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
  }

  async getProfile(): Promise<ProfileResponse | null> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/profile/me`,
      {
        method: "GET",
        headers: await this.getAuthHeaders(),
      },
    )

    if (response.status === 401) {
      throw new Error("Unauthorized")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to get profile")
    }

    const data = await response.json()
    return data
  }

  async setupProfile(data: ProfileSetupRequest): Promise<ProfileResponse> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/profile/setup`,
      {
        method: "POST",
        headers: await this.getAuthHeaders(),
        body: JSON.stringify(data),
      },
    )

    if (response.status === 401) {
      throw new Error("Unauthorized")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to setup profile")
    }

    return response.json()
  }

  async searchCompanies(
    query: string,
    limit: number = 10,
  ): Promise<CompanySearchResult[]> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    })

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/profile/companies/search?${params}`,
      {
        method: "GET",
        headers: await this.getAuthHeaders(),
      },
    )

    if (response.status === 401) {
      throw new Error("Unauthorized")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to search companies")
    }

    return response.json()
  }
}

export const profileAPI = new ProfileAPI()
