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

import { getAuthToken } from "./auth-helper"

// API configuration - uses environment variable or falls back to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX: string = "/api/v1"

// Cache configuration
const CACHE_EXPIRATION_HOURS = 10 // Cache expires after 10 hours
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
  segment?: string
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
  segment?: string
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
  segment?: string
}

/**
 * Response interface for brand segments API
 */
export interface BrandSegmentsResponse {
  brand_id: string
  segments: string[]
}

/**
 * A single data point for brand overview time series
 */
export interface BrandOverviewDataPoint {
  date: string
  awareness_score: number
  share_of_visibility: number
  search_share_index: number
  position_strength: number
  search_momentum: number
}

/**
 * Summary for a single metric with current value and change
 */
export interface BrandOverviewMetricSummary {
  current_value: number
  previous_value: number | null
  change: number | null
  has_previous: boolean
}

/**
 * Summary of all 5 metrics
 */
export interface BrandOverviewSummary {
  awareness_score: BrandOverviewMetricSummary
  share_of_visibility: BrandOverviewMetricSummary
  search_share_index: BrandOverviewMetricSummary
  position_strength: BrandOverviewMetricSummary
  search_momentum: BrandOverviewMetricSummary
}

/**
 * Response for brand overview endpoint
 */
export interface BrandOverviewResponse {
  brand_id: string
  brand_name: string
  summary: BrandOverviewSummary
  data_points: BrandOverviewDataPoint[]
  start_date: string
  end_date: string
}

/**
 * Parameters for brand overview query
 */
export interface BrandOverviewParams {
  brandId: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
  segment?: string
}

/**
 * A single segment's latest metrics
 */
export interface SegmentMetricsRow {
  segment: string
  awareness_score: number
  share_of_visibility: number
  search_share_index: number
  position_strength: number
  search_momentum: number
  consistency_index: number
}

/**
 * Response for segment metrics endpoint
 */
export interface SegmentMetricsResponse {
  brand_id: string
  brand_name: string
  segments: SegmentMetricsRow[]
}

/**
 * Parameters for segment metrics query
 */
