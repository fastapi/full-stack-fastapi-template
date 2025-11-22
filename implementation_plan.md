# Document Lifecycle Management System - Full Implementation Plan

## Goal Description
Create a production-grade Document Lifecycle Management (DLM) system that handles the complete document lifecycle from creation through secure disposal, including:
- **File Management**: Upload, storage, versioning, rollback
- **Check-in/Check-out**: Concurrent access control with locking
- **Approval Workflows**: Configurable multi-step approval processes
- **E-Signature Integration**: DocuSign/Adobe Sign support
- **Retention Policies**: Automated archival and GDPR-compliant disposal
- **Notifications**: Email and webhook alerts for workflow events
- **RBAC**: Fine-grained document permissions
- **Audit Logging**: Comprehensive compliance tracking

## User Review Required

> [!IMPORTANT]
> **Database Schema Expansion**: Adding several new tables:
> - `document_locks`: Check-in/check-out locking mechanism
> - `document_workflow_instances`: Workflow execution state
> - `document_permissions`: RBAC for documents
> - `signature_requests`: E-signature tracking
> - `notifications`: Notification queue
> 
> **External Dependencies**:
> - File storage (local for dev, S3 for production)
> - Background task scheduler (APScheduler or Celery)
> - Email service (SMTP configuration)
> - Optional: DocuSign/Adobe Sign API keys
> - Optional: LDAP/AD server for authentication
>
> **Breaking Changes**: Adding `status` field to `Document` model for lifecycle state tracking

## Proposed Changes

### Phase 2: Advanced Features

#### [NEW] `backend/app/models/document_lock.py`
Document locking system for check-in/check-out:
- `DocumentLock`: Tracks who has a document checked out
- Fields: `document_id`, `locked_by`, `locked_at`, `expires_at`

#### [NEW] `backend/app/models/workflow_instance.py`
Workflow execution tracking:
- `DocumentWorkflowInstance`: Links documents to workflows
- `WorkflowStepInstance`: Tracks progress through workflow steps
- `WorkflowAction`: Records approval/rejection decisions

#### [MODIFY] `backend/app/models/document.py`
Add lifecycle status tracking:
- Add `status` enum: Draft, In Review, Approved, Distributed, Archived, Disposed
- Add `current_workflow_id` relationship

#### [NEW] `backend/app/services/file_storage.py`
File upload/download service:
- `upload_file()`: Handle multipart uploads, generate secure paths
- `download_file()`: Stream file responses
- `delete_file()`: Secure file deletion
- S3-compatible interface for production

#### [NEW] `backend/app/services/workflow_engine.py`
Workflow state machine:
- `submit_for_review()`: Transition Draft → In Review
- `approve_step()`: Progress through workflow
- `reject_step()`: Send back to previous step
- `complete_workflow()`: Transition to Distributed

#### [NEW] `backend/app/api/routes/document_lifecycle.py`
Lifecycle management endpoints:
- `POST /documents/{id}/checkout`: Acquire lock
- `POST /documents/{id}/checkin`: Release lock + create version
- `POST /documents/{id}/submit`: Start workflow
- `POST /workflows/instances/{id}/approve`: Approve current step
- `POST /workflows/instances/{id}/reject`: Reject and send back
- `POST /documents/{id}/rollback/{version_id}`: Restore version

---

### Phase 3: Integrations

#### [NEW] `backend/app/models/signature_request.py`
E-signature tracking:
- `SignatureRequest`: DocuSign/Adobe Sign integration
- Fields: `document_id`, `provider`, `envelope_id`, `status`, `signers`

#### [NEW] `backend/app/services/signature_service.py`
E-signature abstraction:
- `DocuSignProvider`: DocuSign API client
- `AdobeSignProvider`: Adobe Sign API client
- `request_signature()`: Common interface
- `handle_webhook()`: Process signature completion

#### [NEW] `backend/app/services/notification_service.py`
Notification dispatcher:
- `send_email()`: SMTP email sending
- `send_webhook()`: HTTP webhook POST
- `render_template()`: Jinja2 email templates
- Event handlers: workflow_submitted, workflow_approved, document_expiring

#### [NEW] `backend/app/api/routes/signatures.py`
E-signature endpoints:
- `POST /documents/{id}/request-signature`: Initiate signing
- `POST /webhooks/signature-complete`: Handle provider callbacks
- `GET /documents/{id}/signature-status`: Check status

---

### Phase 4: Security & RBAC

#### [NEW] `backend/app/models/document_permission.py`
Fine-grained permissions:
- `DocumentPermission`: User/group permissions
- Permissions: `read`, `write`, `delete`, `share`, `approve`
- Inheritance from folder structure (future)

#### [MODIFY] `backend/app/api/deps.py`
Add permission checking:
- `check_document_permission()`: Dependency for route protection
- `get_accessible_documents()`: Filter by user permissions

#### [NEW] `backend/app/api/routes/permissions.py`
Permission management:
- `POST /documents/{id}/permissions`: Grant access
- `DELETE /documents/{id}/permissions/{user_id}`: Revoke access
- `GET /documents/{id}/permissions`: List permissions

#### [NEW] `backend/app/utils/audit.py`
Audit logging decorator:
- `@audit_log`: Automatically log actions
- Captures: user, action, document_id, IP, timestamp, changes

---

### Phase 5: Background Tasks

#### [NEW] `backend/app/tasks/__init__.py`
Background task scheduler:
- Use APScheduler for task scheduling
- Tasks: retention policy enforcement, notification dispatch

#### [NEW] `backend/app/tasks/retention.py`
Retention policy automation:
- `evaluate_retention_policies()`: Daily job
- `archive_documents()`: Move to cold storage
- `dispose_documents()`: Secure deletion (GDPR-compliant)

## Verification Plan

### Automated Tests
1. **File Upload Tests**: Multipart upload, file validation, storage
2. **Checkout Tests**: Concurrent checkout attempts, lock expiration
3. **Workflow Tests**: State transitions, approval logic, rejection
4. **E-Signature Tests**: Mock DocuSign webhooks
5. **RBAC Tests**: Permission inheritance, access denial
6. **Retention Tests**: Policy evaluation, archival, disposal

### Manual Verification
1. Upload a document via API
2. Check it out, make changes, check it in (new version created)
3. Submit for approval workflow
4. Approve as different user
5. Request e-signature (if configured)
6. Verify audit log entries
7. Test retention policy (set short duration, wait for archival)

### Integration Testing
- Docker Compose stack with all services
- End-to-end workflow from upload to disposal
- Performance testing with concurrent users
