/**
 * BrandAwarenessScoreCurrentScore Component
 *
 * This component displays the current brand awareness score with:
 * - Large score number with trend indicator
 * - Health gauge visualization (0-10 scale)
 * - Color-coded legend for score interpretation
 *
 * Data is fetched from the backend API and cached locally for 10 hours
 * to minimize unnecessary API calls when navigating between pages.
 *
 * Score Health Levels:
 * - Poor: 0-3 (Red)
 * - Fair: 3-5 (Yellow/Orange)
 * - Good: 5-7 (Lime)
 * - Excellent: 7-10 (Green)
 */

import { Loader2, Minus, TrendingDown, TrendingUp } from "lucide-react"
import { useEffect, useState } from "react"
import { type AwarenessScoreResponse, dashboardAPI } from "@/clients/dashboard"

/**
 * Props interface for the GaugeChart component
 */
interface GaugeChartProps {
  value: number // Score value (0-10 scale)
  max?: number // Maximum value for the gauge (default: 10)
}

interface BrandAwarenessScoreCurrentScoreProps {
  brandId?: string
}

export function BrandAwarenessScoreCurrentScore({ brandId }: BrandAwarenessScoreCurrentScoreProps) {
  // ============================================================================
  // State Management
  // ============================================================================

  // Store the awareness score data from API
  const [scoreData, setScoreData] = useState<AwarenessScoreResponse | null>(
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
   * Fetch awareness score data when component mounts
   *
   * The dashboardAPI.getAwarenessScore() method handles caching internally:
   * - First checks localStorage for cached data
   * - If cache is valid (< 10 hours old), returns cached data
   * - Otherwise, makes API call and caches the result
   */
  useEffect(() => {
    const fetchAwarenessScore = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Fetch data from API (with automatic caching)
        // The API client will return cached data if available and not expired
        const data = await dashboardAPI.getAwarenessScore(brandId)

        // Update state with fetched data
        setScoreData(data)

        console.log("[BrandAwarenessScoreCurrentScore] Data loaded:", data)
      } catch (err) {
        // Handle errors gracefully
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load awareness score"
        setError(errorMessage)
        console.error("[BrandAwarenessScoreCurrentScore] Error:", err)
      } finally {
        // Always clear loading state
        setIsLoading(false)
      }
    }

    // Execute the fetch function
    fetchAwarenessScore()
  }, [brandId]) // Re-fetch when brandId changes

  // ============================================================================
  // Trend Calculation Functions
  // ============================================================================

  /**
   * Determine the trend direction based on current and previous scores
   *
   * @returns 'up' | 'down' | 'flat' based on score comparison
   */
  const getTrend = (): "up" | "down" | "flat" => {
    // If no data or no previous score, return flat
    if (
      !scoreData ||
      !scoreData.has_previous ||
      scoreData.previous_normalized_score === null
    ) {
      return "flat"
    }

    const diff =
      scoreData.normalized_score - scoreData.previous_normalized_score

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
        return <Minus className={`${iconClass} text-gray-600`} />
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
        return "text-gray-600"
    }
  }

  /**
   * Calculate the score difference for display
   *
   * @returns The absolute difference between current and previous scores
   */
  const getScoreDiff = (): number => {
    if (
      !scoreData ||
      !scoreData.has_previous ||
      scoreData.previous_normalized_score === null
    ) {
      return 0
    }
    return Math.abs(
      scoreData.normalized_score - scoreData.previous_normalized_score,
    )
  }

  // ============================================================================
  // Gauge Chart Component
  // ============================================================================

  /**
   * GaugeChart - Semi-circular gauge visualization
   *
   * Displays a score on a colored arc with:
   * - Gradient background from red to green
   * - Animated needle pointing to current value
   * - Scale markers (0, 2, 4, 6, 8, 10)
   *
   * @param value - The score to display (0-10 scale)
   * @param max - Maximum value for the gauge (default: 10)
   */
  const GaugeChart = ({ value, max = 10 }: GaugeChartProps) => {
    // Calculate percentage for arc fill
    const percentage = (value / max) * 100

    // Calculate needle rotation angle (-90 to 90 degrees)
    const rotation = (percentage / 100) * 180 - 90

    /**
     * Get color based on score value
     * Matches the health level definitions:
     * - Poor (0-3): Red
     * - Fair (3-5): Orange/Yellow
     * - Good (5-7): Lime
     * - Excellent (7-10): Green
     */
    const getColor = (val: number): string => {
      const ratio = val / max
      if (ratio < 0.3) return "#ef4444" // Red - Poor
      if (ratio < 0.5) return "#f59e0b" // Orange - Fair
      if (ratio < 0.7) return "#eab308" // Yellow/Lime - Good
      if (ratio < 0.85) return "#84cc16" // Light green
      return "#22c55e" // Green - Excellent
    }

    return (
      <div className="relative w-64 h-32 mx-auto">
        <svg viewBox="0 0 200 100" className="w-full h-full">
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
              id="gaugeGradientScore"
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
            stroke="url(#gaugeGradientScore)"
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
                className="text-xs fill-gray-600"
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
      <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
        <div className="flex justify-start">
          <h3 className="text-md font-semibold mb-4">
            Current Awareness Score
          </h3>
        </div>
        {/* Loading spinner centered in the card */}
        <div className="flex flex-col items-center justify-center h-64">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          <p className="mt-4 text-sm text-gray-500">
            Loading awareness score...
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
      <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
        <div className="flex justify-start">
          <h3 className="text-md font-semibold mb-4">
            Current Awareness Score
          </h3>
        </div>
        {/* Error message with retry suggestion */}
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <div className="text-red-500 mb-2">
            <svg
              className="h-12 w-12 mx-auto"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <p className="text-sm text-red-600">{error}</p>
          <p className="text-xs text-gray-500 mt-2">
            Please try refreshing the page
          </p>
        </div>
      </div>
    )
  }

  // ============================================================================
  // No Data State Render
  // ============================================================================

  if (!scoreData) {
    return (
      <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
        <div className="flex justify-start">
          <h3 className="text-md font-semibold mb-4">
            Current Awareness Score
          </h3>
        </div>
        {/* No data message */}
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <p className="text-sm text-gray-500">
            No awareness score data available
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Data will appear once brand performance is tracked
          </p>
        </div>
      </div>
    )
  }

  // ============================================================================
  // Main Render - Data Available
  // ============================================================================

  return (
    <div className="rounded-md bg-gradient-to-b p-6 border border-gray-200 h-full w-full">
      {/* Section Header */}
      <div className="flex justify-start">
        <h3 className="text-md font-semibold mb-4">Current Awareness Score</h3>
      </div>

      {/* Score Display with Trend */}
      <div className="flex items-center justify-center gap-4 mb-6">
        {/* Large score number */}
        <div className="text-6xl font-bold text-blue-600">
          {scoreData.normalized_score.toFixed(1)}
        </div>

        {/* Trend indicator */}
        <div className="flex flex-col items-center">
          {getTrendIcon()}
          <span className={`text-sm font-medium ${getTrendColor()}`}>
            {getScoreDiff().toFixed(2)}
          </span>
        </div>
      </div>

      {/* Trend description text */}
      <p className="text-center text-sm text-gray-500 mb-6">
        {getTrend() === "up"
          ? "Improving"
          : getTrend() === "down"
            ? "Declining"
            : "Stable"}{" "}
        from previous period
      </p>

      {/* Health Gauge Visualization */}
      <GaugeChart value={scoreData.normalized_score} max={10} />

      {/* Legend for gauge colors */}
      <div className="flex justify-center gap-6 mt-4 text-xs flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span>Poor (0-3)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <span>Fair (3-5)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-lime-500" />
          <span>Good (5-7)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span>Excellent (7-10)</span>
        </div>
      </div>

      {/* Brand name and date info (subtle footer) */}
      <div className="mt-4 pt-4 border-t border-gray-100 text-center">
        <p className="text-xs text-gray-400">
          Brand: {scoreData.brand_name} | Updated: {scoreData.current_date}
        </p>
      </div>
    </div>
  )
}
