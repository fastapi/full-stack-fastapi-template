# PRD: PDF Viewer Integration

**Version**: 1.0
**Component**: Frontend
**Status**: Draft
**Last Updated**: 2025-10-22
**Related**: [Product Overview](../overview.md), [Implementation Plan - Math](../implementation-plan-math.md), [Document Upload & Storage](./document-upload-storage.md), [Infrastructure Setup](./infrastructure-setup.md)

---

## 1. Overview

### What & Why

Enable Content Reviewers to view uploaded Math PDF worksheets directly in the browser with interactive controls for navigation, zoom, and responsive viewing. This **Epic 3** feature provides the visual inspection interface needed before reviewers proceed with question extraction and correction workflows.

**Value**: Reviewers can visually verify worksheet content without downloading files or switching applications. This streamlines the review workflow and provides context for extraction accuracy assessment in later epics (Epic 9: PDF Annotations).

### Scope

**In scope**:
- react-pdf library integration with PDF.js worker configuration
- PDF rendering component (`PDFViewer`) with Document/Page components
- Pagination controls (page X of Y, previous/next buttons, jump to page)
- Zoom controls (fit width, fit height, zoom in/out, percentage selector)
- Lazy page loading (render only visible pages, not entire document)
- Loading states and error handling (corrupted PDFs, network errors)
- Route: `/ingestions/:id/review` displays PDF from presigned URL
- Mobile-responsive layout (desktop, tablet, mobile breakpoints)
- Keyboard shortcuts (arrow keys for navigation, +/- for zoom)

**Out of scope (v1)**:
- PDF annotations/highlights (deferred to Epic 9: PDF Viewer with Annotations)
- Text selection and copying (disabled in v1)
- PDF search functionality (deferred to Phase 2)
- PDF download button (presigned URL already provides access)
- Multi-page thumbnail sidebar (deferred to Phase 2)
- Fullscreen mode (deferred to Phase 2)
- PDF rotation controls (deferred to Phase 2)
- Print functionality (browser native print disabled for now)
- PDF editing or markup tools
- Text layer rendering (deferred to Epic 9 for text selection with annotations)

### Living Document

This PRD evolves during implementation:
- Adjustments based on react-pdf performance with large PDFs (>20 pages)
- Zoom level refinements based on typical worksheet layouts
- Lazy loading strategy optimization if memory usage is high
- Mobile UX improvements based on testing on actual devices

### Non-Functional Requirements

- **Performance**:
  - First page render: <1s for 10-page PDF (p95)
  - Subsequent page render: <500ms when navigating (p95)
  - Zoom operation: <200ms to re-render at new scale
  - Page navigation: <300ms between page transitions
  - Memory usage: <150MB for 20-page PDF (avoid memory leaks)
  - Initial bundle size increase: <500KB gzipped (react-pdf + PDF.js worker)
- **Accessibility**:
  - WCAG 2.1 AA compliance
  - Keyboard navigation: Arrow keys, Page Up/Down, Home/End
  - Screen reader announcements for page changes ("Page 3 of 10 loaded")
  - Focus management: Visible focus indicators on controls
  - Alt text for control buttons
- **Responsiveness**:
  - Desktop (≥1024px): Full controls, side-by-side layout ready for Epic 9
  - Tablet (768px-1023px): Simplified controls, full-width PDF
  - Mobile (<768px): Touch-friendly controls, pinch-to-zoom support
- **Browser Compatibility**:
  - Chrome/Edge 120+ (primary)
  - Firefox 120+
  - Safari 17+ (iOS and macOS)
  - No IE11 support

---

## 2. User Stories

### Primary Story
**As a** Content Reviewer
**I want** to view uploaded Math PDF worksheets in the browser with zoom and pagination
**So that** I can visually inspect the document before and during the extraction review process

### Supporting Stories

**As a** Content Reviewer
**I want** to navigate between pages using next/previous buttons or jump to a specific page
**So that** I can quickly move to sections of interest in multi-page worksheets

**As a** Content Reviewer
**I want** to zoom in/out on the PDF to read small text or see the full page layout
**So that** I can examine question details and verify extraction boundaries

**As a** Content Reviewer on Mobile
**I want** the PDF viewer to work responsively on my tablet
**So that** I can review worksheets on-the-go without needing a desktop computer

**As a** Frontend Developer
**I want** a reusable PDF viewer component with clean props interface
**So that** I can integrate it with annotations in Epic 9 without major refactoring

**As a** User with Slow Internet
**I want** to see the first page quickly even if the full PDF hasn't loaded
**So that** I can start reviewing without waiting for the entire document

---

## 3. Acceptance Criteria (Gherkin)

