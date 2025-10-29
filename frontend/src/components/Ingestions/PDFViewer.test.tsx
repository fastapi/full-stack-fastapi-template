import { screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"
import { renderWithChakra as render } from "@/test/utils"
import { PDFViewer } from "./PDFViewer"

// Mock react-pdf components
vi.mock("react-pdf", () => {
  const React = require("react")

  return {
    Document: ({ children, onLoadSuccess, onLoadError, loading, error }: any) => {
      // Simulate successful load on mount
      React.useEffect(() => {
        if (onLoadSuccess) {
          onLoadSuccess({ numPages: 10 })
        }
      }, [onLoadSuccess])

      if (loading) {
        return <div>{loading}</div>
      }
      if (error) {
        return <div>{error}</div>
      }
      return <div data-testid="pdf-document">{children}</div>
    },
    Page: ({ pageNumber, loading }: any) => {
      if (loading) {
        return <div>Page loading...</div>
      }
      return (
        <div data-testid="pdf-page">
          <canvas data-testid="pdf-canvas">Page {pageNumber}</canvas>
        </div>
      )
    },
    pdfjs: {
      version: "4.10.38",
      GlobalWorkerOptions: {
        workerSrc: "",
      },
    },
  }
})

describe("PDFViewer", () => {
  const mockPresignedUrl = "https://example.com/sample.pdf"

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  describe("Rendering and Loading", () => {
    it("should render loading state initially", () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)
      expect(screen.getByText(/loading pdf/i)).toBeInTheDocument()
    })

    it("should render PDF after successful load", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByTestId("pdf-document")).toBeInTheDocument()
      })

      await waitFor(() => {
        expect(screen.getByTestId("pdf-canvas")).toBeInTheDocument()
      })
    })

    it("should display page indicator after load", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        // Page indicator is split across elements: "Page", input with value "1", "of 10"
        expect(screen.getByText(/^page$/i)).toBeInTheDocument()
        expect(screen.getByText(/^of 10$/i)).toBeInTheDocument()
      })
    })

    it("should render controls after PDF loads", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByLabelText(/previous page/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/next page/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/zoom in/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/zoom out/i)).toBeInTheDocument()
      })
    })
  })

  describe("Pagination Controls", () => {
    it("should disable Previous button on first page", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        const prevButton = screen.getByLabelText(/previous page/i)
        expect(prevButton).toBeDisabled()
      })
    })

    it("should enable Next button when not on last page", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        const nextButton = screen.getByLabelText(/next page/i)
        expect(nextButton).not.toBeDisabled()
      })
    })

    it("should navigate to next page on Next button click", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/^of 10$/i)).toBeInTheDocument()
      })

      const nextButton = screen.getByLabelText(/next page/i)
      fireEvent.click(nextButton)

      await waitFor(() => {
        // Check input value changed to "2"
        const pageInput = screen.getByLabelText(/go to page/i) as HTMLInputElement
        expect(pageInput.value).toBe("2")
      })
    })

    it("should navigate to previous page on Previous button click", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      // Wait for load and navigate to page 2
      await waitFor(() => {
        expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument()
      })

      const nextButton = screen.getByLabelText(/next page/i)
      fireEvent.click(nextButton)

      await waitFor(() => {
        expect(screen.getByText(/page 2 of 10/i)).toBeInTheDocument()
      })

      // Navigate back to page 1
      const prevButton = screen.getByLabelText(/previous page/i)
      fireEvent.click(prevButton)

      await waitFor(() => {
        expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument()
      })
    })

    it("should enable both buttons when on middle page", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument()
      })

      // Navigate to page 2 (middle page)
      const nextButton = screen.getByLabelText(/next page/i)
      fireEvent.click(nextButton)

      await waitFor(() => {
        const prevButton = screen.getByLabelText(/previous page/i)
        expect(prevButton).not.toBeDisabled()
        expect(nextButton).not.toBeDisabled()
      })
    })

    it("should allow jumping to specific page via input", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument()
      })

      const pageInput = screen.getByLabelText(/go to page/i)
      fireEvent.change(pageInput, { target: { value: "5" } })
      fireEvent.blur(pageInput)

      await waitFor(() => {
        expect(screen.getByText(/page 5 of 10/i)).toBeInTheDocument()
      })
    })

    it("should ignore invalid page numbers", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument()
      })

      const pageInput = screen.getByLabelText(/go to page/i)

      // Try invalid page number (999)
      fireEvent.change(pageInput, { target: { value: "999" } })
      fireEvent.blur(pageInput)

      // Should stay on page 1
      await waitFor(() => {
        expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument()
      })
    })
  })

  describe("Zoom Controls", () => {
    it("should display default zoom level (100%)", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/100%/i)).toBeInTheDocument()
      })
    })

    it("should zoom in by 25% on Zoom In button click", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/100%/i)).toBeInTheDocument()
      })

      const zoomInButton = screen.getByLabelText(/zoom in/i)
      fireEvent.click(zoomInButton)

      await waitFor(() => {
        expect(screen.getByText(/125%/i)).toBeInTheDocument()
      })
    })

    it("should zoom out by 25% on Zoom Out button click", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/100%/i)).toBeInTheDocument()
      })

      const zoomOutButton = screen.getByLabelText(/zoom out/i)
      fireEvent.click(zoomOutButton)

      await waitFor(() => {
        expect(screen.getByText(/75%/i)).toBeInTheDocument()
      })
    })

    it("should not zoom in beyond 300%", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/100%/i)).toBeInTheDocument()
      })

      const zoomInButton = screen.getByLabelText(/zoom in/i)

      // Click 8 times to exceed 300% (100 + 8*25 = 300)
      for (let i = 0; i < 10; i++) {
        fireEvent.click(zoomInButton)
      }

      await waitFor(() => {
        // Should cap at 300%
        expect(screen.getByText(/300%/i)).toBeInTheDocument()
      })
    })

    it("should not zoom out below 50%", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/100%/i)).toBeInTheDocument()
      })

      const zoomOutButton = screen.getByLabelText(/zoom out/i)

      // Click 5 times to go below 50% (100 - 5*25 = -25)
      for (let i = 0; i < 5; i++) {
        fireEvent.click(zoomOutButton)
      }

      await waitFor(() => {
        // Should cap at 50%
        expect(screen.getByText(/50%/i)).toBeInTheDocument()
      })
    })

    it("should switch to Fit Width mode", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/100%/i)).toBeInTheDocument()
      })

      const fitWidthButton = screen.getByRole("button", { name: /fit width/i })
      fireEvent.click(fitWidthButton)

      await waitFor(() => {
        expect(screen.getByText(/fit width/i)).toBeInTheDocument()
      })
    })

    it("should switch to Fit Height mode", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/100%/i)).toBeInTheDocument()
      })

      const fitHeightButton = screen.getByRole("button", { name: /fit height/i })
      fireEvent.click(fitHeightButton)

      await waitFor(() => {
        expect(screen.getByText(/fit height/i)).toBeInTheDocument()
      })
    })
  })

  describe("Error Handling", () => {
    it("should display error message for corrupted PDF", async () => {
      // Mock Document to trigger error
      vi.doMock("react-pdf", () => ({
        Document: ({ onLoadError, error }: any) => {
          if (onLoadError) {
            setTimeout(() => {
              onLoadError(new Error("Failed to load PDF"))
            }, 0)
          }
          return error ? <div>{error}</div> : null
        },
        Page: () => null,
      }))

      render(<PDFViewer presignedUrl="https://example.com/corrupted.pdf" />)

      await waitFor(() => {
        expect(
          screen.getByText(/failed to load pdf.*corrupted/i),
        ).toBeInTheDocument()
      })
    })

    it("should show Try Again button on error", async () => {
      vi.doMock("react-pdf", () => ({
        Document: ({ onLoadError, error }: any) => {
          if (onLoadError) {
            setTimeout(() => {
              onLoadError(new Error("Network error"))
            }, 0)
          }
          return error ? <div>{error}</div> : null
        },
        Page: () => null,
      }))

      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument()
      })
    })
  })

  describe("Edge Cases", () => {
    it("should disable both navigation buttons for single-page PDF", async () => {
      // Mock Document with single page
      vi.doMock("react-pdf", () => ({
        Document: ({ onLoadSuccess }: any) => {
          if (onLoadSuccess) {
            setTimeout(() => {
              onLoadSuccess({ numPages: 1 })
            }, 0)
          }
          return <div data-testid="pdf-document" />
        },
        Page: () => <div data-testid="pdf-page" />,
      }))

      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByText(/page 1 of 1/i)).toBeInTheDocument()
      })

      const prevButton = screen.getByLabelText(/previous page/i)
      const nextButton = screen.getByLabelText(/next page/i)

      expect(prevButton).toBeDisabled()
      expect(nextButton).toBeDisabled()
    })

    it("should render only current page for large PDFs", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} />)

      await waitFor(() => {
        expect(screen.getByTestId("pdf-canvas")).toBeInTheDocument()
      })

      // Should only render one Page component (lazy loading)
      const pages = screen.queryAllByTestId("pdf-page")
      expect(pages).toHaveLength(1)
    })

    it("should validate presignedUrl is HTTPS", () => {
      const consoleWarnSpy = vi.spyOn(console, "warn").mockImplementation(() => {})

      render(<PDFViewer presignedUrl="http://example.com/insecure.pdf" />)

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining("HTTPS"),
      )

      consoleWarnSpy.mockRestore()
    })
  })

  describe("Props", () => {
    it("should start at defaultPage if provided", async () => {
      render(<PDFViewer presignedUrl={mockPresignedUrl} defaultPage={3} />)

      await waitFor(() => {
        expect(screen.getByText(/page 3 of 10/i)).toBeInTheDocument()
      })
    })

    it("should call onPageChange callback when page changes", async () => {
      const onPageChange = vi.fn()
      render(
        <PDFViewer presignedUrl={mockPresignedUrl} onPageChange={onPageChange} />,
      )

      await waitFor(() => {
        expect(screen.getByText(/page 1 of 10/i)).toBeInTheDocument()
      })

      const nextButton = screen.getByLabelText(/next page/i)
      fireEvent.click(nextButton)

      await waitFor(() => {
        expect(onPageChange).toHaveBeenCalledWith(2)
      })
    })

    it("should call onError callback on load failure", async () => {
      const onError = vi.fn()

      vi.doMock("react-pdf", () => ({
        Document: ({ onLoadError }: any) => {
          if (onLoadError) {
            setTimeout(() => {
              onLoadError(new Error("Load failed"))
            }, 0)
          }
          return null
        },
        Page: () => null,
      }))

      render(<PDFViewer presignedUrl={mockPresignedUrl} onError={onError} />)

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(expect.any(Error))
      })
    })
  })
})
