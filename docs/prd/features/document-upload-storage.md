# PRD: Document Upload & Storage

**Version**: 1.0
**Component**: Full-stack (Backend + Frontend)
**Status**: Ready for Implementation
**Last Updated**: 2025-10-22
**Related**: [Product Overview](../overview.md), [Implementation Plan - Math](../implementation-plan-math.md), [Infrastructure Setup](./infrastructure-setup.md)

---

## 1. Overview

### What & Why

Enable Content Reviewers to upload Math worksheet PDFs to the system for extraction processing. This epic establishes the foundational upload workflow: file validation, secure cloud storage via Supabase, presigned URL generation, and extraction record creation. This is **Epic 2** in the Math Question Extraction MVP implementation plan.

**Value**: Provides the entry point for the extraction pipeline. Without upload capability, reviewers cannot process worksheets. This epic unblocks all downstream extraction features (OCR, segmentation, tagging).

### Scope

**In scope**:
- Upload API endpoint (`POST /api/v1/ingestions`) accepting multipart form data
- File validation (PDF/DOCX, max 25MB, MIME type verification)
- Supabase Storage integration (`worksheets` bucket)
- Presigned URL generation with 7-day expiry for draft files
- Extraction record creation with status: UPLOADED
- Metadata extraction (filename, file size, page count, MIME type, upload timestamp)
- Frontend upload form with drag-and-drop or file picker
- Upload progress indicator (0-100%)
- Success/error handling and user feedback
- Row-Level Security (RLS) policies for multi-user isolation

**Out of scope (v1)**:
- Batch/multi-file upload (single file only)
- DOCX support (PDF only for MVP; DOCX deferred to Phase 2)
- Resume failed uploads (chunked upload)
- Client-side compression or preprocessing
- Background job triggering (handled in Epic 8: Background Job Orchestration)
- PDF preview/thumbnail generation
- Virus/malware scanning
- Duplicate detection
- File versioning

### Living Document

This PRD evolves during implementation:
- Adjustments based on Supabase API limitations discovered during integration
- Upload size limits based on production testing (may reduce from 25MB if needed)
- Error handling refinements based on real-world upload failures
- Performance optimizations if upload times exceed 5s for 10MB files

### Non-Functional Requirements

- **Performance**:
  - Upload: <5s for 10MB PDF at p95 (Supabase Storage upload time)
  - API response: <200ms for extraction record creation (p95)
  - Presigned URL generation: <100ms
  - Frontend file selection: <50ms to open file picker
  - Progress updates: Real-time (every 10% or 500ms, whichever is less frequent)
- **Security**:
  - JWT authentication required for upload endpoint
  - Supabase Storage RLS: Users can only upload to their own namespace
  - Presigned URLs: 7-day expiry for draft files, read-only access
  - File type validation: MIME type + magic number verification (prevent spoofing)
  - Path traversal protection: Sanitize filenames, use UUID-based storage paths
  - No execution of uploaded files on server
- **Reliability**:
  - Atomic operations: Upload + record creation in transaction (rollback on failure)
  - Orphaned file cleanup: Background job removes files without DB records (daily cron)
  - Error recovery: Clear error messages with actionable guidance
- **Usability**:
  - Drag-and-drop support for modern browsers
  - File picker fallback for browsers without drag-and-drop
  - Visual feedback: Progress bar, success/error toasts
  - Accessible: Screen reader announcements for upload status

---

## 2. User Stories

### Primary Story
**As a** Content Operations Reviewer (Math teacher/editor)
**I want** to upload Math PDF worksheets securely to the system
**So that** they are stored for processing and I can proceed to extraction

### Supporting Stories

**As a** Content Reviewer
**I want** to see upload progress in real-time
**So that** I know the upload is working and can estimate remaining time

**As a** Content Reviewer
**I want** to receive immediate feedback if my file is rejected (wrong format, too large)
**So that** I can correct the issue without waiting for upload completion

**As a** Content Admin
**I want** uploaded files to be isolated per user with Row-Level Security
**So that** reviewers cannot access each other's uploaded worksheets

**As a** Backend Developer
**I want** a clean separation between upload logic and extraction pipeline
**So that** I can test upload independently and swap storage backends if needed

---

## 3. Acceptance Criteria (Gherkin)

### Scenario: Successful PDF Upload
```gherkin
Given I am logged in as a Content Reviewer
And I have a 5MB Math PDF file "P4_Decimals_Worksheet.pdf"
When I navigate to the upload page
And I drag the file into the drop zone
And I submit the upload
Then the file uploads to Supabase Storage within 5 seconds
And a presigned URL with 7-day expiry is generated
And an extraction record is created with status "UPLOADED"
And I see a success message: "Uploaded successfully. Extraction ID: [uuid]"
And I am redirected to the review page `/ingestions/[id]/review`
```