### Scenario: Successful PDF Rendering
```gherkin
Given I have an extraction with ID "abc-123" and a valid presigned PDF URL
When I navigate to "/ingestions/abc-123/review"
Then the PDF renders in the browser within 1 second (first page)
And I see page 1 of N displayed
And I see pagination controls (Previous, Next, "Page 1 of N")
And I see zoom controls (Zoom In, Zoom Out, Fit Width, Fit Height)
And the PDF is rendered at "Fit Width" by default
```

### Scenario: Page Navigation - Next/Previous Buttons
```gherkin
Given I am viewing a 10-page PDF on page 1
When I click the "Next" button
Then page 2 loads within 500ms
And the page indicator updates to "Page 2 of 10"
And the "Previous" button is now enabled
When I click "Previous"
Then page 1 is displayed again
And the "Previous" button is disabled (first page)
```

### Scenario: Page Navigation - Jump to Page
```gherkin
Given I am viewing a 10-page PDF on page 1
When I click on the page number input field
And I type "7" and press Enter
Then page 7 loads within 500ms
And the page indicator shows "Page 7 of 10"
```

### Scenario: Zoom Controls - Zoom In/Out
```gherkin
Given I am viewing a PDF at 100% zoom
When I click the "Zoom In" button
Then the PDF zooms to 125%
And the zoom percentage indicator shows "125%"
When I click "Zoom In" again
Then the PDF zooms to 150%
When I click "Zoom Out"
Then the PDF zooms back to 125%
```

### Scenario: Zoom Controls - Fit Width
```gherkin
Given I am viewing a PDF at 150% zoom
When I click the "Fit Width" button
Then the PDF scales to fit the container width
And the zoom percentage updates to the calculated percentage (e.g., "110%")
And the entire page width is visible without horizontal scrolling
```

### Scenario: Lazy Loading - Large PDFs
```gherkin
Given I upload a 25-page PDF
When the PDF viewer loads
Then only page 1 is rendered initially
And subsequent pages are not loaded into the DOM
When I navigate to page 15
Then page 15 is rendered
And previously viewed pages remain in memory (e.g., pages 1-14)
```

### Scenario: Loading State
```gherkin
Given I navigate to a PDF review page
When the PDF is loading
Then I see a loading spinner with text "Loading PDF..."
And I see a progress indicator if available (e.g., "Loaded 25%")
And the page controls are disabled
When the PDF finishes loading
Then the loading state is replaced with the rendered PDF
And the controls are enabled
```

### Scenario: Error Handling - Corrupted PDF
```gherkin
Given I have an extraction with a corrupted PDF file
When I navigate to the review page
Then I see an error message: "Failed to load PDF. The file may be corrupted."
And I see a "Try Again" button
And I see a "Contact Support" link
When I click "Try Again"
Then the PDF viewer attempts to reload the PDF
```

### Scenario: Error Handling - Network Error
```gherkin
Given I navigate to a PDF review page
And the presigned URL has expired or is unreachable
When the PDF fails to load due to network error
Then I see an error message: "Failed to load PDF. Please check your connection and try again."
And I see a "Retry" button
```

### Scenario: Responsive - Mobile View
```gherkin
Given I am viewing the PDF viewer on a mobile device (<768px width)
When the page loads
Then the PDF fills the screen width
And the controls are touch-friendly (larger tap targets ≥44px)
And I can pinch-to-zoom on the PDF
And pagination controls are stacked vertically for space efficiency
```

### Scenario: Keyboard Navigation
```gherkin
Given I am viewing a PDF with keyboard focus
When I press the Right Arrow key
Then the viewer navigates to the next page
When I press the Left Arrow key
Then the viewer navigates to the previous page
When I press "+" or "="
Then the PDF zooms in
When I press "-"
Then the PDF zooms out
```

---

## 4. Functional Requirements

### Core Behavior

**PDF Rendering Workflow**:
1. Component receives `extractionId` from route parameter (`:id`)
2. Fetch extraction record from API: `GET /api/v1/ingestions/:id`
3. Extract `presigned_url` and `page_count` from response
4. Load PDF via react-pdf `<Document file={presigned_url}>` component
5. Render single `<Page>` component for current page (lazy loading)
6. On page navigation, update `pageNumber` prop to render different page
7. On zoom change, update `scale` or `width` prop to re-render at new size

**Zoom Modes**:
- **Fit Width**: Scale PDF to container width (default)
- **Fit Height**: Scale PDF to container height
- **Percentage**: Fixed zoom levels: 50%, 75%, 100%, 125%, 150%, 200%, 300%
- **Zoom In**: Increment by 25% (e.g., 100% → 125%)
- **Zoom Out**: Decrement by 25% (e.g., 125% → 100%)
- **Min/Max**: Min 50%, Max 300%

**Lazy Loading Strategy**:
- Render only the current page in the DOM
- Use react-pdf's built-in lazy loading (no external virtualization library in v1)
- Keep rendered pages in memory for faster back navigation (browser caching)
- If memory issues arise (>150MB for 20 pages), implement page unmounting strategy

