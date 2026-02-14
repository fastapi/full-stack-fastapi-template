/**
 * Dashboard API Client
 *
 * This module provides API client methods for fetching dashboard metrics
 * including awareness scores and consistency indices. It includes built-in
 * caching functionality to minimize API calls and improve performance.
 *
 * Features:
 * - Fetch awareness score data from backend
 * - Fetch consistency index data from backend
 * - Local storage caching with configurable expiration (default: 10 hours)
 * - Automatic cache invalidation on expiry
 */

// API configuration - uses environment variable or falls back to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
const API_PREFIX: string = "/api/v1"

// Cache configuration
const CACHE_EXPIRATION_HOURS = 10 // Cache expires after 10 hours
const CACHE_KEY_AWARENESS = "dashboard_awareness_score"
const CACHE_KEY_CONSISTENCY = "dashboard_consistency_index"
const CACHE_KEY_METRICS = "dashboard_metrics"
const CACHE_KEY_USER_BRANDS = "dashboard_user_brands"

/**
 * Interface for cached data wrapper
 * Stores the actual data along with timestamp for expiration checking
 */
interface CachedData<T> {
  data: T
  timestamp: number // Unix timestamp in milliseconds when data was cached
}

/**
 * Response interface for awareness score API
 * Matches the backend AwarenessScoreResponse schema
 */
export interface AwarenessScoreResponse {
  brand_id: string
  brand_name: string
  current_score: number // Original score (0-100 scale)
  previous_score: number | null
  normalized_score: number // Score on 0-10 scale for gauge display
  previous_normalized_score: number | null
  current_date: string // ISO date string
  previous_date: string | null
  has_previous: boolean
}

/**
 * Response interface for consistency index API
 * Matches the backend ConsistencyIndexResponse schema
 */
export interface ConsistencyIndexResponse {
  brand_id: string
  brand_name: string
  current_index: number // Original index (0-100 scale)
  previous_index: number | null
  normalized_index: number // Index on 0-10 scale for gauge display
  previous_normalized_index: number | null
  current_date: string // ISO date string
  previous_date: string | null
  has_previous: boolean
}

/**
 * Combined response for all dashboard metrics
 * Matches the backend DashboardMetricsResponse schema
 */
export interface DashboardMetricsResponse {
  awareness: AwarenessScoreResponse | null
  consistency: ConsistencyIndexResponse | null
}

/**
 * A single data point in historical trends
 */
export interface HistoricalDataPoint {
  date: string // ISO date string (YYYY-MM-DD)
  awareness_score: number // Normalized to 0-10 scale
  consistency_index: number // Normalized to 0-10 scale
}

/**
 * Statistical summary for a metric
 */
export interface MetricStatistics {
  average: number
  highest: number
  lowest: number
  median: number
  average_growth: number // Percentage
}

/**
 * Response interface for historical trends API
 */
export interface HistoricalTrendsResponse {
  brand_id: string
  brand_name: string
  data_points: HistoricalDataPoint[]
  awareness_stats: MetricStatistics | null
  consistency_stats: MetricStatistics | null
  start_date: string
  end_date: string
}

/**
 * Time range options for historical data queries
 */
export type TimeRange = "1month" | "1quarter" | "1year" | "ytd" | "custom"

/**
 * A brand accessible by the user
 */
export interface UserBrand {
  brand_id: string
  brand_name: string
  project_id: string
  project_name: string
  user_role: string
}

/**
 * Response interface for user brands API
 */
export interface UserBrandsResponse {
  brands: UserBrand[]
  total_count: number
}

/**
 * Parameters for historical trends query
 */
export interface HistoricalTrendsParams {
  timeRange: TimeRange
  startDate?: string // ISO date string for custom range
  endDate?: string // ISO date string for custom range
  brandId?: string
}

/**
 * A single data point for detail metrics (visibility + ranking)
 */
export interface DetailMetricsDataPoint {
  date: string // ISO date string (YYYY-MM-DD)
  visibility_rate: number // Percentage (0-100)
  avg_ranking: number // Average ranking for the day
}

