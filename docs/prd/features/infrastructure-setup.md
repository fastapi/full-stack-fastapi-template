# PRD: Infrastructure Setup for Question Extraction Pipeline

**Version**: 1.2
**Component**: Backend Infrastructure
**Status**: Draft
**Last Updated**: 2025-10-22
**Related**: [Project Overview](../overview.md), [Implementation Plan](../implementation-plan-math.md), [Math Extraction Feature](./math-worksheet-question-extractor.md)

---

## 1. Overview

### What & Why

Configure the foundational infrastructure for the CurriculumExtractor backend to support the AI-powered question extraction pipeline. This **Epic 1** focuses on core backend services: migrating from local PostgreSQL to Supabase (managed Postgres + Object Storage) and adding Redis + Celery for background job processing.

**Value**: Enables async extraction pipeline and cloud-based storage for scalability. This is the foundational epic that unblocks all subsequent development work.

### Scope

**In scope (Epic 1)**:
- **Database Migration**: Switch from local Postgres to Supabase managed Postgres
- **Object Storage**: Configure Supabase Storage buckets (`worksheets`, `extractions`)
- **Background Jobs**: Add Redis + Celery worker for async extraction pipeline
- **Environment Configuration**: Update .env with Supabase credentials and Redis connection
- **Docker Compose**: Add Redis service, Celery worker service with health checks
- **Database Migrations**: Ensure Alembic works seamlessly with Supabase
- **Dependencies**: Add Python packages (celery, redis, supabase-py)
- **CI/CD Workflows**: Update GitHub Actions workflows for new infrastructure (test-docker-compose, test-backend, generate-client)

**Out of scope (handled in later epics)**:
- **Epic 2**: Document upload API and file validation
- **Epic 3**: PDF viewer integration (react-pdf, react-pdf-highlighter)
- **Epic 4+**: ML model deployment, OCR pipeline
- Multi-region Supabase setup
- CDN configuration for static assets
- Kubernetes/production orchestration

### Living Document

This PRD evolves during implementation:
- Adjustments based on Supabase API limitations discovered during integration
- Redis memory tuning based on actual job queue sizes
- PDF rendering performance optimizations

### Non-Functional Requirements

- **Performance**:
  - PDF rendering: <1s for first page, <500ms for subsequent pages
  - Redis connection pool: 10-50 connections
  - Celery worker concurrency: 4 workers per service
  - Supabase Storage upload: <5s for 10MB PDF
- **Security**:
  - Supabase RLS (Row-Level Security) enabled for multi-tenancy
  - Supabase Storage presigned URLs with 7-day expiry for drafts
  - Redis password authentication enabled
  - No hardcoded credentials (use environment variables)
- **Reliability**:
  - Celery task retry: 3 attempts with exponential backoff
  - Redis persistence: RDB + AOF for durability
  - Graceful worker shutdown on SIGTERM
- **Scalability**:
  - Horizontal Celery worker scaling via Docker Compose replicas
  - Supabase connection pooling (pgBouncer built-in)
  - Redis max memory: 256MB (LRU eviction policy)

---

## 2. User Stories

### Primary Story
**As a** Backend Developer
**I want** the infrastructure configured with Supabase, Redis, and Celery
**So that** I can implement async extraction pipeline and cloud storage for question extraction

### Supporting Stories

**As a** DevOps Engineer
**I want** all services defined in Docker Compose with health checks
**So that** the development environment is reproducible and services restart on failure

**As a** Backend Developer
**I want** Supabase Storage buckets configured with RLS policies
**So that** uploaded files are securely stored and accessible only to authorized users

**As a** Backend Developer
**I want** Celery task monitoring via Flower (optional)
**So that** I can debug failed extraction jobs

**As a** QA Engineer
**I want** database migrations to work seamlessly with Supabase
**So that** schema changes are versioned and applied consistently

**As a** CI/CD Engineer
**I want** GitHub Actions workflows updated to validate the new infrastructure
**So that** Redis + Celery + Supabase integration is tested automatically on every commit

---

## 3. Acceptance Criteria (Gherkin)

### Scenario: Supabase Database Connection
```gherkin
Given the .env file contains valid Supabase credentials (SUPABASE_URL, SUPABASE_KEY, DATABASE_URL)
When the backend service starts
Then the application connects to Supabase Postgres successfully
And Alembic migrations run without errors
And the backend health check endpoint returns 200 OK
```