### Scenario: File Type Validation - Reject Invalid File
```gherkin
Given I am logged in as a Content Reviewer
When I attempt to upload a file "worksheet.docx" (DOCX format)
Then the upload is rejected before submission
And I see an error message: "Invalid file type. Only PDF files are supported."
And no API call is made
```

### Scenario: File Size Validation - Reject Oversized File
```gherkin
Given I am logged in as a Content Reviewer
When I attempt to upload a 30MB PDF file (exceeds 25MB limit)
Then the upload is rejected before submission
And I see an error message: "File too large. Maximum size: 25MB. Your file: 30MB."
And no API call is made
```

### Scenario: Upload Progress Indicator
```gherkin
Given I am uploading a 10MB PDF file
When the upload is in progress
Then I see a progress bar updating from 0% to 100%
And progress updates occur at least every 500ms or every 10% completion
And the submit button is disabled with text "Uploading..."
```

### Scenario: Network Error Handling
```gherkin
Given I am uploading a file
And the network connection is lost mid-upload
When the upload fails
Then I see an error message: "Upload failed. Please check your connection and try again."
And the form is reset to allow retry
And no incomplete extraction record is created
```

### Scenario: Server Error Handling (500)
```gherkin
Given I am uploading a file
And the backend service is unavailable
When the upload request fails with 500 error
Then I see an error message: "Server error. Please try again later. If the issue persists, contact support."
And the form is reset to allow retry
```

### Scenario: Authenticated Access Only
```gherkin
Given I am not logged in
When I attempt to access the upload page
Then I am redirected to the login page
And I see a message: "Please log in to upload worksheets."
```

### Scenario: Metadata Extraction
```gherkin
Given I upload a 12-page PDF file named "Math_Worksheet_Final.pdf" (3.5MB)
When the upload completes successfully
Then the extraction record contains:
  | Field          | Value                              |
  | filename       | "Math_Worksheet_Final.pdf"         |
  | file_size      | 3670016 (bytes)                    |
  | page_count     | 12                                 |
  | mime_type      | "application/pdf"                  |
  | upload_time    | ISO8601 timestamp                  |
  | status         | "UPLOADED"                         |
  | presigned_url  | https://[supabase].co/... (7d exp) |
```

---

## 4. Functional Requirements

### Core Behavior

**Upload Workflow**:
1. User selects file via drag-and-drop or file picker
2. Frontend validates file type (PDF) and size (≤25MB)
3. If validation fails, show inline error (no API call)
4. If validation passes, submit multipart form to `POST /api/v1/ingestions`
5. Backend validates file again (server-side verification)
6. Backend uploads file to Supabase Storage bucket `worksheets`
7. Backend extracts PDF metadata (page count using `pypdf`)
8. Backend generates presigned URL (7-day expiry, read-only)
9. Backend creates extraction record in database
10. Backend returns extraction ID and presigned URL
11. Frontend shows success message and redirects to review page

**File Storage Path** (Supabase):
```
worksheets/
  {user_id}/
    {extraction_id}/
      original.pdf
```

Example: `worksheets/550e8400-e29b-41d4-a716-446655440000/7c9e6679-7425-40de-944b-e07fc1f90ae7/original.pdf`

**Presigned URL**:
- Generated via Supabase Storage API: `storage.from_('worksheets').create_signed_url(path, expiry)`
- Expiry: 604800 seconds (7 days)
- Access: Read-only (no write, delete, or list permissions)
- Auto-refreshed when extraction moves from DRAFT → IN_REVIEW (extend to permanent)

### States & Transitions

| Extraction Status | Description | Triggered By | Next States |
|-------------------|-------------|--------------|-------------|
| **UPLOADED** | File successfully uploaded, awaiting processing | Upload API endpoint | OCR_PROCESSING (Epic 4), FAILED |
| **FAILED** | Upload or validation failed | Upload error | None (terminal state, allows retry) |

### Business Rules

1. **Single PDF per upload**: One file at a time (no batch upload in v1)
2. **File size limit**: 25MB maximum (enforced on frontend and backend)
3. **Supported formats**: PDF only (DOCX deferred to Phase 2)
4. **File naming**: Original filename stored for reference, but storage path uses `{extraction_id}/original.pdf` (UUID-based, prevents collisions)
5. **Presigned URL expiry**: 7 days for DRAFT status, permanent (no expiry) for APPROVED status
6. **User isolation**: Each user's files stored in `worksheets/{user_id}/` namespace (RLS enforced)
7. **Orphaned file cleanup**: Daily cron job removes files uploaded >24h ago without extraction record (handles partial failures)
8. **Filename sanitization**: Remove special characters, limit to 255 characters, preserve extension
9. **Duplicate filenames**: Allowed (storage path is unique per extraction_id)

### Permissions