/**
 * Response interface for detail metrics API
 */
export interface DetailMetricsResponse {
  brand_id: string
  brand_name: string
  data_points: DetailMetricsDataPoint[]
  visibility_stats: MetricStatistics | null
  ranking_stats: MetricStatistics | null
  start_date: string
  end_date: string
}

/**
 * Parameters for detail metrics query
 */
export interface DetailMetricsParams {
  timeRange: TimeRange
  startDate?: string
  endDate?: string
  brandId: string
}

/**
 * A competitor brand associated with a user's brand
 */
export interface CompetitorBrand {
  brand_id: string
  competitor_brand_name: string
}

/**
 * Response interface for competitor list API
 */
export interface CompetitorListResponse {
  brand_id: string
  competitors: CompetitorBrand[]
  total_count: number
}

/**
 * A single data point for competitor metrics (visibility + ranking)
 */
export interface CompetitorMetricsDataPoint {
  date: string
  visibility_rate: number
  avg_ranking: number
}

/**
 * Response interface for competitor metrics API
 */
export interface CompetitorMetricsResponse {
  brand_id: string
  competitor_brand_name: string
  data_points: CompetitorMetricsDataPoint[]
  visibility_stats: MetricStatistics | null
  ranking_stats: MetricStatistics | null
  start_date: string
  end_date: string
}

/**
 * Parameters for competitor metrics query
 */
export interface CompetitorMetricsParams {
  brandId: string
  competitorBrandName: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * Standard API error response interface
 */
export interface ApiError {
  detail: string
}

/**
 * Dashboard API Client Class
 *
 * Provides methods to fetch dashboard metrics with built-in caching.
 * The cache uses localStorage and expires after 10 hours to ensure
 * users see reasonably fresh data without making excessive API calls.
 */
class DashboardAPI {
  private readonly baseUrl: string
  private readonly apiPrefix: string

  constructor(baseUrl: string = API_BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl
    this.apiPrefix = apiPrefix
  }

  /**
   * Get authorization headers for API requests
   * Retrieves the JWT token from localStorage
   *
   * @returns Headers object with Content-Type and Authorization
   */
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem("access_token")
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
  }

  /**
   * Check if cached data is still valid (not expired)
   *
   * @param timestamp - Unix timestamp when data was cached
   * @returns true if cache is still valid, false if expired
   */
  private isCacheValid(timestamp: number): boolean {
    const now = Date.now()
    const expirationMs = CACHE_EXPIRATION_HOURS * 60 * 60 * 1000 // Convert hours to milliseconds
    const isValid = now - timestamp < expirationMs

    if (!isValid) {
      console.log(
        `[DashboardAPI] Cache expired. Cached at: ${new Date(timestamp).toISOString()}, ` +
          `Now: ${new Date(now).toISOString()}`,
      )
    }

    return isValid
  }

  /**
   * Retrieve cached data from localStorage
   *
   * @param key - The cache key to look up
   * @returns The cached data if valid, null if expired or not found
   */
  private getCachedData<T>(key: string): T | null {
    try {
      const cachedString = localStorage.getItem(key)

      if (!cachedString) {
        console.log(`[DashboardAPI] No cached data found for key: ${key}`)
        return null
      }

      const cached: CachedData<T> = JSON.parse(cachedString)

      // Check if cache is still valid
      if (this.isCacheValid(cached.timestamp)) {
        console.log(`[DashboardAPI] Using cached data for key: ${key}`)
        return cached.data
      }

      // Cache expired, remove it
      console.log(`[DashboardAPI] Removing expired cache for key: ${key}`)
      localStorage.removeItem(key)
      return null
    } catch (error) {
      // If parsing fails, remove corrupted cache
      console.error(
        `[DashboardAPI] Error parsing cached data for key: ${key}`,
        error,
      )
      localStorage.removeItem(key)
      return null
    }
  }

