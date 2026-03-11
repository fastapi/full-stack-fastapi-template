/**
 * BrandAwarenessScoreGaugeView Component
 *
 * This component displays the current brand consistency index with:
 * - Large index number with trend indicator
 * - Health gauge visualization (0-10 scale)
 * - Color-coded legend for index interpretation
 *
 * Data is fetched from the backend API and cached locally for 10 hours
 * to minimize unnecessary API calls when navigating between pages.
 *
 * Index Health Levels:
 * - Low: 0-3 (Red)
 * - Moderate: 3-5 (Yellow/Orange)
 * - Good: 5-7 (Lime)
 * - High: 7-10 (Green)
 */

import { Loader2, Minus, TrendingDown, TrendingUp } from "lucide-react"
import { useEffect, useState } from "react"
import {
  type ConsistencyIndexResponse,
  dashboardAPI,
} from "@/clients/dashboard"

/**
 * Props interface for the GaugeChart component
 */
interface GaugeChartProps {
  value: number // Index value (0-10 scale)
  max?: number // Maximum value for the gauge (default: 10)
}

interface BrandAwarenessScoreGaugeViewProps {
  brandId?: string
  segment?: string
}

export function BrandAwarenessScoreGaugeView({
  brandId,
  segment = "All-Segment",
}: BrandAwarenessScoreGaugeViewProps) {
  // ============================================================================
  // State Management
  // ============================================================================

  // Store the consistency index data from API
  const [indexData, setIndexData] = useState<ConsistencyIndexResponse | null>(
    null,
  )

  // Loading state for showing spinner during API call
  const [isLoading, setIsLoading] = useState<boolean>(true)

  // Error state for displaying error messages
  const [error, setError] = useState<string | null>(null)

  // ============================================================================
  // Data Fetching
  // ============================================================================

  /**
   * Fetch consistency index data when component mounts
   *
   * The dashboardAPI.getConsistencyIndex() method handles caching internally:
   * - First checks localStorage for cached data
   * - If cache is valid (< 10 hours old), returns cached data
   * - Otherwise, makes API call and caches the result
   */
  useEffect(() => {
    const fetchConsistencyIndex = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Fetch data from API (with automatic caching)
        // The API client will return cached data if available and not expired
        const data = await dashboardAPI.getConsistencyIndex(brandId, segment)

        // Update state with fetched data
        setIndexData(data)

        console.log("[BrandAwarenessScoreGaugeView] Data loaded:", data)
      } catch (err) {
        // Handle errors gracefully
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to load consistency index"
        setError(errorMessage)
        console.error("[BrandAwarenessScoreGaugeView] Error:", err)
      } finally {
        // Always clear loading state
        setIsLoading(false)
      }
    }

    // Execute the fetch function
    fetchConsistencyIndex()
  }, [brandId, segment]) // Re-fetch when brandId or segment changes

  // ============================================================================
  // Trend Calculation Functions
  // ============================================================================

  /**
   * Determine the trend direction based on current and previous indices
   *
   * @returns 'up' | 'down' | 'flat' based on index comparison
   */
  const getTrend = (): "up" | "down" | "flat" => {
    // If no data or no previous index, return flat
    if (
      !indexData ||
      !indexData.has_previous ||
      indexData.previous_normalized_index === null
    ) {
      return "flat"
    }

    const diff =
      indexData.normalized_index - indexData.previous_normalized_index

    // Use threshold to avoid showing trend for tiny changes
    if (Math.abs(diff) < 0.05) return "flat"
    return diff > 0 ? "up" : "down"
  }

  /**
   * Get the appropriate trend icon component based on trend direction
   *
   * @returns React component for the trend icon
   */
  const getTrendIcon = () => {
    const trend = getTrend()
    const iconClass = "h-6 w-6"

    switch (trend) {
      case "up":
        return <TrendingUp className={`${iconClass} text-green-600`} />
      case "down":
        return <TrendingDown className={`${iconClass} text-red-600`} />
      default:
        return <Minus className={`${iconClass} text-slate-600`} />
    }
  }

  /**
   * Get the CSS color class for the trend text
   *
   * @returns Tailwind CSS class for text color
   */
  const getTrendColor = (): string => {
    const trend = getTrend()
    switch (trend) {
      case "up":
        return "text-green-600"
      case "down":
        return "text-red-600"
      default:
        return "text-slate-600"
    }
  }

  /**
   * Calculate the index difference for display
   *
   * @returns The absolute difference between current and previous indices
   */
  const getIndexDiff = (): number => {
    if (
      !indexData ||
      !indexData.has_previous ||
      indexData.previous_normalized_index === null
    ) {
      return 0
    }
    return Math.abs(
      indexData.normalized_index - indexData.previous_normalized_index,
    )
  }

  // ============================================================================
  // Gauge Chart Component
  // ============================================================================

  /**
   * GaugeChart - Semi-circular gauge visualization
   *
   * Displays an index on a colored arc with:
   * - Gradient background from red to green
   * - Animated needle pointing to current value
   * - Scale markers (0, 2, 4, 6, 8, 10)
   *
   * @param value - The index to display (0-10 scale)
   * @param max - Maximum value for the gauge (default: 10)
   */
  const GaugeChart = ({ value, max = 10 }: GaugeChartProps) => {
    // Calculate percentage for arc fill
    const percentage = (value / max) * 100

    // Calculate needle rotation angle (-90 to 90 degrees)
    const rotation = (percentage / 100) * 180 - 90

    /**
     * Get color based on index value
     * Matches the health level definitions:
     * - Low (0-3): Red
     * - Moderate (3-5): Orange/Yellow
     * - Good (5-7): Lime
     * - High (7-10): Green
     */
    const getColor = (val: number): string => {
      const ratio = val / max
      if (ratio < 0.3) return "#ef4444" // Red - Low
      if (ratio < 0.5) return "#f59e0b" // Orange - Moderate
      if (ratio < 0.7) return "#eab308" // Yellow/Lime - Good
      if (ratio < 0.85) return "#84cc16" // Light green
      return "#22c55e" // Green - High
    }

    return (
      <div className="relative w-64 h-32 mx-auto">
        <svg viewBox="0 0 200 100" className="w-full h-full">
          <title>Brand awareness score gauge</title>
          {/* Background arc - gray track */}
          <path
            d="M 20 90 A 80 80 0 0 1 180 90"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="20"
            strokeLinecap="round"
          />

          {/* Gradient definition for the colored arc */}
          <defs>
            <linearGradient
              id="gaugeGradientConsistency"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="0%"
            >
              <stop offset="0%" stopColor="#ef4444" /> {/* Red */}
              <stop offset="25%" stopColor="#f59e0b" /> {/* Orange */}
              <stop offset="50%" stopColor="#eab308" /> {/* Yellow */}
              <stop offset="75%" stopColor="#84cc16" /> {/* Lime */}
              <stop offset="100%" stopColor="#22c55e" /> {/* Green */}
            </linearGradient>
          </defs>

          {/* Colored arc - fills based on percentage */}
          <path
            d="M 20 90 A 80 80 0 0 1 180 90"
            fill="none"
            stroke="url(#gaugeGradientConsistency)"
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 2.51}, 1000`}
          />

          {/* Indicator needle - points to current value */}
          <line
            x1="100"
            y1="90"
            x2="100"
            y2="30"
            stroke={getColor(value)}
            strokeWidth="3"
            strokeLinecap="round"
            transform={`rotate(${rotation} 100 90)`}
          />

          {/* Center circle - needle base */}
          <circle cx="100" cy="90" r="8" fill={getColor(value)} />

          {/* Scale markers - numbers around the arc */}
          {[0, 2, 4, 6, 8, 10].map((num) => {
            const angle = (num / max) * 180 - 90
            const rad = (angle * Math.PI) / 180
            const x = 100 + 75 * Math.cos(rad)
            const y = 90 + 75 * Math.sin(rad)
            return (
              <text
                key={num}
                x={x}
                y={y + 5}
                textAnchor="middle"
                className="text-xs fill-slate-600"
              >
                {num}
              </text>
            )
          })}
        </svg>
      </div>
    )
  }

  // ============================================================================
  // Loading State Render
  // ============================================================================

  if (isLoading) {
    return (
      <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
        <div className="flex justify-start">
          <h3 className="text-base font-semibold mb-4 text-slate-900">
            Current Consistency Index
          </h3>
        </div>
        {/* Loading spinner centered in the card */}
        <div className="flex flex-col items-center justify-center h-64">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-sm text-slate-500">
            Loading consistency index...
          </p>
        </div>
      </div>
    )
  }

  // ============================================================================
  // Error State Render
  // ============================================================================

  if (error) {
    return (
      <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
        <div className="flex justify-start">
          <h3 className="text-base font-semibold mb-4 text-slate-900">
            Current Consistency Index
          </h3>
        </div>
        {/* Error message centered in the card */}
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-red-500 text-center">
            <p className="font-medium">Failed to load data</p>
            <p className="text-sm mt-2">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  // ============================================================================
  // No Data State Render
  // ============================================================================

  if (!indexData) {
    return (
      <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
        <div className="flex justify-start">
          <h3 className="text-base font-semibold mb-4 text-slate-900">
            Current Consistency Index
          </h3>
        </div>
        {/* No data message centered in the card */}
        <div className="flex flex-col items-center justify-center h-64">
          <p className="text-slate-500">No consistency index data available</p>
        </div>
      </div>
    )
  }

  // ============================================================================
  // Main Render with Data
  // ============================================================================

  return (
    /* Current Consistency Index */
    <div className="rounded-2xl bg-white p-6 border border-slate-200 h-full w-full shadow-sm">
      <div className="flex justify-start">
        <h3 className="text-base font-semibold mb-4 text-slate-900">
          Current Consistency Index
        </h3>
      </div>

      {/* Index and Trend */}
      <div className="flex items-center justify-center gap-4 mb-6">
        <div className="text-6xl font-bold text-blue-600">
          {indexData.normalized_index.toFixed(1)}
        </div>
        <div className="flex flex-col items-center">
          {getTrendIcon()}
          <span className={`text-sm font-medium ${getTrendColor()}`}>
            {getIndexDiff().toFixed(2)}
          </span>
        </div>
      </div>
      <p className="text-center text-sm text-slate-500 mb-6">
        {getTrend() === "up"
          ? "Improving"
          : getTrend() === "down"
            ? "Declining"
            : "Stable"}{" "}
        from previous period
      </p>

      {/* Consistency Gauge */}
      <GaugeChart value={indexData.normalized_index} max={10} />
      <div className="flex justify-center gap-6 mt-4 text-xs flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span>Low (0-3)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <span>Moderate (3-5)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-lime-500" />
          <span>Good (5-7)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span>High (7-10)</span>
        </div>
      </div>
    </div>
  )
}