export interface SegmentMetricsParams {
  brandId: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * A single row in the performance detail table with date
 */
export interface PerformanceDetailRow {
  segment: string
  awareness_score: number
  share_of_visibility: number
  search_share_index: number
  position_strength: number
  search_momentum: number
  date: string // YYYY-MM-DD
}

/**
 * Response for performance detail table endpoint
 */
export interface PerformanceDetailTableResponse {
  brand_id: string
  brand_name: string
  rows: PerformanceDetailRow[]
}

/**
 * Parameters for performance detail table query
 */
export interface PerformanceDetailTableParams {
  brandId: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * A single data point for competitor awareness time series
 */
export interface CompetitorAwarenessDataPoint {
  date: string
  awareness_score: number
  share_of_visibility: number
  search_share_index: number
  position_strength: number
  search_momentum: number
}

/**
 * Response for competitor awareness endpoint
 */
export interface CompetitorAwarenessResponse {
  brand_id: string
  competitor_brand_name: string
  data_points: CompetitorAwarenessDataPoint[]
  start_date: string
  end_date: string
}

/**
 * Parameters for competitor awareness query
 */
export interface CompetitorAwarenessParams {
  brandId: string
  competitorBrandName: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
  segment: string
}

/**
 * A single row in the competitor detail table with segment gap
 */
export interface CompetitorDetailRow {
  segment: string
  awareness_score: number
  share_of_visibility: number
  search_share_index: number
  position_strength: number
  search_momentum: number
  date: string
  segment_gap: number | null
}

/**
 * Response for competitor detail table endpoint
 */
export interface CompetitorDetailTableResponse {
  brand_id: string
  brand_name: string
  competitor_brand_name: string
  rows: CompetitorDetailRow[]
}

/**
 * Parameters for competitor detail table query
 */
export interface CompetitorDetailTableParams {
  brandId: string
  competitorBrandName: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * Response for top competitor endpoint
 */
export interface TopCompetitorResponse {
  brand_id: string
  segment: string
  top_competitor_name: string | null
  avg_awareness_score: number | null
}

/**
 * Parameters for top competitor query
 */
export interface TopCompetitorParams {
  brandId: string
  segment: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * A single signal's latest severity for the risk overview
 */
export interface InsightSignalSeverity {
  signal_type: string
  signal_name: string
  severity: string
  signal_score: number
  business_meaning: string
}

/**
 * Response for risk overview endpoint (5 severity cards)
 */
export interface BrandRiskOverviewResponse {
  brand_id: string
  segment: string
  signals: InsightSignalSeverity[]
}

/**
 * Parameters for risk overview query
 */
export interface RiskOverviewParams {
  brandId: string
  segment: string
}

/**
 * A single data point for risk history chart
 */
export interface RiskHistoryDataPoint {
  date: string
  competitive_dominance: number | null
  competitive_erosion: number | null
  competitor_breakthrough: number | null
  growth_deceleration: number | null
  position_weakness: number | null
  rank_displacement: number | null
  fragile_leadership: number | null
  volatility_spike: number | null
  new_entrant: number | null
}

/**
 * Response for risk history endpoint
 */
export interface RiskHistoryResponse {
  brand_id: string
  segment: string
  data_points: RiskHistoryDataPoint[]
}

/**
 * Parameters for risk history query
 */
export interface RiskHistoryParams {
  brandId: string
  segment: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * Response for brand segments endpoint
 */
export interface BrandSegmentsResponse {
  brand_id: string
  segments: string[]
}

/**
 * A single data point for the brand ranking trend chart.
 * is_interpolated=true means the brand had no visibility that day — values are linearly filled.
 */
export interface BrandRankingTrendDataPoint {
  date: string
  min_ranking: number | null
  max_ranking: number | null
  median_ranking: number | null
  avg_ranking: number | null
  is_interpolated: boolean
}

export interface BrandRankingTrendResponse {
  brand_id: string
  segment: string
  data_points: BrandRankingTrendDataPoint[]
}

export interface BrandRankingTrendParams {
  brandId: string
  segment: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * A single data point for the brand impression historical trend chart.
 * Nulls have been interpolated on the server side.
 */
export interface BrandImpressionTrendDataPoint {
  date: string
  visibility: number | null
  position: number | null
  sentiment: number | null
}

export interface BrandImpressionTrendResponse {
  brand_id: string
  segment: string
  data_points: BrandImpressionTrendDataPoint[]
}

export interface BrandImpressionTrendParams {
  brandId: string
  segment: string
  timeRange: TimeRange
  startDate?: string
  endDate?: string
}

/**
 * A single metric in the brand impression summary card
 */
export interface BrandImpressionMetric {
  current_value: number | null
  previous_value: number | null
  change: number | null
  trend: "up" | "down" | "flat" | "no_data"
}

/**
 * Response for the brand impression summary card (3 quick metrics)
 */
export interface BrandImpressionSummaryResponse {
  brand_id: string
  brand_name: string
  visibility: BrandImpressionMetric
  position: BrandImpressionMetric
  sentiment: BrandImpressionMetric
  current_period_end: string | null
  previous_period_end: string | null
}

export interface ReferenceSourceItem {
  seq: number
  source: string
}

export interface ReferenceSourcesResponse {
  brand_id: string
  sources: ReferenceSourceItem[]
}

export interface CustomerReviewItem {
  seq: number
  review: string
  sentiment: "Positive" | "Neutral" | "Negative"
}

export interface CustomerReviewsResponse {
  brand_id: string
  reviews: CustomerReviewItem[]
}

/**
 * A single gap metric for competitive comparison
 */
export interface CompetitorGapMetric {
  gap_value: number | null
  previous_gap_value: number | null
  change: number | null
  trend: "up" | "down" | "flat" | "no_data"
}

/**
 * Response for competitor gap summary (3 gap metrics)
 */
export interface CompetitorGapSummaryResponse {
  brand_id: string
  segment: string
  competitor_brand_name: string
  visibility_gap: CompetitorGapMetric
  position_gap: CompetitorGapMetric
  sentiment_gap: CompetitorGapMetric
  current_period_end: string | null
  previous_period_end: string | null
}

/**
 * Response for competitors-by-segment endpoint
 */
export interface CompetitorsBySegmentResponse {
  brand_id: string
  segment: string
  competitor_names: string[]
}

/**
 * A single time-series point of gap metrics (brand vs competitor)
 */
export interface CompetitorGapTrendDataPoint {
  date: string
  // Raw values
  brand_visibility: number | null
  comp_visibility: number | null
  brand_median_ranking: number | null
  comp_median_ranking: number | null
  brand_sentiment: number | null
  comp_sentiment: number | null
  // Gaps
  visibility_gap: number | null
  position_gap: number | null
  sentiment_gap: number | null
}

/**
 * Response for competitor gap historical trend endpoint
 */
export interface CompetitorGapTrendResponse {
  brand_id: string
  segment: string
  competitor_brand_name: string
  data_points: CompetitorGapTrendDataPoint[]
}

/**
 * One date window of brand vs competitor ranking stats (lower number = better position).
 * Null means the brand/competitor had no visibility in that window.
 */
export interface CompetitorRankingDetailDataPoint {
  date: string
  // Raw values
  brand_best: number | null
  brand_worst: number | null
  brand_avg: number | null
  comp_best: number | null
  comp_worst: number | null
  comp_avg: number | null
  // Gaps (comp - brand; positive = brand ranks better)
  best_gap: number | null
  worst_gap: number | null
  avg_gap: number | null
}

/**
 * Response for competitor ranking detail endpoint
 */
export interface CompetitorRankingDetailResponse {
  brand_id: string
  segment: string
  competitor_brand_name: string
  data_points: CompetitorRankingDetailDataPoint[]
}

/**
 * One row in the sentiment comparison table (brand review vs competitor review)
 */
export interface SentimentComparisonRow {
  sentiment: string
  brand_review: string
  comp_review: string
}

/**
 * Response for sentiment comparison endpoint
 */
export interface SentimentComparisonResponse {
  brand_id: string
  segment: string
  competitor_brand_name: string
  rows: SentimentComparisonRow[]
}

/**
 * One row in the reference source comparison table
 */
export interface ReferenceSourceComparisonRow {
  seq: number
  /** "common" | "brand_only" | "comp_only" */
  category: string
  brand_source: string
  comp_source: string
}

/**
 * Response for reference source comparison endpoint
 */
export interface ReferenceSourceComparisonResponse {
  brand_id: string
  segment: string
  competitor_brand_name: string
  rows: ReferenceSourceComparisonRow[]
}

/**
 * Standard API error response interface
 */
export interface ApiError {
  detail: string
}

export interface MarketDynamicDataPoint {
  date: string
  visibility_share: number | null
  search_momentum: number | null
  position_strength: number | null
}

export interface MarketDynamicBrandData {
  brand_name: string
  is_target: boolean
  data_points: MarketDynamicDataPoint[]
  avg_visibility_share: number
  median_position_strength: number
}

export interface MarketDynamicResponse {
  brands: MarketDynamicBrandData[]
  start_date: string
  end_date: string
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
  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken()
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
    localStorage.removeItem(CACHE_KEY_METRICS)
    console.log("[DashboardAPI] All dashboard cache cleared")
  }