  /**
   * Store data in localStorage cache with timestamp
   *
   * @param key - The cache key
   * @param data - The data to cache
   */
  private setCachedData<T>(key: string, data: T): void {
    try {
      const cached: CachedData<T> = {
        data,
        timestamp: Date.now(),
      }
      localStorage.setItem(key, JSON.stringify(cached))
      console.log(`[DashboardAPI] Data cached for key: ${key}`)
    } catch (error) {
      // localStorage might be full or disabled
      console.error(`[DashboardAPI] Error caching data for key: ${key}`, error)
    }
  }

  /**
   * Clear all dashboard-related cached data
   * Useful when user wants to force refresh
   */
  public clearCache(): void {
    localStorage.removeItem(CACHE_KEY_AWARENESS)
    localStorage.removeItem(CACHE_KEY_CONSISTENCY)
    localStorage.removeItem(CACHE_KEY_METRICS)
    console.log("[DashboardAPI] All dashboard cache cleared")
  }

  /**
   * Fetch awareness score data from API
   *
   * This method first checks the local cache. If valid cached data exists,
   * it returns that. Otherwise, it makes an API call and caches the result.
   *
   * @param brandId - Optional brand ID to filter results
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns AwarenessScoreResponse or null if no data exists
   * @throws Error if API call fails
   */
  async getAwarenessScore(
    brandId?: string,
    forceRefresh: boolean = false,
  ): Promise<AwarenessScoreResponse | null> {
    // Check cache first (unless force refresh is requested)
    if (!forceRefresh) {
      const cached =
        this.getCachedData<AwarenessScoreResponse>(CACHE_KEY_AWARENESS)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching awareness score from API...")

    // Build URL with optional brand_id query parameter
    let url = `${this.baseUrl}${this.apiPrefix}/dashboard/awareness-score`
    if (brandId) {
      url += `?brand_id=${encodeURIComponent(brandId)}`
    }

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    // Handle authentication errors
    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    // Handle other errors
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch awareness score")
    }

    // Parse response
    const data = await response.json()

    // Cache the result if data exists
    if (data) {
      this.setCachedData(CACHE_KEY_AWARENESS, data)
    }

    console.log("[DashboardAPI] Awareness score fetched successfully")
    return data
  }

  /**
   * Fetch consistency index data from API
   *
   * This method first checks the local cache. If valid cached data exists,
   * it returns that. Otherwise, it makes an API call and caches the result.
   *
   * @param brandId - Optional brand ID to filter results
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns ConsistencyIndexResponse or null if no data exists
   * @throws Error if API call fails
   */
  async getConsistencyIndex(
    brandId?: string,
    forceRefresh: boolean = false,
  ): Promise<ConsistencyIndexResponse | null> {
    // Check cache first (unless force refresh is requested)
    if (!forceRefresh) {
      const cached = this.getCachedData<ConsistencyIndexResponse>(
        CACHE_KEY_CONSISTENCY,
      )
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching consistency index from API...")

    // Build URL with optional brand_id query parameter
    let url = `${this.baseUrl}${this.apiPrefix}/dashboard/consistency-index`
    if (brandId) {
      url += `?brand_id=${encodeURIComponent(brandId)}`
    }

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    // Handle authentication errors
    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    // Handle other errors
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch consistency index")
    }

    // Parse response
    const data = await response.json()

    // Cache the result if data exists
    if (data) {
      this.setCachedData(CACHE_KEY_CONSISTENCY, data)
    }

    console.log("[DashboardAPI] Consistency index fetched successfully")
    return data
  }