**Keyboard Shortcuts**:
| Key | Action |
|-----|--------|
| Right Arrow, Page Down | Next page |
| Left Arrow, Page Up | Previous page |
| Home | First page |
| End | Last page |
| `+`, `=` | Zoom in |
| `-` | Zoom out |
| `0` | Reset to 100% zoom |

### States & Transitions

| State | Description | Transitions To |
|-------|-------------|----------------|
| **INITIAL** | Component mounted, no PDF loaded | LOADING |
| **LOADING** | Fetching extraction record or loading PDF | LOADED, ERROR |
| **LOADED** | PDF successfully rendered | NAVIGATING, ZOOMING, ERROR |
| **NAVIGATING** | User changing pages | LOADED |
| **ZOOMING** | User adjusting zoom level | LOADED |
| **ERROR** | PDF failed to load (corrupted, network, expired URL) | LOADING (retry) |

### Business Rules

1. **Default Zoom**: Always open PDF at "Fit Width" to maximize readability
2. **Page Persistence**: Remember current page when user navigates away and returns (use URL query param: `?page=3`)
3. **Zoom Persistence**: Remember zoom level per session (sessionStorage, not persisted across sessions)
4. **Pagination Bounds**: Disable "Previous" on page 1, disable "Next" on last page
5. **Zoom Bounds**: Min 50%, Max 300% (prevent unusable zoom levels)
6. **Presigned URL Expiry**: If presigned URL expires (7 days for drafts), show error with option to regenerate URL via API (not in v1, manual refresh required)
7. **Mobile Touch**: Support pinch-to-zoom on mobile (native browser behavior with react-pdf)
8. **Loading Priority**: Load first page immediately, defer subsequent pages until navigated

### Permissions

- **Access**: Same as extraction record - only owner can view PDF
- **Authentication**: JWT token required (same as `/ingestions/:id` API endpoint)
- **Authorization**: Backend validates extraction ownership in `GET /api/v1/ingestions/:id`

---

## 5. Technical Specification

### Architecture Pattern

**Component-Based with Custom Hook** (matches existing frontend patterns):
- **Route** (`frontend/src/routes/_layout/ingestions/$id.review.tsx`): TanStack Router file-based route
- **Container Component** (`PDFReviewPage`): Fetches extraction data, handles loading/error states
- **Presentation Component** (`PDFViewer`): Renders PDF with controls (reusable, no API dependencies)
- **Custom Hook** (`usePDFNavigation`): Encapsulates pagination and zoom state management

**Rationale**: This pattern matches `items.tsx` and `AddItem.tsx`. Separating PDF rendering logic into a custom hook enables reuse in Epic 9 when annotations are added.

### API Endpoints

No new backend endpoints needed. Use existing:

#### `GET /api/v1/ingestions/:id`
**Purpose**: Fetch extraction record with presigned URL and metadata

**Response** (200 OK):
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "filename": "P4_Decimals_Worksheet.pdf",
  "file_size": 5242880,
  "page_count": 10,
  "mime_type": "application/pdf",
  "status": "UPLOADED",
  "presigned_url": "https://[project].supabase.co/storage/v1/object/sign/worksheets/...",
  "uploaded_at": "2025-10-22T14:30:00Z",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Errors**:
- `401 Unauthorized`: User not logged in
- `403 Forbidden`: User does not own this extraction
- `404 Not Found`: Extraction ID does not exist

---

### Data Models

**TypeScript Interfaces** (frontend):

```typescript
// Hook state management
interface PDFNavigationState {
  currentPage: number;
  totalPages: number;
  zoomLevel: number;
  zoomMode: 'fitWidth' | 'fitHeight' | 'percentage';
}

interface PDFNavigationActions {
  goToPage: (page: number) => void;
  nextPage: () => void;
  previousPage: () => void;
  zoomIn: () => void;
  zoomOut: () => void;
  setZoomMode: (mode: 'fitWidth' | 'fitHeight') => void;
  setZoomPercentage: (percentage: number) => void;
}

// Component props
interface PDFViewerProps {
  presignedUrl: string;
  defaultPage?: number;
  onPageChange?: (page: number) => void;
  onError?: (error: Error) => void;
}

interface PDFControlsProps {
  currentPage: number;
  totalPages: number;
  zoomLevel: number;
  zoomMode: string;
  onPageChange: (page: number) => void;
  onNextPage: () => void;
  onPreviousPage: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomModeChange: (mode: string) => void;
}
```

---

## 6. Integration Points

### Dependencies

**Frontend Packages** (add to `package.json`):
```json
{
  "dependencies": {
    "react-pdf": "^9.1.1",
    "pdfjs-dist": "^4.8.69"
  }
}
```

**Note**: `pdfjs-dist` is a peer dependency of `react-pdf` and must be installed separately.