  /**
   * Clear every localStorage entry whose key starts with "dashboard_".
   * Call this on user-initiated refresh so stale chart data is discarded.
   */
  public clearAllCache(): void {
    const keysToRemove: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith("dashboard_")) keysToRemove.push(key)
    }
    keysToRemove.forEach((k) => localStorage.removeItem(k))
    console.log(`[DashboardAPI] Cleared ${keysToRemove.length} dashboard cache entries`)
  }

  /**
   * Fetch awareness score data from API
   *
   * @param brandId - Optional brand ID to filter results
   * @param segment - Segment name to filter by (default: "All-Segment")
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns AwarenessScoreResponse or null if no data exists
   * @throws Error if API call fails
   */
  async getAwarenessScore(
    brandId?: string,
    segment: string = "All-Segment",
    forceRefresh: boolean = false,
  ): Promise<AwarenessScoreResponse | null> {
    const cacheKey = `dashboard_awareness_${brandId || "all"}_${segment}`

    // Check cache first (unless force refresh is requested)
    if (!forceRefresh) {
      const cached = this.getCachedData<AwarenessScoreResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching awareness score from API...")

    // Build URL with query parameters
    const queryParams = new URLSearchParams()
    if (brandId) {
      queryParams.append("brand_id", brandId)
    }
    queryParams.append("segment", segment)

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/awareness-score?${queryParams.toString()}`

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
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
      this.setCachedData(cacheKey, data)
    }

    console.log("[DashboardAPI] Awareness score fetched successfully")
    return data
  }

  /**
   * Fetch consistency index data from API
   *
   * @param brandId - Optional brand ID to filter results
   * @param segment - Segment name to filter by (default: "All-Segment")
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns ConsistencyIndexResponse or null if no data exists
   * @throws Error if API call fails
   */
  async getConsistencyIndex(
    brandId?: string,
    segment: string = "All-Segment",
    forceRefresh: boolean = false,
  ): Promise<ConsistencyIndexResponse | null> {
    const cacheKey = `dashboard_consistency_${brandId || "all"}_${segment}`

    // Check cache first (unless force refresh is requested)
    if (!forceRefresh) {
      const cached = this.getCachedData<ConsistencyIndexResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching consistency index from API...")

    // Build URL with query parameters
    const queryParams = new URLSearchParams()
    if (brandId) {
      queryParams.append("brand_id", brandId)
    }
    queryParams.append("segment", segment)

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/consistency-index?${queryParams.toString()}`

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
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
      this.setCachedData(cacheKey, data)
    }

    console.log("[DashboardAPI] Consistency index fetched successfully")
    return data
  }

  /**
   * Fetch all dashboard metrics in a single API call
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
      headers: await this.getAuthHeaders(),
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

    console.log("[DashboardAPI] Dashboard metrics fetched successfully")
    return data
  }

  /**
   * Generate a cache key for historical trends based on query parameters
   */
  private getHistoricalTrendsCacheKey(params: HistoricalTrendsParams): string {
    const { timeRange, startDate, endDate, brandId, segment } = params
    const seg = segment || "All-Segment"
    if (timeRange === "custom") {
      return `dashboard_historical_custom_${startDate}_${endDate}_${brandId || "all"}_${seg}`
    }
    return `dashboard_historical_${timeRange}_${brandId || "all"}_${seg}`
  }