### Scenario: Supabase Storage Upload
```gherkin
Given the backend is connected to Supabase
When a user uploads a 5MB PDF via POST /api/ingestions
Then the PDF is uploaded to Supabase Storage bucket "worksheets"
And a presigned URL with 7-day expiry is generated
And the URL is stored in the extractions table
And the PDF is accessible via the presigned URL
```

### Scenario: Redis Connection
```gherkin
Given Docker Compose includes a Redis service on port 6379
And the .env file contains REDIS_URL=redis://redis:6379/0
When the backend service starts
Then the backend connects to Redis successfully
And Redis ping returns PONG
```

### Scenario: Celery Worker Startup
```gherkin
Given Docker Compose includes a Celery worker service
And the worker is configured with 4 concurrent processes
When docker compose up is run
Then the Celery worker starts without errors
And the worker registers tasks (extract_worksheet_pipeline, etc.)
And the worker is ready to consume tasks from the Redis queue
```

### Scenario: Background Job Execution
```gherkin
Given a Celery worker is running
When a task is queued: extract_worksheet_pipeline.delay(extraction_id="abc123")
Then the task is picked up by a worker within 1 second
And the task executes asynchronously
And the task result is stored in Redis
And the extraction status updates to "PROCESSING" → "DRAFT" or "FAILED"
```

### Scenario: All Services Start Successfully
```gherkin
Given all environment variables are set in .env
When I run docker compose up
Then all services start without errors
And health checks pass for backend, Redis, Celery worker
And backend logs show "Connected to Supabase Postgres"
And Celery worker logs show "ready" and registered tasks
```

### Scenario: Environment Variable Validation
```gherkin
Given the .env file is missing SUPABASE_URL
When docker compose up is run
Then the backend service fails with error "SUPABASE_URL not set"
And the error message is visible in docker logs
```

### Scenario: CI Workflows Validate Infrastructure
```gherkin
Given GitHub Actions workflows are updated with Redis and Celery
And workflows include test-docker-compose, test-backend, and generate-client
When a pull request is opened with infrastructure changes
Then the test-docker-compose workflow starts Redis and Celery worker services
And the workflow validates Redis is accessible via redis-cli ping
And the workflow validates Celery worker registers tasks
And all CI checks pass successfully
```

---

## 4. Functional Requirements

### Core Behavior

**Supabase Integration**:
1. Replace `POSTGRES_SERVER=localhost` with Supabase connection string
2. Configure Supabase Storage with buckets:
   - `worksheets`: Uploaded PDF/DOCX files (private, RLS enabled)
   - `extractions`: Extracted images/page crops (private, RLS enabled)
3. Use `supabase-py` client for Python SDK, `@supabase/supabase-js` for frontend
4. Enable Row-Level Security (RLS) policies for multi-user access

**Redis + Celery Setup**:
1. Add Redis 7 service to docker-compose.yml (port 6379, password-protected)
2. Add Celery worker service (depends on Redis + backend)
3. Configure Celery to use Redis as broker and result backend
4. Define task routing: `extraction_tasks` queue for OCR/segmentation/tagging
5. Set task timeouts: 120s for OCR, 180s for segmentation, 60s for tagging

**React PDF Integration**:
1. Install `react-pdf@9.x` and `react-pdf-highlighter@6.x`
2. Configure PDF.js worker from CDN or local bundle
3. Implement lazy page loading with virtualization
4. Render annotations (bounding boxes) as canvas overlays

**Docker Compose Configuration**:
1. Add `redis` service with persistent volume
2. Add `celery-worker` service with auto-restart
3. Add health checks for all services
4. Configure environment variable passing

### States & Transitions

| Service | Health Check | Retry Policy |
|---------|--------------|--------------|
| `backend` | `GET /api/v1/utils/health-check/` | 3 retries, 10s interval |
| `redis` | `redis-cli ping` | 3 retries, 5s interval |
| `celery-worker` | `celery -A app.worker inspect ping` | Restart on exit |
| `db` (Supabase) | Connection test via `psycopg` | 5 retries, 10s interval |

### Business Rules