- **Access**: Authenticated users only (JWT required)
- **Upload**: User can upload to their own namespace (`worksheets/{user_id}/`)
- **Read**: User can access presigned URLs for their own extractions
- **Delete**: Not exposed in v1 (admin-only via Supabase dashboard)
- **RLS Policies** (Supabase):
  ```sql
  -- Upload policy
  CREATE POLICY "Users can upload to own namespace" ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (
    bucket_id = 'worksheets'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

  -- Read policy
  CREATE POLICY "Users can read own files" ON storage.objects FOR SELECT
  TO authenticated
  USING (
    bucket_id = 'worksheets'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );
  ```

---

## 5. Technical Specification

### Architecture Pattern

**Layered Backend Architecture** (matches existing FastAPI project structure):
- **Route Layer** (`app/api/routes/ingestions.py`): Handles HTTP request/response, file upload
- **Service Layer** (`app/services/storage.py`): Supabase Storage integration, presigned URL generation
- **Model Layer** (`app/models.py`): SQLModel schemas for Extraction table
- **Dependency Layer** (`app/api/deps.py`): JWT authentication, database session

**Rationale**: This pattern is consistent with existing `items.py` route structure. Separating storage logic into a service layer enables easy testing and future backend swaps (e.g., S3 instead of Supabase).

**Frontend Pattern** (TanStack Router + React Hook Form):
- **Route** (`frontend/src/routes/_layout/ingestions/upload.tsx`): Upload page component
- **Form Component** (`frontend/src/components/Ingestions/UploadForm.tsx`): Reusable upload form
- **Custom Hook** (`frontend/src/hooks/useFileUpload.ts`): Upload logic with progress tracking
- **API Client** (`frontend/src/client/`): Auto-generated OpenAPI client

**Rationale**: Matches existing pattern in `items.tsx`. Custom hook encapsulates upload state management (progress, errors) for reusability.

### API Endpoints

#### `POST /api/v1/ingestions`
**Purpose**: Upload PDF worksheet and create extraction record

**Request** (multipart/form-data):
```
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="worksheet.pdf"
Content-Type: application/pdf

<binary PDF data>
--boundary--
```

**FastAPI Signature**:
```python
@router.post("/", response_model=IngestionPublic)
def create_ingestion(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="PDF worksheet file")
) -> Any:
    """
    Upload PDF worksheet and create extraction record.

    Validates file type, size, uploads to Supabase Storage,
    extracts metadata, and creates extraction record.
    """
```

**Response** (201 Created):
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "filename": "P4_Decimals_Worksheet.pdf",
  "file_size": 5242880,
  "page_count": 10,
  "mime_type": "application/pdf",
  "status": "UPLOADED",
  "presigned_url": "https://[project].supabase.co/storage/v1/object/sign/worksheets/550e.../original.pdf?token=...",
  "uploaded_at": "2025-10-22T14:30:00Z",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Errors**:
- `400 Bad Request`: Invalid file type, file too large, missing file
  ```json
  {"detail": "Invalid file type. Only PDF files are supported."}
  ```
- `401 Unauthorized`: Missing or invalid JWT token
- `413 Payload Too Large`: File exceeds 25MB (Nginx/server limit)
- `422 Unprocessable Entity`: Validation errors (malformed PDF, corrupted file)
  ```json
  {"detail": "Could not extract page count. PDF may be corrupted."}
  ```
- `500 Internal Server Error`: Supabase upload failure, database error
  ```json
  {"detail": "Upload failed. Please try again."}
  ```

**Rate Limiting**: 10 requests/minute per user (prevent abuse)

---

### Data Models

**Backend SQLModel** (`app/models.py`):
```python
from datetime import datetime
from enum import Enum
import uuid

from sqlmodel import Field, Relationship, SQLModel


class ExtractionStatus(str, Enum):
    """Extraction pipeline status enum"""
    UPLOADED = "UPLOADED"
    OCR_PROCESSING = "OCR_PROCESSING"
    OCR_COMPLETE = "OCR_COMPLETE"
    SEGMENTATION_PROCESSING = "SEGMENTATION_PROCESSING"
    SEGMENTATION_COMPLETE = "SEGMENTATION_COMPLETE"
    TAGGING_PROCESSING = "TAGGING_PROCESSING"
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


# Shared properties
class IngestionBase(SQLModel):
    filename: str = Field(max_length=255, description="Original filename")
    file_size: int = Field(gt=0, description="File size in bytes")
    page_count: int | None = Field(default=None, description="Number of pages in PDF")
    mime_type: str = Field(max_length=100, description="MIME type (application/pdf)")
    status: ExtractionStatus = Field(default=ExtractionStatus.UPLOADED)


# Properties to receive via API on creation (not used, file upload instead)
class IngestionCreate(IngestionBase):
    pass


# Database model, database table inferred from class name
class Ingestion(IngestionBase, table=True):
    __tablename__ = "extractions"  # Table name matches domain: extractions

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    presigned_url: str = Field(max_length=2048, description="Supabase presigned URL")
    storage_path: str = Field(max_length=512, description="Storage path in Supabase")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: "User" = Relationship(back_populates="ingestions")


# Properties to return via API
class IngestionPublic(IngestionBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    presigned_url: str
    uploaded_at: datetime


class IngestionsPublic(SQLModel):
    data: list[IngestionPublic]
    count: int


# Add to User model
class User(UserBase, table=True):
    # ... existing fields ...
    ingestions: list["Ingestion"] = Relationship(back_populates="owner", cascade_delete=True)
```

