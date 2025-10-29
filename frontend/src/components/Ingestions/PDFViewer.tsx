import {
  Box,
  Button,
  Flex,
  HStack,
  Icon,
  IconButton,
  Input,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useEffect, useState } from "react"
import { Document, Page, pdfjs } from "react-pdf"
import {
  FiChevronLeft,
  FiChevronRight,
  FiZoomIn,
  FiZoomOut,
} from "react-icons/fi"
import { usePDFNavigation } from "@/hooks/usePDFNavigation"

// Import required CSS for react-pdf
import "react-pdf/dist/Page/AnnotationLayer.css"
import "react-pdf/dist/Page/TextLayer.css"

/**
 * PDFViewer component props
 */
export interface PDFViewerProps {
  /** Presigned URL to the PDF file (must be HTTPS) */
  presignedUrl: string
  /** Starting page number (default: 1) */
  defaultPage?: number
  /** Callback when page changes */
  onPageChange?: (page: number) => void
  /** Callback when error occurs */
  onError?: (error: Error) => void
}

/**
 * PDF Viewer Component with Pagination and Zoom Controls
 *
 * Displays a PDF document with navigation controls, zoom functionality,
 * and lazy loading for performance. Only renders the current page.
 *
 * @example
 * <PDFViewer
 *   presignedUrl="https://example.com/document.pdf"
 *   defaultPage={1}
 *   onPageChange={(page) => console.log('Page:', page)}
 * />
 */
