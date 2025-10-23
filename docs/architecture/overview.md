# Architecture Overview

**CurriculumExtractor - AI-Powered Worksheet Extraction Platform**

## System Architecture

Full-stack application with async task processing for K-12 educational content extraction.

## High-Level Architecture

```
┌──────────────────────┐
│   React Frontend     │ ──HTTP/REST──> ┌────────────────────┐
│   (Vite + TS)        │ <────JSON───── │  FastAPI Backend   │
│                      │                │  (Python 3.10)     │
│  - PDF Viewer        │                │                    │
│  - LaTeX Renderer    │                │  - User Auth (JWT) │
│  - Question Editor   │                │  - File Upload API │
└──────────────────────┘                │  - Task Management │
                                        └────────────────────┘
                                                 │
                         ┌───────────────────────┼────────────────────┐
                         │                       │                    │
                         ▼                       ▼                    ▼
                ┌─────────────────┐    ┌─────────────────┐  ┌──────────────┐
                │   Supabase      │    │  Redis 7        │  │  Celery      │
                │   PostgreSQL 17 │    │  (Message       │  │  Worker      │
                │                 │    │   Broker)       │  │  (4 procs)   │
                │  - Session Mode │    └─────────────────┘  └──────────────┘
                │  - Port 5432    │             │                    │
                │  - ap-south-1   │             └────────────────────┘
                │                 │                      │
                │  Storage        │              Async Task Queue
                │  - Worksheets   │              (OCR, Segmentation,
                │  - Extractions  │               ML Tagging)
                └─────────────────┘
```

## Backend Architecture

### Layered Architecture with Async Processing

```
┌──────────────────────────────────────────────────────┐
│  API Routes (app/api/routes/)                        │ ◄─ HTTP/REST endpoints
│  - users.py, login.py, tasks.py                      │
│  - extractions.py (future), questions.py (future)    │
├──────────────────────────────────────────────────────┤
│  Dependencies (app/api/deps.py)                      │ ◄─ Auth, DB session injection
│  - SessionDep, CurrentUser                           │
├──────────────────────────────────────────────────────┤
│  CRUD (app/crud.py)                                  │ ◄─ Database operations
│  - User management, Question bank operations         │
├──────────────────────────────────────────────────────┤
│  Models (app/models.py)                              │ ◄─ SQLModel definitions
│  - User, Extraction, Question, Ingestion, Tag        │
├──────────────────────────────────────────────────────┤
│  Database (core/db.py)                               │ ◄─ SQLAlchemy engine
│  - Supabase Session Mode (10 base + 20 overflow)     │
└──────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────────┐
                              │                         │
                              ▼                         ▼
                    ┌──────────────────┐      ┌──────────────────┐
                    │  Celery Worker   │      │  Supabase        │
                    │  (app/worker.py) │      │  PostgreSQL 17   │
                    │                  │      │                  │
                    │  Tasks:          │      │  Tables:         │
                    │  - OCR           │      │  - users         │
                    │  - Segmentation  │      │  - extractions   │
                    │  - Tagging       │      │  - questions     │
                    │                  │      │  - tags          │
                    │  Queue: Redis    │      │                  │
                    └──────────────────┘      │  Storage:        │
                                              │  - worksheets/   │
                                              │  - extractions/  │
                                              └──────────────────┘
```

### Key Components

- **models.py**: Data models with SQLModel
  - **User**: Authentication and authorization
  - **Extraction**: PDF upload metadata, processing status
  - **Question**: Extracted questions with curriculum tags
  - **Ingestion**: Batch upload tracking
  - **Tag**: Curriculum taxonomy nodes
  - Pattern: Base → Create → Update → DB Model (table=True) → Public

- **crud.py**: Database operations layer
  - User creation, authentication
  - Extraction lifecycle management
  - Question bank operations
  - Decoupled from API routes

- **api/deps.py**: Dependency injection
  - `SessionDep`: Database session per request (auto-commit/rollback)
  - `CurrentUser`: JWT authentication requirement
  - Reusable across all routes

