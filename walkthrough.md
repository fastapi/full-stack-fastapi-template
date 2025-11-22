# Document Lifecycle Management System Walkthrough

## Overview
Implementation of a production-grade Document Lifecycle Management System with complete lifecycle automation from creation through secure disposal.

## Changes

### Phase 1: Foundation
**Database Schema**:
- `documents`: Core document metadata with status tracking
- `document_versions`: Version history with file paths
- `workflows`: Configurable approval workflows
- `workflow_steps`: Individual workflow stages
- `audit_logs`: Comprehensive audit trail
- `retention_policies`: Automated retention rules

**Models Refactored**: Converted `models.py` to package structure

### Phase 2: Advanced Features

**File Management**:
- Multipart file upload with secure storage
- File download and streaming
- Metadata extraction (size, type, timestamps)

**Document Locking**:
- `document_locks`: Check-in/check-out system
- Concurrent access prevention
- Lock expiration (24 hours default)
- Admin force-unlock capability

**Workflow Engine**:
- `document_workflow_instances`: Execution tracking
- `workflow_actions`: Approval/rejection history
- State machine: Draft → In Review → Approved
- Automatic document status updates

**Version Management**:
- Version rollback with file copying
- Version comparison with metadata diff
- Complete version history tracking

**Retention & Archival**:
- APScheduler integration with FastAPI lifespan
- Daily retention policy evaluation (2 AM)
- Automated archival (status change)
- GDPR-compliant disposal (secure file deletion)
- Manual archival/disposal endpoints (admin)

### API Endpoints

**Documents**:
- `POST /api/v1/documents/`: Create document with file upload
- `GET /api/v1/documents/{id}`: Get document metadata
- `GET /api/v1/documents/{id}/content`: Download file
- `GET /api/v1/documents/{id}/versions`: List all versions
- `GET /api/v1/documents/{id}/metadata`: Get file metadata

**Lifecycle**:
- `POST /api/v1/documents/{id}/checkout`: Lock document
- `POST /api/v1/documents/{id}/checkin`: Upload new version & unlock
- `POST /api/v1/documents/{id}/submit?workflow_id=`: Submit to workflow
- `POST /api/v1/documents/{id}/rollback/{version_id}`: Revert to version

**Versions**:
- `GET /api/v1/documents/{id}/compare/{v1}/{v2}`: Compare versions
- `GET /api/v1/documents/{id}/metadata`: Extract file metadata

**Workflows**:
- `POST /api/v1/workflows/`: Create workflow
- `POST /api/v1/workflows/{id}/steps`: Add workflow step
- `POST /api/v1/workflows/instances/{id}/approve`: Approve current step
- `POST /api/v1/workflows/instances/{id}/reject`: Reject workflow

**Admin** (Superuser only):
- `POST /api/v1/admin/documents/{id}/archive`: Manual archive
- `POST /api/v1/admin/documents/{id}/dispose`: Secure disposal
- `POST /api/v1/admin/documents/{id}/force-unlock`: Break lock

## Verification

### Automated Tests
- `test_documents.py`: Document CRUD operations
- `test_document_lifecycle.py`: Lifecycle flows, locking, workflows

**Run tests**:
```bash
docker-compose up -d db
pytest backend/tests/
```

### Manual Testing

1. **Start services**:
```bash
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

2. **Access Swagger UI**: `http://localhost:8000/docs`

3. **Test Document Lifecycle**:
   - Create document with file upload
   - Checkout → Edit → Checkin (new version)
   - Create workflow with 2 steps
   - Submit document to workflow
   - Approve each step
   - Verify document status = "Approved"

4. **Test Retention**:
   - Create retention policy (short duration for testing)
   - Assign to document
   - Wait for scheduler or trigger manually
   - Verify archival/disposal

5. **Test Admin Functions**:
   - Force-unlock a checked-out document
   - Manually archive a document
   - Dispose of a document (verify file deletion)

### Background Jobs

The scheduler runs:
- **Retention Evaluation**: Daily at 2 AM
- Checks all documents with retention policies
- Archives or disposes based on policy action

## Architecture Notes

**Storage**: Local filesystem (configurable for S3 in production)
**Scheduler**: APScheduler with AsyncIO backend
**Audit Trail**: All lifecycle actions logged to `audit_logs`
**Security**: Superuser-only endpoints for destructive actions