**TypeScript Interface** (frontend, auto-generated from OpenAPI):
```typescript
export interface IngestionPublic {
  id: string;                // UUID
  filename: string;          // Original filename
  file_size: number;         // Bytes
  page_count: number | null; // Number of pages
  mime_type: string;         // "application/pdf"
  status: ExtractionStatus;  // "UPLOADED"
  presigned_url: string;     // Supabase signed URL
  uploaded_at: string;       // ISO8601
  owner_id: string;          // User UUID
}

export enum ExtractionStatus {
  UPLOADED = "UPLOADED",
  OCR_PROCESSING = "OCR_PROCESSING",
  // ... other statuses
}
```

### Database Schema

**Migration**: `backend/app/alembic/versions/[timestamp]_add_extractions_table.py`

```sql
-- Create enum type for extraction status
CREATE TYPE extraction_status AS ENUM (
    'UPLOADED',
    'OCR_PROCESSING',
    'OCR_COMPLETE',
    'SEGMENTATION_PROCESSING',
    'SEGMENTATION_COMPLETE',
    'TAGGING_PROCESSING',
    'DRAFT',
    'IN_REVIEW',
    'APPROVED',
    'REJECTED',
    'FAILED'
);

-- Create extractions table
CREATE TABLE extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL CHECK (file_size > 0),
    page_count INTEGER,
    mime_type VARCHAR(100) NOT NULL,
    status extraction_status NOT NULL DEFAULT 'UPLOADED',
    presigned_url VARCHAR(2048) NOT NULL,
    storage_path VARCHAR(512) NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_extractions_owner_id ON extractions(owner_id);
CREATE INDEX idx_extractions_status ON extractions(status);
CREATE INDEX idx_extractions_uploaded_at ON extractions(uploaded_at DESC);

-- Trigger to update updated_at
CREATE TRIGGER update_extractions_updated_at BEFORE UPDATE ON extractions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Note**: `update_updated_at_column()` function should already exist from User table migrations.

---

## 6. Integration Points

### Dependencies

**Backend Python Packages** (add to `pyproject.toml`):
```toml
[project.dependencies]
# Existing: fastapi, sqlmodel, pydantic, alembic, psycopg, ...

# New for upload & storage:
"supabase<3.0.0,>=2.0.0"              # Supabase Python client
"pypdf<4.0.0,>=3.0.0"                 # PDF metadata extraction (page count)
"python-multipart<1.0.0,>=0.0.7"      # Already exists - multipart form handling
```

**Frontend Packages** (add to `package.json`):
```json
{
  "dependencies": {
    // Existing: react, @tanstack/react-router, react-hook-form, ...

    // New for upload:
    "@supabase/supabase-js": "^2.45.0"  // Optional: for client-side presigned URL refresh
  }
}
```

**External Services**:
- **Supabase Storage**: Object storage with S3-compatible API
  - Bucket: `worksheets` (private, RLS enabled)
  - Endpoint: `https://[project].supabase.co/storage/v1`
- **Supabase Postgres**: Database for extraction records (via existing DATABASE_URL)

**Internal Dependencies**:
- `app/core/config.py`: Add Supabase configuration
  ```python
  class Settings(BaseSettings):
      # ... existing fields ...

      # Supabase
      SUPABASE_URL: str
      SUPABASE_KEY: str  # Anon public key
      SUPABASE_SERVICE_KEY: str  # Service role key (backend only)
      SUPABASE_STORAGE_BUCKET_WORKSHEETS: str = "worksheets"
  ```
- `app/api/deps.py`: Existing JWT authentication dependency (`CurrentUser`)
- `app/models.py`: User model (add `ingestions` relationship)

### Events/Webhooks

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| `ingestion.uploaded` | `POST /api/v1/ingestions` success | `{ingestion_id, status: "UPLOADED", owner_id}` | (Future) WebSocket notification to frontend |
| `ingestion.failed` | Upload validation/storage failure | `{error_type, error_message, owner_id}` | Sentry error tracking |

**Note**: Event system not implemented in v1. Backend emits logs only. WebSocket notifications deferred to Phase 3.

---

## 7. UX Specifications

### Key UI States

1. **Initial (Empty)**:
   - Drag-and-drop zone with dashed border
   - Message: "Drag and drop a PDF file here, or click to select"
   - File picker button: "Choose File"
   - Supported formats note: "PDF files only, max 25MB"