  /**
   * Fetch historical trends data from API
   *
   * @param params - Query parameters including time range, optional dates, and segment
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

    if (params.segment) {
      queryParams.append("segment", params.segment)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/historical-trends?${queryParams.toString()}`

    // Make API request
    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
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
      headers: await this.getAuthHeaders(),
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
   * Fetch segments for a brand
   *
   * @param brandId - Brand ID to get segments for
   * @param forceRefresh - If true, bypasses cache and fetches fresh data
   * @returns BrandSegmentsResponse with list of segment names
   * @throws Error if API call fails
   */
  async getBrandSegments(
    brandId: string,
    forceRefresh: boolean = false,
  ): Promise<BrandSegmentsResponse> {
    const cacheKey = `dashboard_segments_${brandId}`

    if (!forceRefresh) {
      const cached = this.getCachedData<BrandSegmentsResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching brand segments from API...", { brandId })

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/brand-segments?brand_id=${encodeURIComponent(brandId)}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch brand segments")
    }

    const data: BrandSegmentsResponse = await response.json()

    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Brand segments fetched successfully", {
      count: data.segments.length,
    })

    return data
  }

  /**
   * Generate a cache key for detail metrics based on query parameters
   */
  private getDetailMetricsCacheKey(params: DetailMetricsParams): string {
    const { timeRange, startDate, endDate, brandId, segment } = params
    const seg = segment || "all"
    if (timeRange === "custom") {
      return `dashboard_detail_custom_${startDate}_${endDate}_${brandId}_${seg}`
    }
    return `dashboard_detail_${timeRange}_${brandId}_${seg}`
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

    if (params.segment) {
      queryParams.append("segment", params.segment)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/detail-metrics?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
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
      headers: await this.getAuthHeaders(),
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
    const { timeRange, startDate, endDate, brandId, competitorBrandName, segment } = params
    const seg = segment || "all"
    if (timeRange === "custom") {
      return `dashboard_comp_metrics_custom_${startDate}_${endDate}_${brandId}_${competitorBrandName}_${seg}`
    }
    return `dashboard_comp_metrics_${timeRange}_${brandId}_${competitorBrandName}_${seg}`
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

    if (params.segment) {
      queryParams.append("segment", params.segment)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/competitor-metrics?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
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

  /**
   * Generate a cache key for brand overview
   */
  private getBrandOverviewCacheKey(params: BrandOverviewParams): string {
    const { timeRange, startDate, endDate, brandId, segment } = params
    const seg = segment || "All-Segment"
    if (timeRange === "custom") {
      return `dashboard_overview_custom_${startDate}_${endDate}_${brandId}_${seg}`
    }
    return `dashboard_overview_${timeRange}_${brandId}_${seg}`
  }

  /**
   * Fetch brand overview data (metric summaries + time series)
   */
  async getBrandOverview(
    params: BrandOverviewParams,
    forceRefresh: boolean = false,
  ): Promise<BrandOverviewResponse> {
    const cacheKey = this.getBrandOverviewCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<BrandOverviewResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching brand overview from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("Start date and end date are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    if (params.segment) {
      queryParams.append("segment", params.segment)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/brand-overview?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch brand overview")
    }

    const data: BrandOverviewResponse = await response.json()
    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Brand overview fetched successfully", {
      dataPoints: data.data_points.length,
      brandName: data.brand_name,
    })

    return data
  }

  /**
   * Generate a cache key for segment metrics
   */
  private getSegmentMetricsCacheKey(params: SegmentMetricsParams): string {
    const { timeRange, startDate, endDate, brandId } = params
    if (timeRange === "custom") {
      return `dashboard_seg_metrics_custom_${startDate}_${endDate}_${brandId}`
    }
    return `dashboard_seg_metrics_${timeRange}_${brandId}`
  }

  /**
   * Fetch per-segment metrics breakdown
   */
  async getSegmentMetrics(
    params: SegmentMetricsParams,
    forceRefresh: boolean = false,
  ): Promise<SegmentMetricsResponse> {
    const cacheKey = this.getSegmentMetricsCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<SegmentMetricsResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching segment metrics from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("Start date and end date are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/segment-metrics?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch segment metrics")
    }

    const data: SegmentMetricsResponse = await response.json()
    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Segment metrics fetched successfully", {
      segments: data.segments.length,
    })

