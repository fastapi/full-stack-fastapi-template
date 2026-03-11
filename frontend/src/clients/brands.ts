/**
 * Brands API Client
 *
 * This module provides API client methods for managing brands.
 * Includes built-in caching functionality to minimize API calls.
 */

import { getAuthToken } from "./auth-helper"

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX = "/api/v1"

// Cache configuration
const CACHE_EXPIRATION_HOURS = 10
const CACHE_KEY_BRANDS = "brands_list"

/**
 * Interface for cached data wrapper
 */
interface CachedData<T> {
  data: T
  timestamp: number
}

/**
 * Response interface for a single brand
 */
export interface Brand {
  brand_id: string
  brand_name: string
  description: string | null
  company_id: string | null
  created_by: string
  created_at: string // ISO datetime string
  is_active: boolean
}

/**
 * Response interface for brand list
 */
export interface BrandListResponse {
  brands: Brand[]
  total_count: number
}

/**
 * Segment data for brand setup
 */
export interface SegmentData {
  segment_name: string
  prompts: string
}

/**
 * Segment detail from backend
 */
export interface SegmentDetail {
  prompt_id: string
  segment_name: string
  prompts: string
  is_active: boolean
}

/**
 * Request interface for creating a brand with segments
 */
export interface BrandSetupRequest {
  brand_name: string
  description?: string
  segments: SegmentData[]
}

/**
 * Response interface for brand setup
 */
export interface BrandSetupResponse {
  brand_id: string
  prompt_count: number
  message: string
}

/**
 * Request interface for updating a brand
 */
export interface BrandUpdateRequest {
  brand_name?: string
  description?: string
  is_active?: boolean
}

/**
 * Response interface for brand update
 */
export interface BrandUpdateResponse {
  brand_id: string
  message: string
}

/**
 * Response interface for brand details including segments
 */
export interface BrandDetailResponse {
  brand_id: string
  brand_name: string
  description: string | null
  company_id: string | null
  created_by: string
  created_at: string
  is_active: boolean
  segments: SegmentDetail[]
}

/**
 * Request interface for full brand update
 */
export interface BrandFullUpdateRequest {
  brand_name: string
  description?: string
  is_active: boolean
  segments: SegmentData[]
}

/**
 * Standard API error response
 */
export interface ApiError {
  detail: string
}

/**
 * Error type for 409 Conflict responses
 */
export interface ApiConflictError extends Error {
  isConflict: boolean
}

/**
 * Brands API Client Class
 */
class BrandsAPI {
  private readonly baseUrl: string
  private readonly apiPrefix: string

  constructor(baseUrl: string = API_BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl
    this.apiPrefix = apiPrefix
  }