2. **File Selected (Pre-Upload)**:
   - Show selected filename, file size
   - Preview icon (PDF icon)
   - "Upload" button enabled (primary color)
   - "Cancel" button to reset

3. **Uploading (In Progress)**:
   - Progress bar with percentage: "Uploading... 45%"
   - Estimated time remaining (if available): "~10 seconds remaining"
   - "Upload" button disabled with spinner: "Uploading..."
   - Cancel button disabled (prevent mid-upload cancellation in v1)

4. **Upload Success**:
   - Green checkmark icon
   - Success message: "✓ Uploaded successfully! Extraction ID: [uuid]"
   - Auto-redirect to review page after 2 seconds
   - "View Extraction" button (immediate redirect)

5. **Upload Error**:
   - Red error icon
   - Error message: "✗ Upload failed: [specific error]"
   - "Try Again" button (resets form)
   - Help text: "If issue persists, contact support"

### Component Structure (Frontend)

**Route**: `frontend/src/routes/_layout/ingestions/upload.tsx`
```tsx
import { UploadForm } from '@/components/Ingestions/UploadForm'

export const Route = createFileRoute('/_layout/ingestions/upload')({
  component: UploadPage,
})

function UploadPage() {
  return (
    <Container maxW="container.md" py={8}>
      <Heading mb={6}>Upload Worksheet</Heading>
      <UploadForm />
    </Container>
  )
}
```

**Component**: `frontend/src/components/Ingestions/UploadForm.tsx`
```tsx
import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Box, Button, Progress, Text, VStack } from '@chakra-ui/react'
import { useFileUpload } from '@/hooks/useFileUpload'
import { IngestionsService } from '@/client'

export function UploadForm() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const { upload, progress, isUploading, error } = useFileUpload()

  const handleSubmit = async () => {
    if (!file) return

    const result = await upload(file)
    if (result.success) {
      // Redirect to review page
      navigate({ to: `/ingestions/${result.data.id}/review` })
    }
  }

  return (
    <VStack spacing={4} align="stretch">
      {/* Drag-and-drop zone */}
      <Box
        border="2px dashed"
        borderColor="gray.300"
        borderRadius="md"
        p={8}
        textAlign="center"
        cursor="pointer"
        _hover={{ borderColor: 'blue.500' }}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <Text>Drag and drop a PDF file here, or click to select</Text>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileSelect}
          hidden
          ref={fileInputRef}
        />
        <Button mt={4} onClick={() => fileInputRef.current?.click()}>
          Choose File
        </Button>
      </Box>

      {/* File info */}
      {file && !isUploading && (
        <Box>
          <Text>Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</Text>
        </Box>
      )}

      {/* Progress bar */}
      {isUploading && (
        <Box>
          <Progress value={progress} size="sm" colorScheme="blue" />
          <Text fontSize="sm" color="gray.600">Uploading... {progress}%</Text>
        </Box>
      )}

      {/* Error message */}
      {error && (
        <Text color="red.500">✗ {error}</Text>
      )}

      {/* Submit button */}
      <Button
        colorScheme="blue"
        onClick={handleSubmit}
        isDisabled={!file || isUploading}
        isLoading={isUploading}
        loadingText="Uploading..."
      >
        Upload
      </Button>
    </VStack>
  )
}
```

**Custom Hook**: `frontend/src/hooks/useFileUpload.ts`
```tsx
import { useState } from 'react'
import axios, { AxiosProgressEvent } from 'axios'
import { IngestionsService, IngestionPublic } from '@/client'

export function useFileUpload() {
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const upload = async (file: File) => {
    setIsUploading(true)
    setError(null)
    setProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const result = await axios.post<IngestionPublic>(
        '/api/v1/ingestions',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 1)
            )
            setProgress(percentCompleted)
          },
        }
      )

      return { success: true, data: result.data }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Upload failed. Please try again.'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setIsUploading(false)
    }
  }

  return { upload, progress, isUploading, error }
}
```

### Responsive Behavior

- **Desktop (≥1024px)**:
  - Upload form centered, max-width 600px
  - Drag-and-drop zone 400px height
  - Progress bar full width

- **Tablet (768px-1023px)**:
  - Upload form full width with 16px padding
  - Drag-and-drop zone 300px height

- **Mobile (<768px)**:
  - Upload form full width with 8px padding
  - Drag-and-drop zone 200px height
  - File picker button primary interaction (drag-and-drop optional)

---

## 8. Implementation Guidance

### Follow Existing Patterns

**Based on codebase analysis**:

- **File structure**: Place route in `backend/app/api/routes/ingestions.py` (matches `items.py`)
- **Naming**: Use `IngestionBase`, `Ingestion`, `IngestionPublic` (matches `ItemBase`, `Item`, `ItemPublic`)
- **Error handling**: Return `HTTPException` with status codes and detail messages (matches `items.py` pattern)
  ```python
  raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")
  ```