    return data
  }

  /**
   * Generate a cache key for performance detail table
   */
  private getPerformanceDetailTableCacheKey(params: PerformanceDetailTableParams): string {
    const { timeRange, startDate, endDate, brandId } = params
    if (timeRange === "custom") {
      return `dashboard_perf_detail_custom_${startDate}_${endDate}_${brandId}`
    }
    return `dashboard_perf_detail_${timeRange}_${brandId}`
  }

  /**
   * Fetch performance detail table data (all segment rows with dates)
   */
  async getPerformanceDetailTable(
    params: PerformanceDetailTableParams,
    forceRefresh: boolean = false,
  ): Promise<PerformanceDetailTableResponse> {
    const cacheKey = this.getPerformanceDetailTableCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<PerformanceDetailTableResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching performance detail table from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("Start date and end date are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/performance-detail-table?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch performance detail table")
    }

    const data: PerformanceDetailTableResponse = await response.json()
    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Performance detail table fetched successfully", {
      rows: data.rows.length,
    })

    return data
  }

  /**
   * Generate a cache key for competitor awareness
   */
  private getCompetitorAwarenessCacheKey(params: CompetitorAwarenessParams): string {
    const { timeRange, startDate, endDate, brandId, competitorBrandName, segment } = params
    if (timeRange === "custom") {
      return `dashboard_comp_aware_custom_${startDate}_${endDate}_${brandId}_${competitorBrandName}_${segment}`
    }
    return `dashboard_comp_aware_${timeRange}_${brandId}_${competitorBrandName}_${segment}`
  }

  /**
   * Fetch competitor awareness time series (5 metrics)
   */
  async getCompetitorAwareness(
    params: CompetitorAwarenessParams,
    forceRefresh: boolean = false,
  ): Promise<CompetitorAwarenessResponse> {
    const cacheKey = this.getCompetitorAwarenessCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorAwarenessResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching competitor awareness from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("competitor_brand_name", params.competitorBrandName)
    queryParams.append("time_range", params.timeRange)
    queryParams.append("segment", params.segment)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("Start date and end date are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/competitor-awareness?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitor awareness")
    }

    const data: CompetitorAwarenessResponse = await response.json()
    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Competitor awareness fetched successfully", {
      dataPoints: data.data_points.length,
    })

    return data
  }

  /**
   * Generate a cache key for competitor detail table
   */
  private getCompetitorDetailTableCacheKey(params: CompetitorDetailTableParams): string {
    const { timeRange, startDate, endDate, brandId, competitorBrandName } = params
    if (timeRange === "custom") {
      return `dashboard_comp_detail_custom_${startDate}_${endDate}_${brandId}_${competitorBrandName}`
    }
    return `dashboard_comp_detail_${timeRange}_${brandId}_${competitorBrandName}`
  }

  /**
   * Fetch competitor detail table data (all segment rows with dates and segment gap)
   */
  async getCompetitorDetailTable(
    params: CompetitorDetailTableParams,
    forceRefresh: boolean = false,
  ): Promise<CompetitorDetailTableResponse> {
    const cacheKey = this.getCompetitorDetailTableCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorDetailTableResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching competitor detail table from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("competitor_brand_name", params.competitorBrandName)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("Start date and end date are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/competitor-detail-table?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitor detail table")
    }

    const data: CompetitorDetailTableResponse = await response.json()
    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Competitor detail table fetched successfully", {
      rows: data.rows.length,
    })

    return data
  }

  /**
   * Generate a cache key for top competitor
   */
  private getTopCompetitorCacheKey(params: TopCompetitorParams): string {
    const { timeRange, startDate, endDate, brandId, segment } = params
    if (timeRange === "custom") {
      return `dashboard_top_comp_custom_${startDate}_${endDate}_${brandId}_${segment}`
    }
    return `dashboard_top_comp_${timeRange}_${brandId}_${segment}`
  }

  /**
   * Fetch top competitor by awareness score for a brand + segment + time range
   */
  async getTopCompetitor(
    params: TopCompetitorParams,
    forceRefresh: boolean = false,
  ): Promise<TopCompetitorResponse> {
    const cacheKey = this.getTopCompetitorCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<TopCompetitorResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching top competitor from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("segment", params.segment)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("Start date and end date are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/top-competitor?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch top competitor")
    }

    const data: TopCompetitorResponse = await response.json()
    this.setCachedData(cacheKey, data)

    console.log("[DashboardAPI] Top competitor fetched successfully", {
      topCompetitor: data.top_competitor_name,
    })

    return data
  }

  // ── Risk Overview (Insight page) ──────────────────────────────

  private getRiskOverviewCacheKey(params: RiskOverviewParams): string {
    return `dashboard_risk_overview_${params.brandId}_${params.segment}`
  }

  async getRiskOverview(
    params: RiskOverviewParams,
    forceRefresh = false,
  ): Promise<BrandRiskOverviewResponse> {
    const cacheKey = this.getRiskOverviewCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<BrandRiskOverviewResponse>(cacheKey)
      if (cached) {
        console.log("[DashboardAPI] Returning cached risk overview")
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching risk overview from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("segment", params.segment)

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/risk-overview?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch risk overview")
    }

    const data: BrandRiskOverviewResponse = await response.json()
    this.setCachedData(cacheKey, data)

    return data
  }

  // ── Risk History (Insight page chart) ─────────────────────────

  private getRiskHistoryCacheKey(params: RiskHistoryParams): string {
    return `dashboard_risk_history_${params.brandId}_${params.segment}_${params.timeRange}_${params.startDate || ""}_${params.endDate || ""}`
  }

  async getRiskHistory(
    params: RiskHistoryParams,
    forceRefresh = false,
  ): Promise<RiskHistoryResponse> {
    const cacheKey = this.getRiskHistoryCacheKey(params)

    if (!forceRefresh) {
      const cached = this.getCachedData<RiskHistoryResponse>(cacheKey)
      if (cached) {
        console.log("[DashboardAPI] Returning cached risk history")
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching risk history from API...", params)

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", params.brandId)
    queryParams.append("segment", params.segment)
    queryParams.append("time_range", params.timeRange)

    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("Start date and end date are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/risk-history?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch risk history")
    }

    const data: RiskHistoryResponse = await response.json()
    this.setCachedData(cacheKey, data)

    return data
  }

  // ── Brand Impression Summary ───────────────────────────────────

  private getBrandImpressionSummaryCacheKey(brandId: string, segment: string): string {
    return `dashboard_brand_impression_summary_${brandId}_${segment}`
  }

  async getBrandImpressionSummary(
    brandId: string,
    segment: string,
    forceRefresh = false,
  ): Promise<BrandImpressionSummaryResponse> {
    const cacheKey = this.getBrandImpressionSummaryCacheKey(brandId, segment)

    if (!forceRefresh) {
      const cached = this.getCachedData<BrandImpressionSummaryResponse>(cacheKey)
      if (cached) {
        return cached
      }
    }

    console.log("[DashboardAPI] Fetching brand impression summary from API...", { brandId, segment })

    const queryParams = new URLSearchParams()
    queryParams.append("brand_id", brandId)
    queryParams.append("segment", segment || "all-segment")

    const url = `${this.baseUrl}${this.apiPrefix}/dashboard/brand-impression-summary?${queryParams.toString()}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch brand impression summary")
    }

    const data: BrandImpressionSummaryResponse = await response.json()
    this.setCachedData(cacheKey, data)

    return data
  }

  async getBrandRankingTrend(
    params: BrandRankingTrendParams,
    forceRefresh = false,
  ): Promise<BrandRankingTrendResponse> {
    const cacheKey = `dashboard_brand_ranking_trend_${params.brandId}_${params.segment}_${params.timeRange}_${params.startDate ?? ""}_${params.endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<BrandRankingTrendResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({
      brand_id: params.brandId,
      segment: params.segment || "all-segment",
      time_range: params.timeRange,
    })
    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("startDate and endDate are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/brand-ranking-trend?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch brand ranking trend")
    }

    const data: BrandRankingTrendResponse = await response.json()
    // Only cache non-empty responses; empty means no data yet and shouldn't be served stale
    if (data.data_points.length > 0) {
      this.setCachedData(cacheKey, data)
    }
    return data
  }

  async getBrandImpressionTrend(
    params: BrandImpressionTrendParams,
    forceRefresh = false,
  ): Promise<BrandImpressionTrendResponse> {
    const cacheKey = `dashboard_brand_impression_trend_${params.brandId}_${params.segment}_${params.timeRange}_${params.startDate ?? ""}_${params.endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<BrandImpressionTrendResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({
      brand_id: params.brandId,
      segment: params.segment || "all-segment",
      time_range: params.timeRange,
    })
    if (params.timeRange === "custom") {
      if (!params.startDate || !params.endDate) {
        throw new Error("startDate and endDate are required for custom time range")
      }
      queryParams.append("start_date", params.startDate)
      queryParams.append("end_date", params.endDate)
    }

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/brand-impression-trend?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch brand impression trend")
    }

    const data: BrandImpressionTrendResponse = await response.json()
    // Only cache non-empty responses; empty means no data yet and shouldn't be served stale
    if (data.data_points.length > 0) {
      this.setCachedData(cacheKey, data)
    }
    return data
  }

  async getBrandReferenceSources({
    brandId,
    segment,
    timeRange,
    startDate,
    endDate,
    forceRefresh = false,
  }: {
    brandId: string
    segment?: string
    timeRange: TimeRange
    startDate?: string
    endDate?: string
    forceRefresh?: boolean
  }): Promise<ReferenceSourcesResponse> {
    const cacheKey = `dashboard_brand_reference_sources_${brandId}_${segment ?? ""}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<ReferenceSourcesResponse>(cacheKey)
      if (cached) return cached
    }

    const params = new URLSearchParams({ brand_id: brandId, time_range: timeRange })
    if (segment) params.append("segment", segment)
    if (startDate) params.append("start_date", startDate)
    if (endDate) params.append("end_date", endDate)

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/brand-reference-sources?${params}`,
      { headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch reference sources")
    }
    const data: ReferenceSourcesResponse = await response.json()
    this.setCachedData(cacheKey, data)
    return data
  }

  async getBrandCustomerReviews({
    brandId,
    segment,
    timeRange,
    startDate,
    endDate,
    forceRefresh = false,
  }: {
    brandId: string
    segment?: string
    timeRange: TimeRange
    startDate?: string
    endDate?: string
    forceRefresh?: boolean
  }): Promise<CustomerReviewsResponse> {
    const cacheKey = `dashboard_brand_customer_reviews_${brandId}_${segment ?? ""}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<CustomerReviewsResponse>(cacheKey)
      if (cached) return cached
    }

    const params = new URLSearchParams({ brand_id: brandId, time_range: timeRange })
    if (segment) params.append("segment", segment)
    if (startDate) params.append("start_date", startDate)
    if (endDate) params.append("end_date", endDate)

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/brand-customer-reviews?${params}`,
      { headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch customer reviews")
    }
    const data: CustomerReviewsResponse = await response.json()
    this.setCachedData(cacheKey, data)
    return data
  }

  /**
   * Fetch reference sources across ALL individual segments, merge and deduplicate.
   * Individual segment responses are each cached (10h). The merged result is also
   * cached separately so subsequent calls are instant.
   */
  async getBrandReferenceSourcesAllSegments({
    brandId,
    segments,
    timeRange,
    startDate,
    endDate,
    forceRefresh = false,
  }: {
    brandId: string
    segments: string[]
    timeRange: TimeRange
    startDate?: string
    endDate?: string
    forceRefresh?: boolean
  }): Promise<ReferenceSourcesResponse> {
    const cacheKey = `dashboard_brand_reference_sources_all_${brandId}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<ReferenceSourcesResponse>(cacheKey)
      if (cached) return cached
    }

    // Fetch each segment (individually cached); run in parallel
    const results = await Promise.all(
      segments.map((seg) =>
        this.getBrandReferenceSources({ brandId, segment: seg, timeRange, startDate, endDate }),
      ),
    )

    // Merge and deduplicate by normalized URL
    const normalizeUrl = (url: string): string => {
      let u = url.toLowerCase().trim()
      for (const pfx of ["https://", "http://"]) {
        if (u.startsWith(pfx)) { u = u.slice(pfx.length); break }
      }
      if (u.startsWith("www.")) u = u.slice(4)
      return u.replace(/\/+$/, "")
    }

    const seenKeys = new Set<string>()
    const merged: { source: string }[] = []
    for (const res of results) {
      for (const item of res.sources) {
        const key = normalizeUrl(item.source)
        if (key && !seenKeys.has(key)) {
          seenKeys.add(key)
          merged.push({ source: item.source })
        }
      }
    }

    const data: ReferenceSourcesResponse = {
      brand_id: brandId,
      sources: merged.map((m, i) => ({ seq: i + 1, source: m.source })),
    }
    this.setCachedData(cacheKey, data)
    return data
  }

  /**
   * Fetch customer reviews across ALL individual segments, merge and deduplicate.
   * Individual segment responses are each cached (10h). The merged result is also
   * cached separately so subsequent calls are instant.
   */
  async getBrandCustomerReviewsAllSegments({
    brandId,
    segments,
    timeRange,
    startDate,
    endDate,
    forceRefresh = false,
  }: {
    brandId: string
    segments: string[]
    timeRange: TimeRange
    startDate?: string
    endDate?: string
    forceRefresh?: boolean
  }): Promise<CustomerReviewsResponse> {
    const cacheKey = `dashboard_brand_customer_reviews_all_${brandId}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<CustomerReviewsResponse>(cacheKey)
      if (cached) return cached
    }

    // Fetch each segment (individually cached); run in parallel
    const results = await Promise.all(
      segments.map((seg) =>
        this.getBrandCustomerReviews({ brandId, segment: seg, timeRange, startDate, endDate }),
      ),
    )

    // Merge and deduplicate by normalized review text
    const seenKeys = new Set<string>()
    const merged: { review: string; sentiment: "Positive" | "Neutral" | "Negative" }[] = []
    for (const res of results) {
      for (const item of res.reviews) {
        const key = item.review.toLowerCase().trim()
        if (key && !seenKeys.has(key)) {
          seenKeys.add(key)
          merged.push({ review: item.review, sentiment: item.sentiment })
        }
      }
    }

    const data: CustomerReviewsResponse = {
      brand_id: brandId,
      reviews: merged.map((m, i) => ({ seq: i + 1, review: m.review, sentiment: m.sentiment })),
    }
    this.setCachedData(cacheKey, data)
    return data
  }

  // ── Competitors by segment ─────────────────────────────────────────────────

  async getCompetitorsBySegment(
    brandId: string,
    segment: string,
    forceRefresh = false,
  ): Promise<CompetitorsBySegmentResponse> {
    const cacheKey = `dashboard_competitors_by_segment_${brandId}_${segment}`

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorsBySegmentResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({ brand_id: brandId, segment })
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/competitors-by-segment?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitors by segment")
    }

    const data: CompetitorsBySegmentResponse = await response.json()
    this.setCachedData(cacheKey, data)
    return data
  }

  // ── Competitor gap historical trend ───────────────────────────────────────

  async getCompetitorGapTrend(
    brandId: string,
    segment: string,
    competitorBrandName: string,
    timeRange: TimeRange,
    startDate?: string,
    endDate?: string,
    forceRefresh = false,
  ): Promise<CompetitorGapTrendResponse> {
    const cacheKey = `dashboard_competitor_gap_trend_v2_${brandId}_${segment}_${competitorBrandName}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorGapTrendResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({
      brand_id: brandId,
      segment,
      competitor_brand_name: competitorBrandName,
      time_range: timeRange,
    })
    if (timeRange === "custom") {
      if (!startDate || !endDate) throw new Error("startDate and endDate required for custom range")
      queryParams.append("start_date", startDate)
      queryParams.append("end_date", endDate)
    }

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/competitor-gap-trend?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitor gap trend")
    }

    const data: CompetitorGapTrendResponse = await response.json()
    if (data.data_points.length > 0) this.setCachedData(cacheKey, data)
    return data
  }

  // ── Competitor ranking detail ──────────────────────────────────────────────

  async getCompetitorRankingDetail(
    brandId: string,
    segment: string,
    competitorBrandName: string,
    timeRange: TimeRange,
    startDate?: string,
    endDate?: string,
    forceRefresh = false,
  ): Promise<CompetitorRankingDetailResponse> {
    const cacheKey = `dashboard_competitor_ranking_detail_v3_${brandId}_${segment}_${competitorBrandName}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorRankingDetailResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({
      brand_id: brandId,
      segment,
      competitor_brand_name: competitorBrandName,
      time_range: timeRange,
    })
    if (timeRange === "custom") {
      if (!startDate || !endDate) throw new Error("startDate and endDate required for custom range")
      queryParams.append("start_date", startDate)
      queryParams.append("end_date", endDate)
    }

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/competitor-ranking-detail?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitor ranking detail")
    }

    const data: CompetitorRankingDetailResponse = await response.json()
    if (data.data_points.length > 0) this.setCachedData(cacheKey, data)
    return data
  }

  // ── Reference source comparison ───────────────────────────────────────────

  async getReferenceSourceComparison(
    brandId: string,
    segment: string,
    competitorBrandName: string,
    timeRange: TimeRange,
    startDate?: string,
    endDate?: string,
    forceRefresh = false,
  ): Promise<ReferenceSourceComparisonResponse> {
    const cacheKey = `dashboard_ref_source_comparison_${brandId}_${segment}_${competitorBrandName}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<ReferenceSourceComparisonResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({
      brand_id: brandId,
      segment,
      competitor_brand_name: competitorBrandName,
      time_range: timeRange,
    })
    if (timeRange === "custom") {
      if (!startDate || !endDate) throw new Error("startDate and endDate required for custom range")
      queryParams.append("start_date", startDate)
      queryParams.append("end_date", endDate)
    }

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/reference-source-comparison?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch reference source comparison")
    }

    const data: ReferenceSourceComparisonResponse = await response.json()
    if (data.rows.length > 0) this.setCachedData(cacheKey, data)
    return data
  }

  // ── Sentiment comparison ───────────────────────────────────────────────────

  async getSentimentComparison(
    brandId: string,
    segment: string,
    competitorBrandName: string,
    timeRange: TimeRange,
    startDate?: string,
    endDate?: string,
    forceRefresh = false,
  ): Promise<SentimentComparisonResponse> {
    const cacheKey = `dashboard_sentiment_comparison_${brandId}_${segment}_${competitorBrandName}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<SentimentComparisonResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({
      brand_id: brandId,
      segment,
      competitor_brand_name: competitorBrandName,
      time_range: timeRange,
    })
    if (timeRange === "custom") {
      if (!startDate || !endDate) throw new Error("startDate and endDate required for custom range")
      queryParams.append("start_date", startDate)
      queryParams.append("end_date", endDate)
    }

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/sentiment-comparison?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch sentiment comparison")
    }

    const data: SentimentComparisonResponse = await response.json()
    if (data.rows.length > 0) this.setCachedData(cacheKey, data)
    return data
  }

  // ── Competitor gap summary ─────────────────────────────────────────────────

  async getCompetitorGapSummary(
    brandId: string,
    segment: string,
    competitorBrandName: string,
    forceRefresh = false,
  ): Promise<CompetitorGapSummaryResponse> {
    const cacheKey = `dashboard_competitor_gap_summary_${brandId}_${segment}_${competitorBrandName}`

    if (!forceRefresh) {
      const cached = this.getCachedData<CompetitorGapSummaryResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({
      brand_id: brandId,
      segment,
      competitor_brand_name: competitorBrandName,
    })
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/competitor-gap-summary?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch competitor gap summary")
    }

    const data: CompetitorGapSummaryResponse = await response.json()
    this.setCachedData(cacheKey, data)
    return data
  }

  // ── Market dynamic ─────────────────────────────────────────────────────────

  async getMarketDynamic(
    brandId: string,
    segment: string,
    timeRange: TimeRange,
    startDate?: string,
    endDate?: string,
    forceRefresh = false,
  ): Promise<MarketDynamicResponse> {
    const cacheKey = `dashboard_market_dynamic_${brandId}_${segment}_${timeRange}_${startDate ?? ""}_${endDate ?? ""}`

    if (!forceRefresh) {
      const cached = this.getCachedData<MarketDynamicResponse>(cacheKey)
      if (cached) return cached
    }

    const queryParams = new URLSearchParams({ brand_id: brandId, segment, time_range: timeRange })
    if (startDate) queryParams.set("start_date", startDate)
    if (endDate) queryParams.set("end_date", endDate)

    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/dashboard/market-dynamic?${queryParams}`,
      { method: "GET", headers: await this.getAuthHeaders() },
    )
    if (response.status === 401) throw new Error("Unauthorized - Please log in again")
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch market dynamic data")
    }

    const data: MarketDynamicResponse = await response.json()
    if (data.brands.length > 0) this.setCachedData(cacheKey, data)
    return data
  }
}

// Export singleton instance for use throughout the application
export const dashboardAPI = new DashboardAPI()