**Internal Dependencies**:
- Existing `IngestionsService.getIngestion(id)` from auto-generated API client
- Existing authentication context (JWT token)
- Existing `useCustomToast` hook for error notifications
- Existing Chakra UI components (Button, Input, Box, Flex, Icon, Text, Spinner)

**External Services**:
- Supabase Storage (presigned URLs for PDF files)
- PDF.js worker (loaded from CDN or local bundle)

### PDF.js Worker Configuration

react-pdf requires PDF.js worker to be configured. Two options:

**Option 1: CDN (Recommended for v1)**:
```typescript
// frontend/src/main.tsx or PDFViewer.tsx
import { pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;
```

**Option 2: Local Bundle (Better for production)**:
```typescript
import { pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();
```

**Rationale**: Option 1 (CDN) is simpler for v1 and reduces bundle size. Option 2 eliminates external dependency but increases bundle size by ~500KB. Choose Option 1 for v1, migrate to Option 2 if CDN reliability is a concern.

### Events

| Event | Trigger | Data | Purpose |
|-------|---------|------|---------|
| `onDocumentLoadSuccess` | PDF loads successfully | `{ numPages }` | Update totalPages state |
| `onDocumentLoadError` | PDF fails to load | `error: Error` | Show error message |
| `onPageLoadSuccess` | Page renders successfully | `page: PDFPageProxy` | Log page load (optional) |
| `onPageLoadError` | Page fails to render | `error: Error` | Show page-specific error |
| `onPageChange` (custom) | User navigates to new page | `pageNumber: number` | Update URL query param |

---

## 7. UX Specifications

### Key UI States

1. **Initial Loading**:
   - Full-screen spinner with text: "Loading PDF..."
   - Progress bar if `onLoadProgress` is available: "Loading... 45%"
   - Controls disabled (grayed out)

2. **Loaded - First Page**:
   - PDF rendered at Fit Width
   - Pagination: "Page 1 of 10"
   - Previous button disabled
   - Next button enabled
   - Zoom controls enabled

3. **Page Navigation**:
   - Inline spinner on page change: Small spinner overlaid on PDF during render
   - Page indicator updates immediately: "Page 3 of 10"
   - New page renders within 500ms

4. **Zoom Change**:
   - Immediate zoom percentage update: "125%"
   - PDF re-renders at new scale within 200ms
   - Smooth transition (no flicker)

5. **Error - Corrupted PDF**:
   - Red error box with icon
   - Message: "Failed to load PDF. The file may be corrupted."
   - "Try Again" button (reloads PDF)
   - "Contact Support" link (mailto or support page)

6. **Error - Network/Expired URL**:
   - Yellow warning box
   - Message: "Failed to load PDF. The presigned URL may have expired."
   - "Retry" button (refetches extraction record to get new URL - future feature)
   - Fallback: "Please contact support if the issue persists."

### Component Structure

**Route**: `frontend/src/routes/_layout/ingestions/$id.review.tsx`
```tsx
import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { IngestionsService } from '@/client'
import { PDFViewer } from '@/components/Ingestions/PDFViewer'
import { Container, Heading, Text, Spinner, Box } from '@chakra-ui/react'

export const Route = createFileRoute('/_layout/ingestions/$id/review')({
  component: PDFReviewPage,
})

function PDFReviewPage() {
  const { id } = Route.useParams()
  const { page = 1 } = Route.useSearch<{ page?: number }>()

  const { data: extraction, isLoading, error } = useQuery({
    queryKey: ['ingestion', id],
    queryFn: () => IngestionsService.getIngestion({ id }),
  })

  if (isLoading) {
    return (
      <Container maxW="full" py={8} textAlign="center">
        <Spinner size="xl" />
        <Text mt={4}>Loading extraction...</Text>
      </Container>
    )
  }

  if (error || !extraction) {
    return (
      <Container maxW="full" py={8}>
        <Box bg="red.50" p={4} borderRadius="md">
          <Text color="red.600">Failed to load extraction. Please try again.</Text>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxW="full" h="100vh" p={0}>
      <Heading size="sm" p={4} borderBottom="1px" borderColor="gray.200">
        {extraction.filename}
      </Heading>
      <PDFViewer
        presignedUrl={extraction.presigned_url}
        defaultPage={page}
        onPageChange={(newPage) => {
          // Update URL query param
          window.history.replaceState(null, '', `?page=${newPage}`)
        }}
      />
    </Container>
  )
}
```

**Component**: `frontend/src/components/Ingestions/PDFViewer.tsx`
```tsx
import { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { Box, Flex, Button, Text, Input, Spinner, IconButton } from '@chakra-ui/react'
import { FiChevronLeft, FiChevronRight, FiZoomIn, FiZoomOut } from 'react-icons/fi'
import { usePDFNavigation } from '@/hooks/usePDFNavigation'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`