1. **Supabase Storage Buckets**: Separate buckets for originals (`worksheets`) and processed assets (`extractions`)
2. **Presigned URLs**: All uploaded files use presigned URLs with 7-day expiry for drafts, permanent for approved
3. **Celery Task Retries**: Auto-retry on transient failures (network errors, rate limits) with exponential backoff
4. **Redis Persistence**: Enable both RDB (snapshot) and AOF (append-only file) for data durability
5. **PDF Worker Configuration**: Use PDF.js worker to offload rendering to Web Worker (non-blocking UI)
6. **Environment Validation**: Backend fails fast on startup if required env vars missing

### Permissions

- **Supabase Storage**:
  - Public read: Disabled (use presigned URLs)
  - Authenticated users: Upload to `worksheets`, read own files
  - Admins: Read all files, delete
- **Redis**:
  - Password authentication required
  - No external access (internal Docker network only)
- **Celery Flower** (if enabled):
  - Basic auth protected
  - Admin role required

---

## 5. Technical Specification

### Architecture Pattern

**Cloud-Native Infrastructure with Job Queue**:
- **Database**: Supabase managed Postgres (replaces local Postgres)
- **Object Storage**: Supabase Storage (S3-compatible API)
- **Message Broker**: Redis 7 (in-memory data structure store)
- **Task Queue**: Celery 5.3+ (distributed task queue)
- **PDF Rendering**: react-pdf (client-side rendering via PDF.js)

**Rationale**:
- Supabase provides managed Postgres + Storage + Auth in one platform, reducing DevOps overhead
- Redis + Celery is industry-standard for Python async tasks, battle-tested at scale
- react-pdf uses PDF.js (Mozilla) for robust, cross-browser PDF rendering

### Data Models

**Supabase Storage Metadata**:
```typescript
interface StorageObject {
  id: string;
  name: string;
  bucket_id: string;  // "worksheets" or "extractions"
  owner: string;      // User UUID
  created_at: string;
  updated_at: string;
  metadata: {
    size: number;
    mimetype: string;
    cacheControl: string;
  };
}
```

**Celery Task** (`backend/app/tasks/extraction.py`):
```python
from celery import Task

class ExtractionTask(Task):
    name = "tasks.extract_worksheet_pipeline"
    max_retries = 3
    default_retry_delay = 60  # seconds

    def run(self, extraction_id: str) -> dict:
        # Stage 1: OCR
        # Stage 2: Segmentation
        # Stage 3: Tagging
        # Stage 4: Save draft
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Update extraction status to FAILED
        pass
```

### Environment Variables

**New Variables**:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key  # Backend only, server-side
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# Redis
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=changethis

# Celery
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json

# Supabase Storage
SUPABASE_STORAGE_BUCKET_WORKSHEETS=worksheets
SUPABASE_STORAGE_BUCKET_EXTRACTIONS=extractions
```

**Removed/Replaced**:
- `POSTGRES_SERVER=localhost` → Use `DATABASE_URL` from Supabase
- Local database volume → Supabase managed (no local volume needed)

### Docker Compose Updates

**Add Redis Service**:
```yaml
redis:
  image: redis:7-alpine
  restart: always
  command: redis-server --requirepass ${REDIS_PASSWORD}
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
    interval: 10s
    timeout: 3s
    retries: 5
```

**Add Celery Worker Service**:
```yaml
celery-worker:
  build:
    context: ./backend
  restart: always
  command: celery -A app.worker worker --loglevel=info --concurrency=4
  depends_on:
    redis:
      condition: service_healthy
    backend:
      condition: service_healthy
  env_file:
    - .env
  environment:
    - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    - DATABASE_URL=${DATABASE_URL}
    - SUPABASE_URL=${SUPABASE_URL}
    - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
```

**Add Volumes**:
```yaml
volumes:
  redis-data:
```

**Remove Local DB Service** (optional, if fully migrating to Supabase):
- Keep local `db` service for development/testing if needed
- Or remove entirely and point to Supabase for all environments

---

## 6. Integration Points

### Dependencies

**Backend Python Packages** (add to `pyproject.toml`):
```toml
[project.dependencies]
# Existing: fastapi, sqlmodel, pydantic, alembic, psycopg, ...