- **Testing**: Place tests in `backend/tests/api/routes/test_ingestions.py` (matches `test_items.py`)
- **Frontend route**: Use TanStack Router file-based routing: `frontend/src/routes/_layout/ingestions/upload.tsx`
- **Component structure**: Separate form logic into `components/Ingestions/UploadForm.tsx` (matches `components/Items/AddItem.tsx`)

### Recommended Approach

**Backend Implementation Steps**:

1. **Add Supabase config** to `app/core/config.py`:
   ```python
   SUPABASE_URL: str
   SUPABASE_KEY: str
   SUPABASE_SERVICE_KEY: str
   SUPABASE_STORAGE_BUCKET_WORKSHEETS: str = "worksheets"
   ```

2. **Create storage service** (`app/services/storage.py`):
   ```python
   from supabase import create_client, Client
   from app.core.config import settings

   def get_supabase_client() -> Client:
       return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

   def upload_to_supabase(
       file_path: str,
       file_bytes: bytes,
       content_type: str
   ) -> str:
       """Upload file to Supabase Storage, return storage path"""
       supabase = get_supabase_client()
       response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS).upload(
           path=file_path,
           file=file_bytes,
           file_options={"content-type": content_type}
       )
       return file_path

   def generate_presigned_url(storage_path: str, expiry_seconds: int = 604800) -> str:
       """Generate presigned URL with 7-day expiry"""
       supabase = get_supabase_client()
       response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET_WORKSHEETS).create_signed_url(
           path=storage_path,
           expires_in=expiry_seconds
       )
       return response['signedURL']
   ```

3. **Extract PDF metadata**:
   ```python
   from pypdf import PdfReader

   def get_pdf_page_count(file_bytes: bytes) -> int:
       """Extract page count from PDF"""
       reader = PdfReader(io.BytesIO(file_bytes))
       return len(reader.pages)
   ```

4. **Create API route** (`app/api/routes/ingestions.py`):
   ```python
   from fastapi import APIRouter, UploadFile, File, HTTPException
   from app.api.deps import CurrentUser, SessionDep
   from app.models import Ingestion, IngestionPublic
   from app.services.storage import upload_to_supabase, generate_presigned_url
   import uuid

   router = APIRouter(prefix="/ingestions", tags=["ingestions"])

   @router.post("/", response_model=IngestionPublic, status_code=201)
   async def create_ingestion(
       *,
       session: SessionDep,
       current_user: CurrentUser,
       file: UploadFile = File(..., description="PDF worksheet file")
   ) -> Any:
       # Validate file type
       if file.content_type != "application/pdf":
           raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

       # Validate file size (25MB)
       file_bytes = await file.read()
       if len(file_bytes) > 25 * 1024 * 1024:
           raise HTTPException(status_code=400, detail=f"File too large. Maximum size: 25MB.")

       # Extract metadata
       try:
           page_count = get_pdf_page_count(file_bytes)
       except Exception as e:
           raise HTTPException(status_code=422, detail="Could not extract page count. PDF may be corrupted.")

       # Generate storage path
       extraction_id = uuid.uuid4()
       storage_path = f"{current_user.id}/{extraction_id}/original.pdf"

       # Upload to Supabase
       try:
           upload_to_supabase(storage_path, file_bytes, "application/pdf")
       except Exception as e:
           raise HTTPException(status_code=500, detail="Upload failed. Please try again.")

       # Generate presigned URL
       presigned_url = generate_presigned_url(storage_path)

       # Create extraction record
       ingestion = Ingestion(
           id=extraction_id,
           owner_id=current_user.id,
           filename=file.filename,
           file_size=len(file_bytes),
           page_count=page_count,
           mime_type="application/pdf",
           presigned_url=presigned_url,
           storage_path=storage_path,
           status="UPLOADED"
       )
       session.add(ingestion)
       session.commit()
       session.refresh(ingestion)

       return ingestion
   ```

