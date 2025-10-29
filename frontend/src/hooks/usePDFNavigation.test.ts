import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { usePDFNavigation } from "./usePDFNavigation"

describe("usePDFNavigation", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe("initial state", () => {
    it("should initialize with default values", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      expect(result.current.currentPage).toBe(1)
      expect(result.current.totalPages).toBe(10)
      expect(result.current.zoomLevel).toBe(100)
      expect(result.current.zoomMode).toBe("fitWidth")
    })

    it("should use custom initial page when provided", () => {
      const { result } = renderHook(() => usePDFNavigation(5, 10))

      expect(result.current.currentPage).toBe(5)
    })

    it("should handle initial page greater than totalPages by defaulting to page 1", () => {
      const { result } = renderHook(() => usePDFNavigation(15, 10))

      // According to error handling AC: invalid initial page > totalPages defaults to page 1
      expect(result.current.currentPage).toBe(1)
    })
  })

  describe("navigation - goToPage", () => {
    it("should navigate to valid page number", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.goToPage(5)
      })

      expect(result.current.currentPage).toBe(5)
    })

    it("should ignore invalid page numbers (0)", () => {
      const { result } = renderHook(() => usePDFNavigation(3, 10))

      act(() => {
        result.current.goToPage(0)
      })

      expect(result.current.currentPage).toBe(3) // Should remain unchanged
    })

    it("should ignore invalid page numbers (greater than totalPages)", () => {
      const { result } = renderHook(() => usePDFNavigation(3, 10))

      act(() => {
        result.current.goToPage(999)
      })

      expect(result.current.currentPage).toBe(3) // Should remain unchanged
    })

    it("should ignore negative page numbers", () => {
      const { result } = renderHook(() => usePDFNavigation(3, 10))

      act(() => {
        result.current.goToPage(-5)
      })

      expect(result.current.currentPage).toBe(3) // Should remain unchanged
    })

    it("should navigate to page 1 (boundary)", () => {
      const { result } = renderHook(() => usePDFNavigation(5, 10))

      act(() => {
        result.current.goToPage(1)
      })

      expect(result.current.currentPage).toBe(1)
    })

    it("should navigate to last page (boundary)", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.goToPage(10)
      })

      expect(result.current.currentPage).toBe(10)
    })
  })

  describe("navigation - nextPage", () => {
    it("should navigate to next page", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.nextPage()
      })

      expect(result.current.currentPage).toBe(2)
    })

    it("should not go beyond last page", () => {
      const { result } = renderHook(() => usePDFNavigation(10, 10))

      act(() => {
        result.current.nextPage()
      })

      expect(result.current.currentPage).toBe(10) // Should remain at last page
    })

    it("should increment multiple times correctly", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.nextPage()
      })
      act(() => {
        result.current.nextPage()
      })
      act(() => {
        result.current.nextPage()
      })

      expect(result.current.currentPage).toBe(4)
    })
  })

  describe("navigation - previousPage", () => {
    it("should navigate to previous page", () => {
      const { result } = renderHook(() => usePDFNavigation(5, 10))

      act(() => {
        result.current.previousPage()
      })

      expect(result.current.currentPage).toBe(4)
    })

    it("should not go below page 1", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.previousPage()
      })

      expect(result.current.currentPage).toBe(1) // Should remain at first page
    })

    it("should decrement multiple times correctly", () => {
      const { result } = renderHook(() => usePDFNavigation(5, 10))

      act(() => {
        result.current.previousPage()
      })
      act(() => {
        result.current.previousPage()
      })
      act(() => {
        result.current.previousPage()
      })

      expect(result.current.currentPage).toBe(2)
    })
  })

  describe("zoom - zoomIn", () => {
    it("should increase zoom level by 25%", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.zoomIn()
      })

      expect(result.current.zoomLevel).toBe(125)
    })

    it("should update zoomMode to percentage when zooming", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      // Initial mode is fitWidth
      expect(result.current.zoomMode).toBe("fitWidth")

      act(() => {
        result.current.zoomIn()
      })

      expect(result.current.zoomMode).toBe("percentage")
    })

    it("should not exceed maximum zoom of 300%", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      // Set to near max
      act(() => {
        result.current.setZoomPercentage(300)
        result.current.zoomIn()
      })

      expect(result.current.zoomLevel).toBe(300) // Should remain at max
    })

    it("should increment multiple times correctly", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.zoomIn()
        result.current.zoomIn()
        result.current.zoomIn()
      })

      expect(result.current.zoomLevel).toBe(175)
    })
  })

  describe("zoom - zoomOut", () => {
    it("should decrease zoom level by 25%", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.zoomOut()
      })

      expect(result.current.zoomLevel).toBe(75)
    })

    it("should update zoomMode to percentage when zooming", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.zoomOut()
      })

      expect(result.current.zoomMode).toBe("percentage")
    })

    it("should not go below minimum zoom of 50%", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      // Zoom out twice (100% -> 75% -> 50%)
      act(() => {
        result.current.zoomOut()
        result.current.zoomOut()
      })

      expect(result.current.zoomLevel).toBe(50)

      // Try to zoom out again
      act(() => {
        result.current.zoomOut()
      })

      expect(result.current.zoomLevel).toBe(50) // Should remain at min
    })

    it("should decrement multiple times correctly", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      // Start at 200%
      act(() => {
        result.current.setZoomPercentage(200)
        result.current.zoomOut()
        result.current.zoomOut()
      })

      expect(result.current.zoomLevel).toBe(150)
    })
  })

  describe("zoom - setZoomMode", () => {
    it("should change zoom mode to fitWidth", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      // Change to different mode first
      act(() => {
        result.current.setZoomMode("fitHeight")
        result.current.setZoomMode("fitWidth")
      })

      expect(result.current.zoomMode).toBe("fitWidth")
    })

    it("should change zoom mode to fitHeight", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.setZoomMode("fitHeight")
      })

      expect(result.current.zoomMode).toBe("fitHeight")
    })

    it("should not change zoom level when changing mode", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      const initialZoomLevel = result.current.zoomLevel

      act(() => {
        result.current.setZoomMode("fitHeight")
      })

      expect(result.current.zoomLevel).toBe(initialZoomLevel)
    })
  })

  describe("zoom - setZoomPercentage", () => {
    it("should set custom zoom percentage", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.setZoomPercentage(150)
      })

      expect(result.current.zoomLevel).toBe(150)
      expect(result.current.zoomMode).toBe("percentage")
    })

    it("should clamp zoom percentage to minimum 50%", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.setZoomPercentage(25)
      })

      expect(result.current.zoomLevel).toBe(50)
    })

    it("should clamp zoom percentage to maximum 300%", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      act(() => {
        result.current.setZoomPercentage(500)
      })

      expect(result.current.zoomLevel).toBe(300)
    })
  })

  describe("callbacks - onPageChange", () => {
    it("should trigger onPageChange callback when page changes", () => {
      const onPageChange = vi.fn()
      const { result } = renderHook(() =>
        usePDFNavigation(1, 10, onPageChange),
      )

      act(() => {
        result.current.goToPage(5)
      })

      expect(onPageChange).toHaveBeenCalledWith(5)
      expect(onPageChange).toHaveBeenCalledTimes(1)
    })

    it("should trigger onPageChange when using nextPage", () => {
      const onPageChange = vi.fn()
      const { result } = renderHook(() =>
        usePDFNavigation(1, 10, onPageChange),
      )

      act(() => {
        result.current.nextPage()
      })

      expect(onPageChange).toHaveBeenCalledWith(2)
    })

    it("should trigger onPageChange when using previousPage", () => {
      const onPageChange = vi.fn()
      const { result } = renderHook(() =>
        usePDFNavigation(5, 10, onPageChange),
      )

      act(() => {
        result.current.previousPage()
      })

      expect(onPageChange).toHaveBeenCalledWith(4)
    })

    it("should not trigger onPageChange for invalid page numbers", () => {
      const onPageChange = vi.fn()
      const { result } = renderHook(() =>
        usePDFNavigation(1, 10, onPageChange),
      )

      act(() => {
        result.current.goToPage(0)
        result.current.goToPage(999)
      })

      expect(onPageChange).not.toHaveBeenCalled()
    })

    it("should not trigger onPageChange when at boundaries", () => {
      const onPageChange = vi.fn()
      const { result } = renderHook(() =>
        usePDFNavigation(1, 10, onPageChange),
      )

      act(() => {
        result.current.previousPage() // Already at page 1
      })

      expect(onPageChange).not.toHaveBeenCalled()
    })
  })

  describe("edge cases - zero total pages", () => {
    it("should handle zero total pages gracefully", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 0))

      // Navigation functions should do nothing
      act(() => {
        result.current.nextPage()
      })
      expect(result.current.currentPage).toBe(1)

      act(() => {
        result.current.previousPage()
      })
      expect(result.current.currentPage).toBe(1)

      act(() => {
        result.current.goToPage(5)
      })
      expect(result.current.currentPage).toBe(1)
    })

    it("should not trigger callback with zero pages", () => {
      const onPageChange = vi.fn()
      const { result } = renderHook(() => usePDFNavigation(1, 0, onPageChange))

      act(() => {
        result.current.nextPage()
      })

      expect(onPageChange).not.toHaveBeenCalled()
    })
  })

  describe("integration - combined navigation and zoom", () => {
    it("should maintain independent state for navigation and zoom", () => {
      const { result } = renderHook(() => usePDFNavigation(1, 10))

      // Navigate to page 5
      act(() => {
        result.current.goToPage(5)
      })

      // Zoom in
      act(() => {
        result.current.zoomIn()
        result.current.zoomIn()
      })

      // Check both states are correct
      expect(result.current.currentPage).toBe(5)
      expect(result.current.zoomLevel).toBe(150)
      expect(result.current.zoomMode).toBe("percentage")
    })

    it("should handle rapid state changes correctly", () => {
      const onPageChange = vi.fn()
      const { result } = renderHook(() =>
        usePDFNavigation(5, 10, onPageChange),
      )

      // Rapid navigation (separate act calls for each state update)
      act(() => {
        result.current.nextPage()
      })
      act(() => {
        result.current.nextPage()
      })
      act(() => {
        result.current.previousPage()
      })

      // Rapid zoom
      act(() => {
        result.current.zoomIn()
        result.current.zoomOut()
        result.current.setZoomMode("fitHeight")
      })

      expect(result.current.currentPage).toBe(6)
      expect(result.current.zoomMode).toBe("fitHeight")
      expect(onPageChange).toHaveBeenCalledTimes(3)
    })
  })

  describe("totalPages updates", () => {
    it("should handle totalPages update during usage", () => {
      const { result, rerender } = renderHook(
        ({ initialPage, totalPages }) => usePDFNavigation(initialPage, totalPages),
        {
          initialProps: { initialPage: 1, totalPages: 5 },
        },
      )

      // Navigate to page 3
      act(() => {
        result.current.goToPage(3)
      })
      expect(result.current.currentPage).toBe(3)

      // Update totalPages to 10
      rerender({ initialPage: 1, totalPages: 10 })

      // Should be able to navigate to page 8 now
      act(() => {
        result.current.goToPage(8)
      })
      expect(result.current.currentPage).toBe(8)
    })

    it("should respect new totalPages boundary", () => {
      const { result, rerender } = renderHook(
        ({ initialPage, totalPages }) => usePDFNavigation(initialPage, totalPages),
        {
          initialProps: { initialPage: 1, totalPages: 10 },
        },
      )

      // Navigate to page 8
      act(() => {
        result.current.goToPage(8)
      })

      // Reduce totalPages to 5
      rerender({ initialPage: 1, totalPages: 5 })

      // Current page should automatically adjust to 5 (via useEffect)
      // Wait for effect to run
      expect(result.current.currentPage).toBe(5) // Auto-adjusted to totalPages
    })
  })
})