  /**
   * Fetch all dashboard metrics in a single API call
   *
   * This is the recommended method for initial dashboard load as it
   * reduces the number of API calls from 2 to 1.
   *
   * @param brandId - Optional brand ID to filter results
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns DashboardMetricsResponse with awareness and consistency data
   * @throws Error if API call fails
   */
  async getDashboardMetrics(
    brandId?: string,
    forceRefresh: boolean = false,
  ): Promise<DashboardMetricsResponse> {
    // Check cache first (unless force refresh is requested)
    if (!forceRefresh) {
      const cached =
        this.getCachedData<DashboardMetricsResponse>(CACHE_KEY_METRICS)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching dashboard metrics from API...")

    // Build URL with optional brand_id query parameter
    let url = `${this.baseUrl}${this.apiPrefix}/dashboard/metrics`
    if (brandId) {
      url += `?brand_id=${encodeURIComponent(brandId)}`
    }

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    // Handle authentication errors
    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    // Handle other errors
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch dashboard metrics")
    }

    // Parse response
    const data: DashboardMetricsResponse = await response.json()

    // Cache the combined result
    this.setCachedData(CACHE_KEY_METRICS, data)

    // Also cache individual components for granular access
    if (data.awareness) {
      this.setCachedData(CACHE_KEY_AWARENESS, data.awareness)
    }
    if (data.consistency) {
      this.setCachedData(CACHE_KEY_CONSISTENCY, data.consistency)
    }

    console.log("[DashboardAPI] Dashboard metrics fetched successfully")
    return data
  }

  /**
   * Generate a cache key for historical trends based on query parameters
   *
   * @param params - The query parameters
   * @returns A unique cache key string
   */
  private getHistoricalTrendsCacheKey(params: HistoricalTrendsParams): string {
    const { timeRange, startDate, endDate, brandId } = params
    if (timeRange === "custom") {
      return `dashboard_historical_custom_${startDate}_${endDate}_${brandId || "all"}`
    }
    return `dashboard_historical_${timeRange}_${brandId || "all"}`
  }