5. **Add migration** (Alembic):
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add extractions table"
   alembic upgrade head
   ```

**Frontend Implementation Steps**:

1. **Create route** (`frontend/src/routes/_layout/ingestions/upload.tsx`)
2. **Create UploadForm component** (`frontend/src/components/Ingestions/UploadForm.tsx`)
3. **Create useFileUpload hook** (`frontend/src/hooks/useFileUpload.ts`)
4. **Regenerate API client** after backend OpenAPI changes:
   ```bash
   cd frontend
   npm run generate-client
   ```

### Security Considerations

- **File type validation**: Verify MIME type AND magic number (first bytes of file) to prevent spoofing
  ```python
  # Check magic number for PDF (%PDF-)
  if not file_bytes.startswith(b'%PDF-'):
      raise HTTPException(status_code=400, detail="Invalid PDF file.")
  ```
- **Path traversal**: Use UUID-based storage paths, sanitize filenames
- **Presigned URL expiry**: 7 days for drafts, permanent for approved (refresh on status change)
- **Row-Level Security**: Enforce user isolation via Supabase RLS policies
- **Rate limiting**: 10 uploads/minute per user (prevent abuse)
- **No file execution**: Never execute uploaded files on server

### Performance Optimization

- **Chunked uploads**: Not in v1 (single request), defer to Phase 2 if needed
- **Compression**: Not in v1 (upload original PDF as-is), defer to Phase 2
- **Lazy metadata extraction**: Extract page count asynchronously if it slows upload (move to Celery task)
- **CDN for presigned URLs**: Supabase Storage has built-in CDN

### Observability

- **Logs**:
  - `INFO`: Successful upload (ingestion_id, filename, file_size, user_id)
  - `ERROR`: Upload failures (error_type, user_id, filename)
- **Metrics**:
  - Upload success rate (%)
  - Average upload time (seconds)
  - File size distribution (histogram)
  - Upload errors by type (400/422/500)
- **Alerts**:
  - Upload error rate >5% (5-minute window)
  - Supabase API failure (3 consecutive failures)

---

## 9. Testing Strategy

### Unit Tests

- [ ] **File validation**:
  - Valid PDF → passes
  - DOCX file → rejected with 400
  - File >25MB → rejected with 400
  - Corrupted PDF → rejected with 422
- [ ] **PDF metadata extraction**:
  - 10-page PDF → page_count = 10
  - 1-page PDF → page_count = 1
  - Encrypted PDF → throws exception
- [ ] **Storage path generation**:
  - UUID-based path format: `{user_id}/{extraction_id}/original.pdf`
  - No path traversal vulnerabilities
- [ ] **Presigned URL generation**:
  - URL contains `token=` query param
  - URL expires in 7 days (604800 seconds)
- [ ] **Filename sanitization**:
  - Special characters removed
  - Length limited to 255 characters

### Integration Tests

- [ ] **Upload workflow** (`test_ingestions.py`):
  ```python
  def test_create_ingestion_success(client, normal_user_token_headers, db):
      """Test successful PDF upload"""
      with open("test_data/sample.pdf", "rb") as f:
          response = client.post(
              "/api/v1/ingestions",
              headers=normal_user_token_headers,
              files={"file": ("sample.pdf", f, "application/pdf")}
          )
      assert response.status_code == 201
      data = response.json()
      assert data["filename"] == "sample.pdf"
      assert data["status"] == "UPLOADED"
      assert "presigned_url" in data

      # Verify in database
      ingestion = db.query(Ingestion).filter(Ingestion.id == data["id"]).first()
      assert ingestion is not None
      assert ingestion.page_count > 0
  ```
- [ ] **Supabase Storage integration**:
  - Upload file → verify file exists in bucket
  - Generate presigned URL → verify URL is accessible
  - User isolation → verify user A cannot access user B's files
- [ ] **Error handling**:
  - Invalid file type → 400 error
  - File too large → 400 error
  - Corrupted PDF → 422 error
  - Supabase API failure → 500 error (mock failure)

### E2E Tests (Playwright)

- [ ] **Upload happy path** (`tests/ingestion-upload.spec.ts`):
  ```typescript
  test('user can upload PDF worksheet', async ({ page }) => {
    await page.goto('/ingestions/upload')

    // Upload file
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles('test-data/sample.pdf')

    // Submit
    await page.click('button:has-text("Upload")')

    // Wait for success
    await expect(page.locator('text=Uploaded successfully')).toBeVisible()

    // Verify redirect to review page
    await expect(page).toHaveURL(/\/ingestions\/[a-f0-9-]+\/review/)
  })
  ```
- [ ] **File validation errors**:
  - Upload DOCX → error message displayed
  - Upload 30MB file → error message displayed
- [ ] **Progress indicator**:
  - Upload large file (15MB) → progress bar visible and updates

### Manual Verification

Map to acceptance criteria:
- [ ] **AC1 - Successful upload**: Upload 5MB PDF → success in <5s, extraction created
- [ ] **AC2 - File type validation**: Upload DOCX → rejected before API call
- [ ] **AC3 - File size validation**: Upload 30MB PDF → rejected before API call
- [ ] **AC4 - Progress indicator**: Upload 10MB PDF → progress bar updates every 10%
- [ ] **AC5 - Network error**: Disconnect mid-upload → error message shown
- [ ] **AC6 - Server error**: Stop backend → 500 error handled gracefully
- [ ] **AC7 - Authentication**: Access upload page logged out → redirected to login
- [ ] **AC8 - Metadata extraction**: Upload 12-page PDF → metadata correct in DB

---

## 10. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Supabase free tier limits exceeded** | High (upload blocked) | Medium | Monitor storage usage, add alerts at 80% quota, upgrade to paid tier before limits hit |
| **Large file uploads timeout** | Medium (poor UX) | Medium | Set Nginx/FastAPI timeout to 60s, implement chunked uploads in Phase 2 if needed |
| **Corrupted PDFs break metadata extraction** | Medium (422 errors) | Low | Graceful error handling, log failures, allow upload without page_count (set to NULL) |
| **Presigned URLs expire before user reviews** | Low (minor UX issue) | Low | Refresh presigned URLs when user accesses review page (check expiry <24h, regenerate if needed) |
| **Path traversal vulnerability** | High (security) | Low | Use UUID-based paths only, never use user-provided filenames in storage path |
| **Orphaned files in storage** | Low (storage bloat) | Medium | Daily cron job to cleanup files >7 days old without extraction record |
| **Upload quota abuse** | Medium (cost) | Low | Rate limiting (10/minute per user), monitor usage patterns, block abusive users |

---

## 11. Rollout Plan

### Phase 1: MVP (This Epic)
**Timeline**: 5-7 days
**Deliverables**:
- Backend API endpoint with Supabase integration
- Frontend upload form with drag-and-drop
- Database migration (extractions table)
- Unit + integration tests
- E2E test for happy path
- Documentation (API docs, user guide)

**Acceptance**:
- All AC scenarios pass
- Upload success rate ≥95% in dev environment
- Manual testing on staging environment

### Phase 2: Enhancements (Future)
**Deferred features**:
- DOCX support (requires different metadata extraction)
- Batch/multi-file upload
- Chunked upload for files >25MB
- Resume failed uploads
- Client-side PDF compression
- Thumbnail generation

### Success Metrics

- **Upload success rate**: ≥95% (exclude user errors like invalid file type)
- **Upload time**: <5s for 10MB PDF at p95
- **Metadata extraction accuracy**: 100% for page_count (non-corrupted PDFs)
- **User satisfaction**: <5% support tickets related to upload issues
- **Storage quota**: <50% of Supabase free tier in first month

---

## 12. References

### Codebase References

- **Similar route implementation**: `backend/app/api/routes/items.py` - CRUD pattern, error handling
- **Model pattern**: `backend/app/models.py` - SQLModel schemas (UserBase, User, UserPublic)
- **Authentication**: `backend/app/api/deps.py` - `CurrentUser` dependency
- **Frontend form pattern**: `frontend/src/components/Items/AddItem.tsx` - React Hook Form usage
- **Route structure**: `frontend/src/routes/_layout/items.tsx` - TanStack Router pattern

### External Documentation

- **Supabase Storage**: https://supabase.com/docs/guides/storage
  - Presigned URLs: https://supabase.com/docs/guides/storage/uploads/presigned-urls
  - RLS policies: https://supabase.com/docs/guides/storage/security/access-control
- **pypdf Documentation**: https://pypdf.readthedocs.io/en/stable/
  - PdfReader for metadata extraction
- **FastAPI File Uploads**: https://fastapi.tiangolo.com/tutorial/request-files/
  - UploadFile with multipart/form-data
- **React Hook Form**: https://react-hook-form.com/docs
  - Form validation patterns

### Research Sources

- **File upload best practices** (2024): Client-side validation, chunked uploads, progress tracking
- **Presigned URL security**: Expiry times, read-only access, token rotation
- **PDF metadata extraction**: pypdf vs pdfplumber (pypdf is lighter, sufficient for page count)

---

## Quality Checklist ✅

- [x] Self-contained with full context (no external dependencies beyond infrastructure)
- [x] INVEST user stories (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- [x] Complete Gherkin ACs (8 scenarios: happy path, file validation, progress, errors, auth, metadata)
- [x] API contract with request/response schemas and error codes
- [x] Error handling defined (400, 401, 413, 422, 500)
- [x] Data models documented (SQLModel, TypeScript interfaces, SQL schema)
- [x] Security addressed (JWT auth, RLS, presigned URLs, file validation, rate limiting)
- [x] Performance specified (<5s upload, <200ms API, <100ms presigned URL generation)
- [x] Testing strategy outlined (unit, integration, E2E, manual verification)
- [x] Out-of-scope listed (DOCX, batch upload, chunked upload, resume upload)
- [x] References populated (codebase patterns, Supabase docs, FastAPI docs)
- [x] Matches project conventions (SQLModel, FastAPI router, TanStack Router)
- [x] Quantifiable requirements (no vague terms like "fast" or "user-friendly")

---

**Next Steps**:
1. Review PRD with Product, Backend, and Frontend teams
2. Clarify any ambiguities (file size limit, presigned URL expiry, error messages)
3. Create Linear issues from deliverables (10-12 issues, 0.5-1 day each)
4. Set up Supabase project and storage bucket (prerequisite)
5. Begin implementation: Backend route → Frontend form → Integration testing