interface PDFViewerProps {
  presignedUrl: string
  defaultPage?: number
  onPageChange?: (page: number) => void
  onError?: (error: Error) => void
}

export function PDFViewer({
  presignedUrl,
  defaultPage = 1,
  onPageChange,
  onError,
}: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0)
  const {
    currentPage,
    zoomLevel,
    zoomMode,
    goToPage,
    nextPage,
    previousPage,
    zoomIn,
    zoomOut,
    setZoomMode,
  } = usePDFNavigation(defaultPage, numPages, onPageChange)

  const handleDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
  }

  const handleDocumentLoadError = (error: Error) => {
    console.error('PDF load error:', error)
    onError?.(error)
  }

  return (
    <Flex direction="column" h="full">
      {/* Controls */}
      <Flex
        justify="space-between"
        align="center"
        p={2}
        bg="gray.50"
        borderBottom="1px"
        borderColor="gray.200"
      >
        {/* Pagination */}
        <Flex align="center" gap={2}>
          <IconButton
            aria-label="Previous page"
            icon={<FiChevronLeft />}
            onClick={previousPage}
            isDisabled={currentPage === 1}
            size="sm"
          />
          <Flex align="center" gap={1}>
            <Input
              type="number"
              value={currentPage}
              onChange={(e) => goToPage(Number(e.target.value))}
              min={1}
              max={numPages}
              w="60px"
              size="sm"
              textAlign="center"
            />
            <Text fontSize="sm">of {numPages}</Text>
          </Flex>
          <IconButton
            aria-label="Next page"
            icon={<FiChevronRight />}
            onClick={nextPage}
            isDisabled={currentPage === numPages}
            size="sm"
          />
        </Flex>

        {/* Zoom */}
        <Flex align="center" gap={2}>
          <IconButton
            aria-label="Zoom out"
            icon={<FiZoomOut />}
            onClick={zoomOut}
            isDisabled={zoomLevel <= 50}
            size="sm"
          />
          <Text fontSize="sm" minW="60px" textAlign="center">
            {zoomLevel}%
          </Text>
          <IconButton
            aria-label="Zoom in"
            icon={<FiZoomIn />}
            onClick={zoomIn}
            isDisabled={zoomLevel >= 300}
            size="sm"
          />
          <Button size="sm" onClick={() => setZoomMode('fitWidth')}>
            Fit Width
          </Button>
          <Button size="sm" onClick={() => setZoomMode('fitHeight')}>
            Fit Height
          </Button>
        </Flex>
      </Flex>

      {/* PDF Container */}
      <Box flex={1} overflow="auto" bg="gray.100" p={4}>
        <Document
          file={presignedUrl}
          onLoadSuccess={handleDocumentLoadSuccess}
          onLoadError={handleDocumentLoadError}
          loading={
            <Flex justify="center" align="center" h="full">
              <Spinner size="xl" />
              <Text ml={4}>Loading PDF...</Text>
            </Flex>
          }
          error={
            <Box bg="red.50" p={4} borderRadius="md" maxW="md" mx="auto" mt={8}>
              <Text color="red.600" fontWeight="bold">
                Failed to load PDF
              </Text>
              <Text color="red.600" fontSize="sm" mt={2}>
                The file may be corrupted or the URL has expired.
              </Text>
            </Box>
          }
        >
          <Page
            pageNumber={currentPage}
            scale={zoomMode === 'percentage' ? zoomLevel / 100 : undefined}
            width={zoomMode === 'fitWidth' ? 800 : undefined}
            height={zoomMode === 'fitHeight' ? 1000 : undefined}
            loading={
              <Flex justify="center" align="center" h="600px">
                <Spinner />
              </Flex>
            }
          />
        </Document>
      </Box>
    </Flex>
  )
}
```

**Custom Hook**: `frontend/src/hooks/usePDFNavigation.ts`
```tsx
import { useState, useCallback } from 'react'