  /**
   * Fetch historical trends data from API
   *
   * This method retrieves time series data for awareness score and consistency index
   * along with statistical summaries. Data is cached based on the query parameters.
   *
   * @param params - Query parameters including time range and optional dates
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns HistoricalTrendsResponse with data points and statistics
   * @throws Error if API call fails or custom range is missing dates
   */
  async getHistoricalTrends(
    params: HistoricalTrendsParams,
    forceRefresh: boolean = false,
  ): Promise<HistoricalTrendsResponse> {
    const cacheKey = this.getHistoricalTrendsCacheKey(params)

    // Check cache first (unless force refresh is requested)
    if (!forceRefresh) {
      const cached = this.getCachedData<HistoricalTrendsResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching historical trends from API...", params)

    // Build URL with query parameters
    const queryParams = new URLSearchParams()
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error(
          "Start date and end date are required for custom time range",
        )
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    if (params.brandId) {
      queryParams.append("brand_id", params.brandId)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/historical-trends?${queryParams.toString()}`

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    // Handle authentication errors
    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    // Handle other errors
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch historical trends")
    }

    // Parse response
    const data: HistoricalTrendsResponse = await response.json()

    // Cache the result
    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Historical trends fetched successfully", {
      dataPoints: data.data_points.length,
      brandName: data.brand_name,
    })

    return data
  }

  /**
   * Clear historical trends cache for all time ranges
   * Useful when data has been updated
   */
  clearHistoricalTrendsCache(): void {
    const timeRanges: TimeRange[] = ["1month", "1quarter", "1year", "ytd"]
    for (const range of timeRanges) {
      const key = `dashboard_historical_${range}_all`
      localStorage.removeItem(key)
    }
    console.log("[DashboardAPI] Historical trends cache cleared")
  }

  /**
   * Fetch brands accessible by the current user
   *
   * This method retrieves all brands from projects where the user
   * is either an owner or a monitor. Data is cached for 10 hours.
   *
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns UserBrandsResponse with list of accessible brands
   * @throws Error if API call fails
   */
  async getUserBrands(forceRefresh: boolean = false): Promise<UserBrandsResponse> {
    // Check cache first (unless force refresh is requested)
    if (!forceRefresh) {
      const cached = this.getCachedData<UserBrandsResponse>(CACHE_KEY_USER_BRANDS)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching user brands from API...")

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/user-brands`

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    // Handle authentication errors
    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    // Handle other errors
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch user brands")
    }

    // Parse response
    const data: UserBrandsResponse = await response.json()

    // Cache the result
    this.setCachedData(CACHE_KEY_USER_BRANDS, data)

    console.log("[DashboardAPI] User brands fetched successfully", {
      count: data.total_count,
    })

    return data
  }

  /**
   * Clear user brands cache
   * Useful when project/brand assignments have changed
   */
  clearUserBrandsCache(): void {
    localStorage.removeItem(CACHE_KEY_USER_BRANDS)
    console.log("[DashboardAPI] User brands cache cleared")
  }

  /**
   * Generate a cache key for detail metrics based on query parameters
   */
  private getDetailMetricsCacheKey(params: DetailMetricsParams): string {
    const { timeRange, startDate, endDate, brandId } = params
    if (timeRange === "custom") {
      return `dashboard_detail_custom_${startDate}_${endDate}_${brandId}`
    }
    return `dashboard_detail_${timeRange}_${brandId}`
  }

  /**
   * Fetch detail metrics (visibility + ranking) from API
   */
  async getDetailMetrics(
    params: DetailMetricsParams,
    forceRefresh: boolean = false,
  ): Promise<DetailMetricsResponse> {
    const cacheKey = this.getDetailMetricsCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<DetailMetricsResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching detail metrics from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error(
          "Start date and end date are required for custom time range",
        )
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/detail-metrics?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch detail metrics")
    }

    const data: DetailMetricsResponse = await response.json()

    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Detail metrics fetched successfully", {
      dataPoints: data.data_points.length,
      brandName: data.brand_name,
    })

    return data
  }

  /**
   * Clear detail metrics cache for all time ranges
   */
  clearDetailMetricsCache(): void {
    const timeRanges: TimeRange[] = ["1month", "1quarter", "1year", "ytd"]
    for (const range of timeRanges) {
      const key = `dashboard_detail_${range}_all`
      localStorage.removeItem(key)
    }
    console.log("[DashboardAPI] Detail metrics cache cleared")
  }

  /**
   * Generate a cache key for competitor list
   */
  private getCompetitorsCacheKey(brandId: string): string {
    return `dashboard_competitors_${brandId}`
  }

  /**
   * Fetch competitors for a brand
   */
  async getCompetitors(
    brandId: string,
    forceRefresh: boolean = false,
  ): Promise<CompetitorListResponse> {
    const cacheKey = this.getCompetitorsCacheKey(brandId)

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorListResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching competitors from API...", { brandId })

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/competitors?brand_id=${encodeURIComponent(brandId)}`

    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitors")
    }

    const data: CompetitorListResponse = await response.json()

    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Competitors fetched successfully", {
      count: data.total_count,
    })

    return data
  }

  /**
   * Generate a cache key for competitor metrics
   */
  private getCompetitorMetricsCacheKey(params: CompetitorMetricsParams): string {
    const { timeRange, startDate, endDate, brandId, competitorBrandName } = params
    if (timeRange === "custom") {
      return `dashboard_comp_metrics_custom_${startDate}_${endDate}_${brandId}_${competitorBrandName}`
    }
    return `dashboard_comp_metrics_${timeRange}_${brandId}_${competitorBrandName}`
  }

  /**
   * Fetch competitor metrics (visibility + ranking) from API
   */
  async getCompetitorMetrics(
    params: CompetitorMetricsParams,
    forceRefresh: boolean = false,
  ): Promise<CompetitorMetricsResponse> {
    const cacheKey = this.getCompetitorMetricsCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorMetricsResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching competitor metrics from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("competitor_brand_name", params.competitorBrandName)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error(
          "Start date and end date are required for custom time range",
        )
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/competitor-metrics?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitor metrics")
    }

    const data: CompetitorMetricsResponse = await response.json()

    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Competitor metrics fetched successfully", {
      dataPoints: data.data_points.length,
      competitor: data.competitor_brand_name,
    })

    return data
  }

  /**
   * Clear competitors cache for a brand
   */
  clearCompetitorsCache(brandId: string): void {
    localStorage.removeItem(this.getCompetitorsCacheKey(brandId))
    console.log("[DashboardAPI] Competitors cache cleared for brand:", brandId)
  }
}

// Export singleton instance for use throughout the application
export const dashboardAPI = new DashboardAPI()