# New for Supabase + Celery + Redis:
"supabase<3.0.0,>=2.0.0"              # Supabase Python client
"celery[redis]<6.0.0,>=5.3.4"         # Celery with Redis support
"redis<5.0.0,>=4.6.0"                 # Redis client
"boto3<2.0.0,>=1.28.0"                # S3-compatible storage (Supabase Storage)
"flower<3.0.0,>=2.0.0"                # Celery monitoring (optional)
```

**Frontend Packages** (deferred to Epic 3):
- react-pdf and react-pdf-highlighter will be added in Epic 3 (PDF Viewer Integration)
- @supabase/supabase-js may be added later if frontend needs direct Supabase access

**External Services**:
- **Supabase**: Managed Postgres + Storage + Auth
- **Redis Cloud** (optional for production): Or self-hosted Redis in Docker

### Events/Webhooks

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| `extraction.queued` | POST /api/ingestions | `{extraction_id, status: "UPLOADED"}` | Celery worker picks up task |
| `extraction.completed` | Celery task success | `{extraction_id, status: "DRAFT", question_count}` | Frontend WebSocket notification (future) |
| `extraction.failed` | Celery task failure | `{extraction_id, status: "FAILED", error}` | Admin alert via Sentry |

---

## 7. UX Specifications

**N/A for Epic 1** - This epic is backend infrastructure only. UX specifications for the PDF viewer will be defined in Epic 3 (PDF Viewer Integration) and Epic 9 (PDF Viewer with Annotations).

---

## 8. Implementation Guidance

### Step-by-Step Implementation

**Phase 1: Supabase Database Migration (Day 1)**

1. **Create Supabase Project**:
   - Sign up at supabase.com, create project
   - Copy `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY` from project settings

2. **Update .env**:
   ```env
   DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
   SUPABASE_URL=https://[project].supabase.co
   SUPABASE_KEY=[anon-key]
   SUPABASE_SERVICE_KEY=[service-role-key]
   ```

3. **Test Connection**:
   ```bash
   cd backend
   python -c "from app.core.db import engine; engine.connect(); print('✅ Connected to Supabase')"
   ```

4. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

**Phase 2: Supabase Storage Setup (Day 1)**

5. **Create Buckets** (via Supabase dashboard or SQL):
   ```sql
   -- In Supabase SQL Editor
   INSERT INTO storage.buckets (id, name, public) VALUES
   ('worksheets', 'worksheets', false),
   ('extractions', 'extractions', false);
   ```

6. **Configure RLS Policies** (Supabase dashboard → Storage → Policies):
   ```sql
   -- Allow authenticated users to upload to worksheets
   CREATE POLICY "Users can upload worksheets" ON storage.objects FOR INSERT
   TO authenticated
   WITH CHECK (bucket_id = 'worksheets' AND auth.uid() = owner);

   -- Allow users to read own worksheets
   CREATE POLICY "Users can read own worksheets" ON storage.objects FOR SELECT
   TO authenticated
   USING (bucket_id = 'worksheets' AND auth.uid() = owner);
   ```

7. **Test Upload** (`backend/app/utils.py`):
   ```python
   from supabase import create_client

   supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

   with open("test.pdf", "rb") as f:
       response = supabase.storage.from_("worksheets").upload(
           path="test/test.pdf",
           file=f,
           file_options={"content-type": "application/pdf"}
       )
   print(f"Uploaded: {response}")
   ```

**Phase 3: Redis + Celery (Days 2-3)**

8. **Add Redis to docker-compose.yml** (see Section 5)

9. **Create Celery Worker** (`backend/app/worker.py`):
   ```python
   from celery import Celery
   from app.core.config import settings

   celery_app = Celery(
       "curriculum_extractor",
       broker=settings.CELERY_BROKER_URL,
       backend=settings.CELERY_RESULT_BACKEND,
   )

   celery_app.conf.update(
       task_serializer="json",
       result_serializer="json",
       accept_content=["json"],
       timezone="Asia/Singapore",
       enable_utc=True,
   )

   # Import tasks
   from app.tasks import extraction  # noqa
   ```

10. **Create Sample Task** (`backend/app/tasks/extraction.py`):
    ```python
    from app.worker import celery_app

    @celery_app.task(bind=True, name="tasks.extract_worksheet_pipeline")
    def extract_worksheet_pipeline(self, extraction_id: str):
        # Mock implementation
        print(f"Processing extraction {extraction_id}")
        return {"status": "success", "extraction_id": extraction_id}
    ```

11. **Test Celery**:
    ```bash
    docker compose up redis celery-worker
    # In another terminal:
    docker compose exec backend python -c "
    from app.tasks.extraction import extract_worksheet_pipeline
    result = extract_worksheet_pipeline.delay('test-123')
    print(f'Task ID: {result.id}')
    print(f'Result: {result.get(timeout=10)}')
    "
    ```

**Phase 4: CI/CD Workflow Updates (Day 4)**

12. **Update test-docker-compose.yml**:
    ```yaml
    # Add Redis and Celery worker to service startup
    - run: docker compose up -d --wait backend redis celery-worker frontend

    # Add Redis health check
    - name: Test Redis is up
      run: docker compose exec redis redis-cli --raw incr ping

    # Add Celery worker validation
    - name: Test Celery worker is registered
      run: docker compose logs celery-worker | grep -q "celery@"
    ```

13. **Update test-backend.yml**:
    ```yaml
    # Add Redis service for tests
    - run: docker compose up -d redis mailcatcher  # Remove 'db', add 'redis'

    # Add environment variables for tests
    - name: Run tests
      env:
        DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}  # Or postgresql://localhost
        REDIS_URL: redis://localhost:6379/0
        SUPABASE_URL: ${{ secrets.TEST_SUPABASE_URL }}
        SUPABASE_KEY: ${{ secrets.TEST_SUPABASE_KEY }}
    ```

14. **Update generate-client.yml**:
    ```yaml
    # Add Supabase/Redis env vars for client generation
    - run: uv run bash scripts/generate-client.sh
      env:
        SECRET_KEY: just-for-generating-client
        DATABASE_URL: postgresql://localhost:5432/test
        SUPABASE_URL: https://dummy.supabase.co
        SUPABASE_KEY: dummy-key
        SUPABASE_SERVICE_KEY: dummy-service-key
        REDIS_URL: redis://localhost:6379/0
        CELERY_BROKER_URL: redis://localhost:6379/0
        CELERY_RESULT_BACKEND: redis://localhost:6379/0
    ```

15. **Verify CI Workflows**:
    ```bash
    # Push branch and open PR to trigger workflows
    git checkout -b test/ci-infrastructure-updates
    git add .github/workflows/
    git commit -m "Update CI workflows for Redis + Celery + Supabase"
    git push origin test/ci-infrastructure-updates

    # Monitor GitHub Actions and verify:
    # - test-docker-compose passes with all services
    # - test-backend passes with Redis available
    # - generate-client passes with new env vars
    ```

**Phase 5: Integration Testing & Documentation (Day 5)**

16. **Integration Test - Full Service Stack**:
    ```bash
    # Test all services start correctly
    docker compose up -d
    docker compose ps  # All services should be "healthy"

    # Test backend connects to Supabase
    docker compose exec backend python -c "
    from app.core.db import engine
    with engine.connect() as conn:
        print('✅ Supabase Postgres connected')
    "

    # Test Celery task execution
    docker compose exec backend python -c "
    from app.tasks.extraction import extract_worksheet_pipeline
    result = extract_worksheet_pipeline.delay('test-123')
    print(f'✅ Task queued: {result.id}')
    print(f'✅ Task result: {result.get(timeout=10)}')
    "
    ```

17. **Update Documentation**:
    - Update `CLAUDE.md` with Supabase and Celery configuration
    - Update `README.md` with new environment variables
    - Update `deployment.md` with Supabase setup instructions
    - Document troubleshooting steps for common issues
    - Document CI workflow updates in development guide

### Security Considerations

- **Supabase Service Key**: Never expose in frontend; backend only
- **Redis Password**: Use strong password, change default `changethis`
- **Presigned URLs**: Set appropriate expiry (7 days for drafts, permanent for approved)
- **RLS Policies**: Test that users can only access own files
- **Environment Variables**: Never commit .env to git (ensure in .gitignore)

### Performance Optimization

- **PDF Lazy Loading**: Only render visible pages (virtualization with `react-window`)
- **Celery Prefetch**: Limit task prefetching to prevent memory bloat (`worker_prefetch_multiplier=1`)
- **Redis Max Memory**: Set `maxmemory 256mb` and `maxmemory-policy allkeys-lru`
- **Supabase Connection Pooling**: Use pgBouncer (built-in, no config needed)

### Observability

- **Logs**:
  - Celery worker logs: `docker compose logs -f celery-worker`
  - Redis logs: `docker compose logs -f redis`
  - Backend logs: `docker compose logs -f backend`
- **Metrics**:
  - Celery task duration, success/failure rate (via Flower dashboard or Datadog)
  - Redis memory usage, eviction rate
  - Supabase Storage bandwidth (via Supabase dashboard)
- **Alerts**:
  - Celery worker down (no heartbeat for 60s)
  - Redis out of memory
  - Supabase Storage quota exceeded

---

## 9. Testing Strategy

### Unit Tests

- [ ] Supabase client initializes with correct credentials
- [ ] Supabase Storage upload returns presigned URL with 7-day expiry
- [ ] Celery task serialization/deserialization works correctly
- [ ] Redis connection pool handles concurrent connections
- [ ] PDF.js worker loads correctly in React

### Integration Tests

- [ ] Upload PDF → Supabase Storage → Presigned URL accessible
- [ ] Queue Celery task → Worker processes → Result stored in Redis
- [ ] Backend connects to Supabase Postgres → Alembic migrations run
- [ ] Frontend fetches PDF from presigned URL → react-pdf renders

### E2E Tests (Manual)

- [ ] Full workflow: Upload PDF → Queue extraction → Worker processes → Frontend displays PDF with annotations
- [ ] Docker Compose startup: All services (backend, redis, celery-worker) start with health checks passing
- [ ] Environment variable validation: Missing env var causes graceful failure with clear error message

### Manual Verification

- [ ] Supabase dashboard shows uploaded files in `worksheets` bucket
- [ ] Redis CLI shows queued tasks: `redis-cli LLEN celery`
- [ ] Celery Flower dashboard (if enabled) shows active workers and task history
- [ ] PDF renders in browser with annotations visible

---

## 10. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Supabase free tier limits exceeded** | High (service disruption) | Medium | Monitor storage/bandwidth usage; upgrade to paid tier if needed |
| **Celery worker memory leak** | High (worker crash) | Medium | Set task time limits, monitor memory, restart workers daily |
| **Redis out of memory** | High (task queue failure) | Medium | Set maxmemory policy to LRU eviction; monitor queue depth |
| **PDF rendering performance on large files** | Medium (slow UI) | High | Implement lazy loading, virtualization; compress PDFs on upload |
| **Supabase connection limits** | Medium (connection errors) | Low | Use connection pooling (pgBouncer); limit max connections in app |
| **Celery task timeout** | Low (extraction failure) | Medium | Set appropriate timeouts per task type; implement retry logic |

---

## 11. Rollout Plan

### Phase 1: Infrastructure Setup (Days 1-2)
- Supabase project creation and database migration
- Supabase Storage bucket creation and RLS policies
- Docker Compose updated with Redis service
- **Deliverable**: Supabase connected, storage buckets ready

### Phase 2: Background Jobs (Day 3)
- Celery worker service added to Docker Compose
- Sample extraction task implemented and tested
- Task retry and error handling configured
- **Deliverable**: Celery worker processing mock tasks

### Phase 3: CI/CD Updates (Day 4)
- GitHub Actions workflows updated for new infrastructure
- test-docker-compose.yml includes Redis and Celery checks
- test-backend.yml configured with Redis and Supabase
- generate-client.yml includes all required env vars
- **Deliverable**: All CI workflows passing with new infrastructure

### Phase 4: Integration & Testing (Day 5)
- End-to-end testing of full service stack
- Environment variable validation
- Documentation updates (CLAUDE.md, deployment.md, CI workflows)
- **Deliverable**: All services healthy, CI passing, documentation complete

### Success Metrics (Epic 1)

- **Infrastructure Health**: All services start with health checks passing (100% success rate)
- **Celery Throughput**: Process ≥10 mock extraction tasks/minute
- **Storage Reliability**: 99.9% upload success rate to Supabase Storage (tested with sample files)
- **Zero Silent Failures**: All queued tasks either succeed or fail with error logged
- **CI/CD Validation**: All GitHub Actions workflows pass on PRs (test-docker-compose, test-backend, generate-client)
- **Documentation**: Setup instructions allow new developer to run `docker compose up` successfully in <15 minutes

---

## 12. References

### Codebase References

- **Docker Compose Pattern**: `docker-compose.yml` (existing services: db, backend, frontend)
- **Environment Variables**: `.env` (existing: POSTGRES_*, SECRET_KEY)
- **Backend Entry Point**: `backend/app/main.py` (FastAPI app initialization)
- **Frontend Entry Point**: `frontend/src/main.tsx` (React app initialization)
- **CI Workflows**: `.github/workflows/test-docker-compose.yml`, `.github/workflows/test-backend.yml`, `.github/workflows/generate-client.yml`

### External Documentation

- **Supabase Storage**: https://supabase.com/docs/guides/storage
- **Supabase Python Client**: https://supabase.com/docs/reference/python/introduction
- **Celery Documentation**: https://docs.celeryproject.org/en/stable/
- **Redis Configuration**: https://redis.io/docs/latest/operate/oss_and_stack/management/config/
- **react-pdf**: https://github.com/wojtekmaj/react-pdf
- **react-pdf-highlighter**: https://github.com/agentcooper/react-pdf-highlighter

### Research Sources

- **Celery Best Practices** (2024): Task routing, retry strategies, monitoring
- **Supabase Security**: RLS policies for multi-tenancy
- **PDF.js Performance**: Lazy loading, virtualization patterns

---

## Quality Checklist ✅

- [x] Self-contained with full context (current infrastructure + new requirements)
- [x] INVEST user stories (Backend Dev, DevOps, Frontend Dev, QA)
- [x] Complete Gherkin ACs (Supabase connection, Redis, Celery, PDF rendering)
- [x] Step-by-step implementation guidance (5 phases over 6 days)
- [x] Environment variables documented with examples
- [x] Docker Compose configurations provided
- [x] Security addressed (RLS, presigned URLs, Redis password)
- [x] Performance specified (PDF <1s, task throughput ≥10/min)
- [x] Testing strategy outlined (unit, integration, E2E manual)
- [x] Risks & Mitigation table (6 key risks)
- [x] References populated (codebase patterns, external docs)
- [x] Quantifiable requirements (no vague terms)

---

**Next Steps**:
1. Review PRD with DevOps and Backend teams
2. Set up Supabase project and obtain credentials
3. Begin Phase 1 implementation (Database migration)
4. Test each phase incrementally before proceeding
5. Upon completion, proceed to Epic 2 (Document Upload & Storage)

---

## Change Log

### [2025-10-22] 1.3
- Status: In Progress
- Changes:
  - **Supabase migration completed**: All 4 database migrations successfully applied to Supabase
  - **Config.py updated**: Added automatic conversion of postgresql:// to postgresql+psycopg:// for SQLAlchemy compatibility
  - **Docker Compose updated**: Made local database optional, added Supabase environment variables
  - **Retry logic implemented**: Database connection with 5 retries and 10s intervals for resilience
  - **Environment example updated**: Added clear Supabase connection instructions with URL encoding guide

### [2025-10-22] 1.2
- Status: Draft
- Changes:
  - **Added CI/CD scope**: GitHub Actions workflows now in scope (test-docker-compose, test-backend, generate-client)
  - **New user story**: Added CI/CD Engineer story for workflow validation
  - **New acceptance criteria**: Added scenario for CI workflows validating infrastructure
  - **Implementation guidance**: Added Phase 4 for updating GitHub workflows with specific instructions
  - **Rollout plan updated**: Reorganized phases to include CI/CD updates on Day 4
  - **Success metrics**: Added CI/CD validation metric (all workflows must pass on PRs)
  - **Codebase references**: Added GitHub workflows to references section

### [2025-10-22] 1.1
- Status: Draft
- Changes:
  - **Scope narrowed to Epic 1 only**: Removed react-pdf and frontend PDF integration (moved to Epic 3)
  - **Duration adjusted**: 5 days (was 6 days) to match Epic 1 timeline (3-5 days)
  - **Focus on backend infrastructure**: Supabase, Redis, Celery only
  - **Updated user stories**: Removed Frontend Developer story about PDF viewer
  - **Updated acceptance criteria**: Removed PDF rendering scenarios
  - **Updated dependencies**: Removed frontend packages (react-pdf, react-pdf-highlighter)
  - **Updated implementation phases**: Removed Phase 4 (React PDF Integration)
  - **Clarified scope**: Added explicit references to Epic 1 from implementation-plan-math.md
  - **Success metrics refined**: Focused on infrastructure health, not PDF rendering