export function usePDFNavigation(
  initialPage: number = 1,
  totalPages: number = 0,
  onPageChange?: (page: number) => void
) {
  const [currentPage, setCurrentPage] = useState(initialPage)
  const [zoomLevel, setZoomLevel] = useState(100)
  const [zoomMode, setZoomMode] = useState<'fitWidth' | 'fitHeight' | 'percentage'>('fitWidth')

  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
      onPageChange?.(page)
    }
  }, [totalPages, onPageChange])

  const nextPage = useCallback(() => {
    goToPage(currentPage + 1)
  }, [currentPage, goToPage])

  const previousPage = useCallback(() => {
    goToPage(currentPage - 1)
  }, [currentPage, goToPage])

  const zoomIn = useCallback(() => {
    setZoomLevel((prev) => Math.min(prev + 25, 300))
    setZoomMode('percentage')
  }, [])

  const zoomOut = useCallback(() => {
    setZoomLevel((prev) => Math.max(prev - 25, 50))
    setZoomMode('percentage')
  }, [])

  return {
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
    setZoomPercentage: setZoomLevel,
  }
}
```

### Responsive Behavior

- **Desktop (≥1024px)**:
  - PDF viewer full height (100vh minus header)
  - Controls horizontal layout (pagination left, zoom right)
  - PDF rendered at Fit Width (typically 800px-1000px)
  - Sidebar space reserved for annotations (Epic 9)

- **Tablet (768px-1023px)**:
  - PDF viewer full width
  - Controls horizontal but more compact (smaller buttons)
  - PDF rendered at Fit Width (typically 600px-800px)

- **Mobile (<768px)**:
  - PDF viewer full screen
  - Controls stacked vertically or iconified
  - PDF rendered at Fit Width (screen width minus padding)
  - Larger tap targets (44px minimum)
  - Pinch-to-zoom enabled

---

## 8. Implementation Guidance

### Follow Existing Patterns

**Based on codebase analysis**:

- **File structure**: Place route in `frontend/src/routes/_layout/ingestions/$id.review.tsx` (TanStack Router file-based routing with param)
- **Component structure**: Create `frontend/src/components/Ingestions/PDFViewer.tsx` (matches `Items/AddItem.tsx`)
- **Custom hook**: Create `frontend/src/hooks/usePDFNavigation.ts` (matches `useCustomToast.ts`)
- **API fetching**: Use TanStack Query with `IngestionsService.getIngestion({ id })` (matches `items.tsx` pattern)
- **Error handling**: Use `useCustomToast()` for errors (matches existing pattern)
- **Styling**: Use Chakra UI components only, no custom CSS (matches project convention)

### Recommended Approach

**Implementation Steps**:

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install react-pdf pdfjs-dist
   ```