  /**
   * Get authorization headers
   */
  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken()
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
  }

  /**
   * Check if cached data is still valid
   */
  private isCacheValid(timestamp: number): boolean {
    const now = Date.now()
    const expirationMs = CACHE_EXPIRATION_HOURS * 60 * 60 * 1000
    return now - timestamp < expirationMs
  }

  /**
   * Retrieve cached data from localStorage
   */
  private getCachedData<T>(key: string): T | null {
    try {
      const cachedString = localStorage.getItem(key)
      if (!cachedString) return null

      const cached: CachedData<T> = JSON.parse(cachedString)
      if (this.isCacheValid(cached.timestamp)) {
        console.log(`[BrandsAPI] Using cached data for key: ${key}`)
        return cached.data
      }

      localStorage.removeItem(key)
      return null
    } catch {
      localStorage.removeItem(key)
      return null
    }
  }

  /**
   * Store data in localStorage cache
   */
  private setCachedData<T>(key: string, data: T): void {
    try {
      const cached: CachedData<T> = {
        data,
        timestamp: Date.now(),
      }
      localStorage.setItem(key, JSON.stringify(cached))
      console.log(`[BrandsAPI] Data cached for key: ${key}`)
    } catch (error) {
      console.error(`[BrandsAPI] Error caching data: ${error}`)
    }
  }

  /**
   * Clear brands cache
   */
  public clearCache(): void {
    localStorage.removeItem(CACHE_KEY_BRANDS)
    console.log("[BrandsAPI] Cache cleared")
  }

  /**
   * Fetch list of brands for the current user
   *
   * @param forceRefresh - If true, bypasses cache
   * @returns BrandListResponse with brands array
   */
  async getBrands(forceRefresh: boolean = false): Promise<BrandListResponse> {
    // Check cache first
    if (!forceRefresh) {
      const cached = this.getCachedData<BrandListResponse>(CACHE_KEY_BRANDS)
      if (cached) {
        return cached
      }
    }

    console.log("[BrandsAPI] Fetching brands from API...")

    const url = `${this.baseUrl}${this.apiPrefix}/brands`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      if (forceRefresh) {
        throw new Error("Unauthorized - Please log in again")
      }
      // Retry once with a fresh token
      this.clearCache()
      return await this.getBrands(true)
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch brands")
    }

    const data: BrandListResponse = await response.json()

    // Cache the result
    this.setCachedData(CACHE_KEY_BRANDS, data)

    console.log(`[BrandsAPI] Fetched ${data.total_count} brands`)
    return data
  }

  /**
   * Get brand details including segments
   *
   * @param brandId - The brand ID to fetch
   * @returns BrandDetailResponse with full brand details
   */
  async getBrandDetail(brandId: string): Promise<BrandDetailResponse> {
    console.log(`[BrandsAPI] Fetching brand detail ${brandId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/brands/${brandId}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Brand not found or you don't have permission to view it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch brand details")
    }

    const data: BrandDetailResponse = await response.json()

    console.log(
      `[BrandsAPI] Brand detail fetched: ${data.brand_id}, segments=${data.segments.length}`
    )
    return data
  }

  /**
   * Create a new brand with segments
   *
   * @param setupData - Brand setup data
   * @returns BrandSetupResponse with brand ID and prompt count
   */
  async setupBrand(setupData: BrandSetupRequest): Promise<BrandSetupResponse> {
    console.log("[BrandsAPI] Setting up brand with segments...")

    const url = `${this.baseUrl}${this.apiPrefix}/brands/setup`

    const response = await fetch(url, {
      method: "POST",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(setupData),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 409) {
      const error: ApiError = await response.json()
      const conflictError = new Error(error.detail || "Brand already exists")
      ;(conflictError as ApiConflictError).isConflict = true
      throw conflictError
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to setup brand")
    }

    const data: BrandSetupResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(
      `[BrandsAPI] Brand setup completed: brand=${data.brand_id}, prompts=${data.prompt_count}`
    )
    return data
  }

  /**
   * Update an existing brand (partial update)
   *
   * @param brandId - The brand ID to update
   * @param updateData - Fields to update
   * @returns BrandUpdateResponse with success message
   */
  async updateBrand(
    brandId: string,
    updateData: BrandUpdateRequest
  ): Promise<BrandUpdateResponse> {
    console.log(`[BrandsAPI] Updating brand ${brandId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/brands/${brandId}`

    const response = await fetch(url, {
      method: "PATCH",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(updateData),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Brand not found or you don't have permission to update it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to update brand")
    }

    const data: BrandUpdateResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(`[BrandsAPI] Brand updated: ${data.brand_id}`)
    return data
  }

  /**
   * Full update of brand including segments
   *
   * @param brandId - The brand ID to update
   * @param updateData - Full brand update data
   * @returns BrandSetupResponse with brand ID and prompt count
   */
  async updateBrandFull(
    brandId: string,
    updateData: BrandFullUpdateRequest
  ): Promise<BrandSetupResponse> {
    console.log(`[BrandsAPI] Full update brand ${brandId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/brands/${brandId}`

    const response = await fetch(url, {
      method: "PUT",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(updateData),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Brand not found or you don't have permission to update it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to update brand")
    }

    const data: BrandSetupResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(
      `[BrandsAPI] Brand full update completed: brand=${data.brand_id}, prompts=${data.prompt_count}`
    )
    return data
  }

  /**
   * Delete a brand and its associated segments and prompts
   *
   * @param brandId - The brand ID to delete
   * @returns BrandUpdateResponse with success message
   */
  async deleteBrand(brandId: string): Promise<BrandUpdateResponse> {
    console.log(`[BrandsAPI] Deleting brand ${brandId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/brands/${brandId}`

    const response = await fetch(url, {
      method: "DELETE",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Brand not found or you don't have permission to delete it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to delete brand")
    }

    const data: BrandUpdateResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(`[BrandsAPI] Brand deleted: ${data.brand_id}`)
    return data
  }

  /**
   * Add a member to a brand
   *
   * @param brandId - The brand ID
   * @param data - Member data to add
   */
  async addBrandMember(brandId: string, data: object): Promise<void> {
    console.log(`[BrandsAPI] Adding member to brand ${brandId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/brands/${brandId}/members`

    const response = await fetch(url, {
      method: "POST",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(data),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to add brand member")
    }

    console.log(`[BrandsAPI] Member added to brand ${brandId}`)
  }

  /**
   * Remove a member from a brand
   *
   * @param brandId - The brand ID
   * @param userId - The user ID to remove
   */
  async removeBrandMember(brandId: string, userId: string): Promise<void> {
    console.log(`[BrandsAPI] Removing member ${userId} from brand ${brandId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/brands/${brandId}/members/${userId}`

    const response = await fetch(url, {
      method: "DELETE",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to remove brand member")
    }

    console.log(`[BrandsAPI] Member ${userId} removed from brand ${brandId}`)
  }
}

// Export singleton instance
export const brandsAPI = new BrandsAPI()