export function PDFViewer({
  presignedUrl,
  defaultPage = 1,
  onPageChange,
  onError,
}: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<Error | null>(null)
  const [pageInputValue, setPageInputValue] = useState<string>("")

  // PDF navigation and zoom state
  const {
    currentPage,
    totalPages,
    zoomLevel,
    zoomMode,
    goToPage,
    nextPage,
    previousPage,
    zoomIn,
    zoomOut,
    setZoomMode,
  } = usePDFNavigation(defaultPage, numPages, onPageChange)

  // Validate presigned URL is HTTPS
  useEffect(() => {
    if (presignedUrl && !presignedUrl.startsWith("https://")) {
      console.warn(
        "PDFViewer: presignedUrl should use HTTPS for security. Received:",
        presignedUrl,
      )
    }
  }, [presignedUrl])

  // Update page input value when current page changes
  useEffect(() => {
    setPageInputValue(String(currentPage))
  }, [currentPage])

  /**
   * Handle successful PDF document load
   */
  function onDocumentLoadSuccess({ numPages }: { numPages: number }): void {
    setNumPages(numPages)
    setIsLoading(false)
    setError(null)
  }

  /**
   * Handle PDF document load error
   */
  function onDocumentLoadError(loadError: Error): void {
    setError(loadError)
    setIsLoading(false)
    if (onError) {
      onError(loadError)
    }
  }

  /**
   * Handle page input change
   */
  function handlePageInputChange(e: React.ChangeEvent<HTMLInputElement>): void {
    setPageInputValue(e.target.value)
  }

  /**
   * Handle page input blur (jump to page)
   */
  function handlePageInputBlur(): void {
    const pageNum = Number.parseInt(pageInputValue, 10)
    if (!Number.isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages) {
      goToPage(pageNum)
    } else {
      // Reset to current page if invalid
      setPageInputValue(String(currentPage))
    }
  }

  /**
   * Handle page input Enter key
   */
  function handlePageInputKeyDown(e: React.KeyboardEvent<HTMLInputElement>): void {
    if (e.key === "Enter") {
      handlePageInputBlur()
    }
  }

  /**
   * Retry loading PDF after error
   */
  function handleRetry(): void {
    setError(null)
    setIsLoading(true)
  }

  // Render error state (separate from loading/loaded)
  if (error) {
    return (
      <Box
        p={6}
        borderRadius="md"
        bg="red.50"
        borderWidth="1px"
        borderColor="red.200"
      >
        <VStack gap={3} align="start">
          <Text fontWeight="semibold" color="red.700" fontSize="lg">
            Failed to load PDF
          </Text>
          <Text color="red.600">
            The file may be corrupted or the URL may have expired.
          </Text>
          <Text fontSize="sm" color="red.500">
            Error: {error.message}
          </Text>
          <HStack gap={3}>
            <Button colorPalette="red" onClick={handleRetry}>
              Try Again
            </Button>
            <Text fontSize="sm" color="red.500">
              If issue persists, contact support
            </Text>
          </HStack>
        </VStack>
      </Box>
    )
  }

  // Calculate zoom scale based on mode
  const scale = zoomMode === "percentage" ? zoomLevel / 100 : undefined
  const width = zoomMode === "fitWidth" ? 800 : undefined // Adjust based on container
  const height = zoomMode === "fitHeight" ? 600 : undefined

  return (
    <VStack gap={4} align="stretch">
      {/* Controls Section - Hide until PDF loads */}
      {!isLoading && numPages > 0 && (
        <Flex
          gap={4}
          align="center"
          justify="space-between"
          p={3}
          bg="gray.50"
          borderRadius="md"
          borderWidth="1px"
          borderColor="gray.200"
        >
          {/* Pagination Controls */}
          <HStack gap={2}>
            <IconButton
              aria-label="Previous page"
              onClick={previousPage}
              disabled={currentPage <= 1}
              size="sm"
              variant="outline"
            >
              <Icon fontSize="lg">
                <FiChevronLeft />
              </Icon>
            </IconButton>

            <HStack gap={1} align="center">
              <Text fontSize="sm" color="gray.600">
                Page
              </Text>
              <Input
                aria-label="Go to page"
                value={pageInputValue}
                onChange={handlePageInputChange}
                onBlur={handlePageInputBlur}
                onKeyDown={handlePageInputKeyDown}
                size="sm"
                width="50px"
                textAlign="center"
              />
              <Text fontSize="sm" color="gray.600">
                of {totalPages}
              </Text>
            </HStack>

            <IconButton
              aria-label="Next page"
              onClick={nextPage}
              disabled={currentPage >= totalPages}
              size="sm"
              variant="outline"
            >
              <Icon fontSize="lg">
                <FiChevronRight />
              </Icon>
            </IconButton>
          </HStack>

          {/* Zoom Controls */}
          <HStack gap={2}>
            <IconButton
              aria-label="Zoom out"
              onClick={zoomOut}
              disabled={zoomLevel <= 50}
              size="sm"
              variant="outline"
            >
              <Icon fontSize="lg">
                <FiZoomOut />
              </Icon>
            </IconButton>

            <Text fontSize="sm" fontWeight="medium" minW="60px" textAlign="center">
              {zoomMode === "fitWidth"
                ? "Fit Width"
                : zoomMode === "fitHeight"
                  ? "Fit Height"
                  : `${zoomLevel}%`}
            </Text>

            <IconButton
              aria-label="Zoom in"
              onClick={zoomIn}
              disabled={zoomLevel >= 300}
              size="sm"
              variant="outline"
            >
              <Icon fontSize="lg">
                <FiZoomIn />
              </Icon>
            </IconButton>

            <Button
              size="sm"
              variant="outline"
              onClick={() => setZoomMode("fitWidth")}
            >
              Fit Width
            </Button>

            <Button
              size="sm"
              variant="outline"
              onClick={() => setZoomMode("fitHeight")}
            >
              Fit Height
            </Button>
          </HStack>
        </Flex>
      )}

      {/* PDF Document Container - Always render to trigger loading */}
      <Box
        borderRadius="md"
        borderWidth="1px"
        borderColor="gray.200"
        bg="gray.100"
        p={4}
        overflow="auto"
        maxH="80vh"
      >
        <Document
          file={presignedUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={onDocumentLoadError}
          loading={
            <VStack gap={2} py={8}>
              <Spinner size="lg" color="blue.500" />
              <Text color="gray.600">Loading PDF...</Text>
            </VStack>
          }
          error={
            <Box p={4} bg="red.50" borderRadius="md">
              <Text color="red.700">Failed to load PDF. Please try again.</Text>
            </Box>
          }
        >
          {/* Only render current page (lazy loading) */}
          {!isLoading && (
            <Page
              pageNumber={currentPage}
              scale={scale}
              width={width}
              height={height}
              loading={
                <VStack gap={2} py={8}>
                  <Spinner size="md" color="blue.500" />
                  <Text fontSize="sm" color="gray.600">
                    Loading page...
                  </Text>
                </VStack>
              }
              renderTextLayer={true}
              renderAnnotationLayer={true}
            />
          )}
        </Document>
      </Box>
    </VStack>
  )
}