2. **Configure PDF.js worker** in `frontend/src/main.tsx`:
   ```tsx
   import { pdfjs } from 'react-pdf'
   pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`
   ```

3. **Create custom hook** `usePDFNavigation.ts` with state management for:
   - Current page
   - Zoom level and mode
   - Navigation functions (next, previous, goToPage)
   - Zoom functions (zoomIn, zoomOut, setZoomMode)

4. **Create `PDFViewer` component**:
   - Import `Document`, `Page` from react-pdf
   - Accept `presignedUrl`, `defaultPage` props
   - Use `usePDFNavigation` hook
   - Render controls and PDF
   - Handle loading/error states

5. **Create route** `$id.review.tsx`:
   - Extract `id` from route params
   - Fetch extraction with TanStack Query
   - Render `PDFViewer` with presigned URL
   - Handle URL query param for page persistence

6. **Add keyboard shortcuts** (optional enhancement):
   - Use `useEffect` with `addEventListener('keydown')`
   - Map arrow keys to pagination, +/- to zoom

7. **Test responsive behavior**:
   - Test on mobile (Chrome DevTools device mode)
   - Test on tablet
   - Verify pinch-to-zoom works on touch devices

### Security Considerations

- **Presigned URL**: Already secured by Supabase (7-day expiry, read-only)
- **No XSS risk**: react-pdf renders to Canvas, not DOM (no script injection)
- **CSP**: Ensure Content Security Policy allows PDF.js worker from CDN:
  ```
  script-src 'self' https://unpkg.com
  worker-src blob:
  ```

### Performance Optimization

- **Lazy Loading**: Only render current page (implemented in component)
- **Canvas Rendering**: react-pdf uses Canvas (not DOM), more performant than SVG
- **Worker Thread**: PDF.js runs in Web Worker, doesn't block main thread
- **Caching**: Browser caches presigned URL responses (HTTP cache headers from Supabase)
- **Bundle Size**: Use CDN for PDF.js worker (saves ~500KB in bundle)

**Optimization for Large PDFs** (if needed):
- Limit rendered pages: Unmount pages not in view (implement in Epic 9 if memory issues)
- Reduce resolution: Lower DPI for thumbnails (not needed in v1)
- Compress PDFs: Backend preprocessing (not in scope)

### Observability

- **Logs**:
  - `INFO`: PDF loaded successfully (extraction_id, page_count, load_time)
  - `ERROR`: PDF load failures (extraction_id, error_message)
- **Metrics**:
  - First page load time (p50, p95, p99)
  - Page navigation time (p95)
  - PDF load error rate (%)
- **User Analytics** (optional):
  - Average pages viewed per extraction
  - Most used zoom level
  - Mobile vs desktop usage

---

## 9. Testing Strategy

### Unit Tests

- [ ] **usePDFNavigation hook**:
  - `goToPage(5)` → currentPage = 5
  - `nextPage()` → currentPage increments
  - `previousPage()` → currentPage decrements
  - `nextPage()` on last page → no change
  - `previousPage()` on first page → no change
  - `zoomIn()` → zoomLevel increases by 25%
  - `zoomOut()` → zoomLevel decreases by 25%
  - Zoom min/max bounds (50%, 300%)
- [ ] **PDFViewer component** (React Testing Library):
  - Renders loading state initially
  - Renders PDF after load
  - Pagination buttons enabled/disabled correctly
  - Zoom controls enabled/disabled correctly
  - Error state displayed on load failure

### Integration Tests

- [ ] **PDF rendering** (Playwright with mock PDF):
  - Load review page → PDF renders
  - Navigate to page 2 → new page loads
  - Zoom in → PDF scales up
  - Fit Width → PDF fits container width
- [ ] **API integration**:
  - Fetch extraction record → presigned URL extracted
  - Invalid extraction ID → 404 error handled
  - Expired presigned URL → error message shown
- [ ] **Keyboard shortcuts**:
  - Press Right Arrow → next page
  - Press Left Arrow → previous page
  - Press `+` → zoom in
  - Press `-` → zoom out

### E2E Tests (Playwright)

- [ ] **Happy path** (`tests/pdf-viewer.spec.ts`):
  ```typescript
  test('user can view PDF and navigate pages', async ({ page }) => {
    // Upload PDF (prerequisite)
    await page.goto('/ingestions/upload')
    await page.setInputFiles('input[type="file"]', 'test-data/sample-10pages.pdf')
    await page.click('button:has-text("Upload")')
    await page.waitForURL(/\/ingestions\/.*\/review/)

    // Verify PDF renders
    await expect(page.locator('canvas')).toBeVisible()
    await expect(page.locator('text=Page 1 of 10')).toBeVisible()

    // Navigate to next page
    await page.click('button[aria-label="Next page"]')
    await expect(page.locator('text=Page 2 of 10')).toBeVisible()

    // Zoom in
    await page.click('button[aria-label="Zoom in"]')
    await expect(page.locator('text=125%')).toBeVisible()
  })
  ```
- [ ] **Error handling**:
  - Corrupted PDF → error message shown
  - Network error (mock failed fetch) → error message shown
- [ ] **Responsive**:
  - Mobile viewport → controls are touch-friendly
  - Tablet viewport → PDF fits width

### Manual Verification

Map to acceptance criteria:
- [ ] **AC1 - Successful rendering**: Upload PDF → navigate to review → renders in <1s
- [ ] **AC2 - Next/Previous**: Navigate between pages → <500ms load time
- [ ] **AC3 - Jump to page**: Enter page number → navigates correctly
- [ ] **AC4 - Zoom**: Zoom in/out → PDF scales correctly
- [ ] **AC5 - Fit Width**: Click Fit Width → PDF fits container
- [ ] **AC6 - Lazy loading**: 25-page PDF → only current page in DOM
- [ ] **AC7 - Loading state**: Slow network → loading spinner shown
- [ ] **AC8 - Corrupted PDF**: Upload corrupted file → error message
- [ ] **AC9 - Network error**: Expired URL → error message
- [ ] **AC10 - Mobile**: View on phone → responsive layout
- [ ] **AC11 - Keyboard**: Arrow keys → navigate pages

---

## 10. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Large PDFs (>20 pages) slow or crash browser** | High (poor UX, browser crash) | Medium | Implement lazy loading (only current page), add warning for PDFs >50 pages, defer virtualization to Epic 9 if needed |
| **PDF.js CDN downtime** | High (viewer unusable) | Low | Use CDN with high SLA (unpkg), add fallback to local bundle in Phase 2, monitor CDN availability |
| **Presigned URLs expire during review** | Medium (user must reload) | Medium | 7-day expiry is sufficient for drafts, implement URL refresh API in Phase 2 if needed |
| **Mobile performance on old devices** | Medium (slow rendering) | Medium | Test on low-end devices (iPhone SE, Android mid-range), reduce default zoom on mobile, add performance warnings |
| **Zoom levels don't fit common worksheet layouts** | Low (minor UX issue) | Low | Test with sample Math worksheets, adjust default Fit Width calculation, allow custom zoom percentages |
| **react-pdf version incompatibility** | Medium (rendering bugs) | Low | Pin exact versions in package.json (react-pdf 9.x, pdfjs-dist 4.x), test on multiple browsers, monitor GitHub issues |
| **Keyboard shortcuts conflict with browser defaults** | Low (minor UX issue) | Low | Use `event.preventDefault()` for custom shortcuts, document shortcuts in help modal (Phase 2) |

---

## 11. Rollout Plan

### Phase 1: MVP (This Epic)
**Timeline**: 5-7 days
**Deliverables**:
- react-pdf integration with PDF.js worker configured
- PDFViewer component with pagination and zoom controls
- Route: `/ingestions/:id/review` with TanStack Query integration
- Custom hook: `usePDFNavigation` for state management
- Loading and error states
- Responsive layout (desktop, tablet, mobile)
- Keyboard shortcuts (arrow keys, +/-)
- Unit tests for hook and component
- E2E test for happy path
- Documentation update (CLAUDE.md)

**Acceptance**:
- All AC scenarios pass
- First page renders in <1s (p95)
- Page navigation <500ms (p95)
- No console errors or warnings
- Mobile responsive (tested on Chrome DevTools device mode)

### Phase 2: Enhancements (Future)
**Deferred features**:
- Text layer rendering (for text selection and copy)
- Search functionality (find text in PDF)
- Thumbnail sidebar (visual page navigation)
- Fullscreen mode
- PDF rotation controls
- Print functionality
- Download button with analytics
- Custom zoom percentages (dropdown)
- Virtualization for very large PDFs (>50 pages)
- Presigned URL auto-refresh API

### Success Metrics

- **First page load time**: <1s at p95 (measured client-side)
- **Page navigation time**: <500ms at p95 (measured client-side)
- **Error rate**: <2% (exclude corrupted PDFs)
- **Mobile usage**: ≥20% of review sessions from mobile/tablet
- **Zoom usage**: ≥50% of users adjust zoom at least once per session
- **User satisfaction**: <5% support tickets related to PDF viewer issues

---

## 12. References

### Context7 Documentation

- **react-pdf** v9.x: Used patterns for Document/Page components, loading states, error handling, onLoadSuccess callbacks, lazy loading strategies
- **PDF.js** v4.x: Worker configuration, Canvas rendering, memory management best practices

### Research Sources

- **react-pdf GitHub Discussion #1691** (2024): Performance optimization with large PDFs - lazy loading, avoiding rendering all pages at once, memory management
- **react-pdf GitHub Issue #94**: Best practices for virtualization - trade-offs between virtualization libraries (react-virtualized, react-window) and react-pdf's built-in lazy loading
- **React Performance Optimization** (2024): Memoization for expensive components, useCallback for event handlers, avoiding unnecessary re-renders
- **Web Performance Best Practices** (2024): Web Workers for heavy computation (PDF.js), Canvas optimization, browser caching strategies

### Codebase References

- **Route pattern**: `frontend/src/routes/_layout/items.tsx` - TanStack Router with query params, pagination
- **Component pattern**: `frontend/src/components/Items/AddItem.tsx` - Dialog component with form, React Hook Form usage
- **Custom hook**: `frontend/src/hooks/useCustomToast.ts` - Hook structure, export pattern
- **API fetching**: `frontend/src/routes/_layout/items.tsx` - TanStack Query with `useQuery`, loading states
- **Error handling**: `frontend/src/utils.ts` - `handleError` function for API errors

---

## Quality Checklist ✅

- [x] Self-contained with full context (Epic 3 scope, dependencies on Epic 2)
- [x] INVEST user stories (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- [x] Complete Gherkin ACs (11 scenarios: rendering, navigation, zoom, lazy loading, loading states, errors, responsive, keyboard)
- [x] No new API endpoints (uses existing `GET /api/v1/ingestions/:id`)
- [x] Error handling defined (corrupted PDFs, network errors, expired URLs)
- [x] Data models documented (TypeScript interfaces for state and props)
- [x] Security addressed (presigned URLs, no XSS risk with Canvas rendering, CSP requirements)
- [x] Performance specified (<1s first page, <500ms navigation, <150MB memory for 20 pages)
- [x] Testing strategy outlined (unit tests for hook, integration tests for component, E2E for happy path)
- [x] Out-of-scope listed (annotations, search, thumbnails, fullscreen, rotation, print, text layer)
- [x] References populated (Context7 docs, research sources, codebase patterns)
- [x] Matches project conventions (TanStack Router, Chakra UI, custom hooks, auto-generated API client)
- [x] Quantifiable requirements (specific timings, zoom percentages, memory limits)

---

**Next Steps**:
1. Review PRD with Frontend and Product teams
2. Clarify zoom default (Fit Width vs Fit Height for typical Math worksheets)
3. Decide on PDF.js worker: CDN (v1) vs local bundle (production)
4. Create Linear issues from deliverables (8-10 issues, 0.5-1 day each):
   - Install dependencies and configure PDF.js worker
   - Create `usePDFNavigation` custom hook with tests
   - Create `PDFViewer` component with tests
   - Create route `$id.review.tsx` with TanStack Query
   - Implement pagination controls
   - Implement zoom controls
   - Add keyboard shortcuts
   - Add responsive layout for mobile/tablet
   - E2E test for happy path
   - Documentation update
5. Begin implementation: Hook → Component → Route → Testing
6. Test on sample Math worksheets from Epic 2 (uploaded PDFs)
