import { useCallback, useEffect, useState } from "react"

/**
 * Hook state interface
 */
export interface PDFNavigationState {
  currentPage: number
  totalPages: number
  zoomLevel: number
  zoomMode: "fitWidth" | "fitHeight" | "percentage"
}

/**
 * Hook actions interface
 */
export interface PDFNavigationActions {
  goToPage: (page: number) => void
  nextPage: () => void
  previousPage: () => void
  zoomIn: () => void
  zoomOut: () => void
  setZoomMode: (mode: "fitWidth" | "fitHeight") => void
  setZoomPercentage: (percentage: number) => void
}

/**
 * Hook return type
 */
export type UsePDFNavigationReturn = PDFNavigationState & PDFNavigationActions

// Constants
const MIN_ZOOM = 50
const MAX_ZOOM = 300
const ZOOM_STEP = 25
const DEFAULT_ZOOM = 100

/**
 * Custom hook for managing PDF navigation and zoom state
 *
 * @param initialPage - Initial page number (default: 1)
 * @param totalPages - Total number of pages in PDF
 * @param onPageChange - Optional callback triggered when page changes
 * @returns Navigation state and action functions
 */
export function usePDFNavigation(
  initialPage: number = 1,
  totalPages: number = 0,
  onPageChange?: (page: number) => void,
): UsePDFNavigationReturn {
  // Validate and set initial page
  const validInitialPage = initialPage > totalPages && totalPages > 0 ? 1 : initialPage

  // State management
  const [currentPage, setCurrentPage] = useState(validInitialPage)
  const [zoomLevel, setZoomLevel] = useState(DEFAULT_ZOOM)
  const [zoomMode, setZoomModeState] = useState<"fitWidth" | "fitHeight" | "percentage">("fitWidth")

  // Update current page when totalPages changes (for dynamic PDF loading)
  useEffect(() => {
    // If current page is now invalid after totalPages change, adjust it
    if (totalPages > 0 && currentPage > totalPages) {
      setCurrentPage(totalPages)
    }
  }, [totalPages, currentPage])

  /**
   * Navigate to specific page
   */
  const goToPage = useCallback(
    (page: number) => {
      // Validate page number
      if (totalPages === 0) {
        return // Do nothing if no pages
      }

      if (page < 1 || page > totalPages) {
        // Invalid page number - ignore
        return
      }

      setCurrentPage(page)
      onPageChange?.(page)
    },
    [totalPages, onPageChange],
  )

  /**
   * Navigate to next page
   */
  const nextPage = useCallback(() => {
    if (totalPages === 0) {
      return // Do nothing if no pages
    }

    if (currentPage < totalPages) {
      const newPage = currentPage + 1
      setCurrentPage(newPage)
      onPageChange?.(newPage)
    }
    // If already at last page, do nothing (boundary check)
  }, [currentPage, totalPages, onPageChange])

  /**
   * Navigate to previous page
   */
  const previousPage = useCallback(() => {
    if (totalPages === 0) {
      return // Do nothing if no pages
    }

    if (currentPage > 1) {
      const newPage = currentPage - 1
      setCurrentPage(newPage)
      onPageChange?.(newPage)
    }
    // If already at first page, do nothing (boundary check)
  }, [currentPage, totalPages, onPageChange])

  /**
   * Zoom in by 25%
   */
  const zoomIn = useCallback(() => {
    setZoomLevel((prev) => {
      const newZoom = Math.min(prev + ZOOM_STEP, MAX_ZOOM)
      return newZoom
    })
    setZoomModeState("percentage")
  }, [])

  /**
   * Zoom out by 25%
   */
  const zoomOut = useCallback(() => {
    setZoomLevel((prev) => {
      const newZoom = Math.max(prev - ZOOM_STEP, MIN_ZOOM)
      return newZoom
    })
    setZoomModeState("percentage")
  }, [])

  /**
   * Set zoom mode (fitWidth, fitHeight, or percentage)
   */
  const setZoomMode = useCallback((mode: "fitWidth" | "fitHeight") => {
    setZoomModeState(mode)
  }, [])

  /**
   * Set custom zoom percentage
   */
  const setZoomPercentage = useCallback((percentage: number) => {
    // Clamp to min/max bounds
    const clampedZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, percentage))
    setZoomLevel(clampedZoom)
    setZoomModeState("percentage")
  }, [])

  return {
    // State
    currentPage,
    totalPages,
    zoomLevel,
    zoomMode,
    // Actions
    goToPage,
    nextPage,
    previousPage,
    zoomIn,
    zoomOut,
    setZoomMode,
    setZoomPercentage,
  }
}