- **api/routes/**: REST API endpoints
  - `users.py`: User management and auth
  - `login.py`: Authentication (JWT)
  - `tasks.py`: Celery task management
  - `extractions.py` (future): PDF upload and processing
  - `questions.py` (future): Question bank CRUD

- **worker.py**: Celery configuration
  - Redis broker connection
  - Task auto-discovery
  - Time limits, retries, serialization
  - Timezone: Asia/Singapore

- **tasks/**: Async background tasks
  - `tasks/default.py`: Health check, test tasks
  - `tasks/extraction.py`: PDF processing pipeline
  - All tasks logged and tracked

## Frontend Architecture

### Component Structure

```
src/
├── routes/              # File-based routing (TanStack Router)
│   ├── __root.tsx      # Root layout
│   ├── _layout.tsx     # Authenticated layout
│   └── login.tsx       # Public pages
├── components/          # Reusable components
│   ├── Common/         # Shared components
│   └── ui/             # Chakra UI custom components
├── client/             # Auto-generated API client
├── hooks/              # Custom React hooks
└── theme/              # Chakra UI theming
```

### Data Flow

1. **Route Component** initiates data fetch
2. **TanStack Query** manages server state
3. **Generated Client** makes typed API calls
4. **API Response** updates component via Query cache

### Key Patterns

- **File-based routing**: Routes match file structure
- **Server state**: TanStack Query for all API data
- **Generated client**: Type-safe API calls from OpenAPI
- **Compound components**: Chakra UI pattern (e.g., Table.Root, Table.Row)

## Extraction Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  1. Upload PDF                                              │
│     - User uploads via frontend                             │
│     - API stores in Supabase Storage (worksheets bucket)    │
│     - Creates Extraction record (status=DRAFT)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Queue Celery Task                                       │
│     - API queues: process_pdf_task.delay(extraction_id)     │
│     - Task ID returned to frontend                          │
│     - Frontend polls for status                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Celery Worker Processes (Async)                        │
│     ┌─────────────────────────────────────┐               │
│     │  Stage 1: OCR                       │               │
│     │  - PaddleOCR text extraction        │               │
│     │  - Bounding box detection           │               │
│     └─────────────────────────────────────┘               │
│                     │                                       │
│                     ▼                                       │
│     ┌─────────────────────────────────────┐               │
│     │  Stage 2: Segmentation              │               │
│     │  - Identify question boundaries     │               │
│     │  - Detect multi-part questions      │               │
│     │  - Extract images/diagrams          │               │
│     └─────────────────────────────────────┘               │
│                     │                                       │
│                     ▼                                       │
│     ┌─────────────────────────────────────┐               │
│     │  Stage 3: Curriculum Tagging        │               │
│     │  - ML model inference (DeBERTa-v3)  │               │
│     │  - Top-3 tag suggestions            │               │
│     │  - Confidence scores                │               │
│     └─────────────────────────────────────┘               │
│                     │                                       │
│                     ▼                                       │
│     ┌─────────────────────────────────────┐               │
│     │  Stage 4: Store Results             │               │
│     │  - Save questions to database       │               │
│     │  - Update extraction status=DRAFT   │               │
│     └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Human Review                                            │
│     - Frontend loads PDF + extracted questions              │
│     - Side-by-side review interface                         │
│     - User edits tags, content                              │
│     - Approve → status=APPROVED → Question Bank            │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Current Tables

- **user**: User accounts and authentication
  - UUID primary key
  - Email (unique, indexed)
  - Hashed password (bcrypt)
  - Role flags (is_superuser, is_active)
  - Full name (optional)

### Future Tables (CurriculumExtractor)

- **extraction**: PDF extraction metadata
  - UUID primary key
  - Foreign key to user
  - Filename, PDF URL (Supabase Storage)
  - Status (DRAFT/PROCESSING/APPROVED/REJECTED)
  - Celery task_id
  - Timestamps (created_at, updated_at)

- **question**: Extracted questions
  - UUID primary key
  - Foreign key to extraction
  - Question text, answer, explanation
  - Question type (MCQ, short answer, etc.)
  - Subject, grade level
  - Curriculum tags (JSONB array)
  - LaTeX content (if math question)
  - Bounding boxes for PDF regions

- **ingestion**: Batch upload tracking
  - UUID primary key
  - Foreign key to user
  - Batch metadata
  - Multiple extractions per ingestion

- **tag**: Curriculum taxonomy
  - UUID primary key
  - Subject-specific hierarchy
  - Code, name, description
  - Version (curriculum year)

### Migration Strategy

- **Alembic** for local development (version controlled)
- **Supabase MCP** for quick prototyping/hotfixes
- Auto-generate from model changes
- Review all migrations before applying
- Check for security advisories with `mcp_supabase_get_advisors()`
- Never use `SQLModel.metadata.create_all()` in production

## Technology Stack

### Backend
- **FastAPI** 0.115+ - Python async web framework
- **SQLModel** 0.0.24 - ORM with Pydantic validation
- **PostgreSQL** 17 via **Supabase** - Managed database
- **Celery** 5.5 + **Redis** 7 - Async task queue
- **psycopg3** - PostgreSQL driver
- **Alembic** - Database migrations
- **pyjwt** - JWT authentication

### Frontend
- **React** 19 + **TypeScript** 5.2
- **Vite** 7 - Build tool with HMR
- **TanStack Router** - File-based routing
- **TanStack Query** - Server state management
- **Chakra UI** 3 - Component library
- **react-pdf** 9.x (future) - PDF rendering
- **KaTeX** (future) - LaTeX math rendering

### Infrastructure
- **Docker Compose** - Development orchestration
- **Supabase** - Managed Postgres + Storage + Auth
- **Redis** - Message broker (Celery)
- **Traefik** - Reverse proxy (production)
- **GitHub Actions** - CI/CD pipeline

### ML Pipeline (Phase 2)
- **PaddleOCR** / **Mistral OCR** - Text extraction
- **docTR** / **LayoutLMv3** - Layout analysis
- **DeBERTa-v3** - Curriculum tagging (fine-tuned)

---

## Data Flow

### PDF Upload Flow

```
1. Frontend: Upload PDF
   │
   ├─> POST /api/v1/extractions/ (with file)
   │
2. Backend API: Store & Queue
   │
   ├─> Save to Supabase Storage (worksheets bucket)
   ├─> Create Extraction record (status=DRAFT)
   ├─> Queue Celery task: process_pdf_task.delay(extraction_id)
   └─> Return task_id to frontend
   │
3. Celery Worker: Process Async
   │
   ├─> Fetch PDF from Storage
   ├─> Run OCR (PaddleOCR)
   ├─> Segment questions (docTR)
   ├─> Apply ML tagging (DeBERTa-v3)
   ├─> Store questions in database
   └─> Update extraction status=DRAFT
   │
4. Frontend: Review Interface
   │
   ├─> Poll GET /api/v1/tasks/status/{task_id}
   ├─> Load PDF + questions side-by-side
   ├─> User reviews and edits
   ├─> POST /api/v1/questions/{id}/approve
   └─> Questions moved to question bank (status=APPROVED)
```

---

## Security Architecture

### Authentication & Authorization
- **JWT tokens**: 8-day expiry, signed with SECRET_KEY
- **Password hashing**: bcrypt via passlib
- **Role-based access**: is_superuser, is_active flags
- **Dependency injection**: `CurrentUser` for protected routes
- **Token refresh**: Via `/api/v1/login/access-token`

### Data Security
- **Supabase Row-Level Security (RLS)**: Future multi-tenancy
- **Input validation**: Pydantic models (automatic)
- **SQL injection**: Protected via SQLModel parameterization
- **CORS**: Configurable allowed origins
- **File uploads**: Size limits, type validation
- **Secrets**: Never in code (environment variables only)

### Infrastructure Security
- **Redis**: Password authentication enabled
- **Supabase Service Key**: Backend only (never frontend)
- **Signed URLs**: 7-day expiry for PDF access
- **HTTPS**: Traefik with Let's Encrypt (production)

---

## Connection Pooling

### Supabase Session Mode

**Configuration** (backend/app/core/db.py):
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # 10 permanent connections
    max_overflow=20,     # Up to 30 total during spikes
    pool_pre_ping=True,  # Verify connections alive
    pool_recycle=3600,   # Recycle after 1 hour
)
```

**Why Session Mode**:
- ✅ Best for persistent Docker containers
- ✅ Supports prepared statements (faster queries)
- ✅ Works with SQLAlchemy connection pooling
- ✅ IPv4 + IPv6 compatible
- ❌ Not for serverless (would use Transaction Mode)

**Connection String**:
```
postgresql+psycopg://postgres.wijzypbstiigssjuiuvh:***@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

---

## Async Task Processing

### Celery Architecture

**Worker Configuration** (backend/app/worker.py):
```python
celery_app = Celery(
    "curriculum_extractor",
    broker=REDIS_URL,
    backend=REDIS_URL
)

Config:
- Task time limit: 600s (10 minutes)
- Concurrency: 4 worker processes
- Timezone: Asia/Singapore
- Serializer: JSON
- Auto-discovery: app.tasks
```

**Task Structure**:
```
app/tasks/
├── __init__.py          # Task imports
├── default.py           # health_check, test_task
└── extraction.py        # process_pdf_task (pipeline stages)
```

**Task Execution**:
1. API queues task: `task = process_pdf_task.delay(extraction_id)`
2. Redis stores task in queue
3. Celery worker picks up task
4. Worker executes stages (OCR → Segment → Tag → Store)
5. Result stored in Redis backend
6. API retrieves result: `GET /api/v1/tasks/status/{task_id}`

---

## Development vs Production

### Development (Current)
- ✅ Docker Compose with hot reload (`docker compose watch`)
- ✅ Supabase free tier (managed PostgreSQL)
- ✅ Redis in Docker (ephemeral)
- ✅ Celery worker (4 processes)
- ✅ Debug tooling enabled
- ✅ Permissive CORS (localhost)
- ✅ MailCatcher for email testing

### Production (Future)
- Supabase paid tier (dedicated resources)
- Redis with persistence (RDB + AOF)
- Celery workers (horizontal scaling)
- Sentry error tracking
- Strict CORS (domain whitelist)
- Traefik reverse proxy (HTTPS)
- Real SMTP server (AWS SES)

---

## Supabase Integration

### Database
- **PostgreSQL** 17.6.1
- **Region**: ap-south-1 (Mumbai, India)
- **Connection**: Session Mode pooler (port 5432)
- **Project ID**: wijzypbstiigssjuiuvh
- **Pooling**: Supavisor (built-in)

### Storage
- **Buckets**: `worksheets`, `extractions`
- **Access**: Signed URLs (7-day expiry)
- **SDK**: `@supabase/supabase-js` (frontend), `supabase-py` (backend)

### Management
- **Dashboard**: https://app.supabase.com/project/wijzypbstiigssjuiuvh
- **MCP Server**: Direct access via Cursor (database operations)
- **CLI**: `supabase` (future - for migrations)

---

## Scalability Considerations

### Current Capacity (Free Tier)
- **Database**: 500 MB storage, 2 GB bandwidth/month
- **Storage**: 1 GB files
- **Concurrent Connections**: 60 max (Supavisor handles pooling)
- **Celery**: 4 processes (can scale horizontally)

### Scaling Strategy
- **Database**: Upgrade Supabase tier, add read replicas
- **Celery**: Add more worker containers (`docker compose scale celery-worker=8`)
- **Redis**: Upgrade to managed Redis (Upstash, Redis Cloud)
- **Storage**: Upgrade Supabase storage tier

---

For architecture decisions, see [decisions/](./decisions/) (ADRs - to be created)
