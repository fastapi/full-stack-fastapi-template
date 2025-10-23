# CurriculumExtractor - Template Cleanup & Setup Plan

**Generated**: 2025-10-23
**Project**: CurriculumExtractor (K-12 Singapore Worksheet Extraction Platform)
**Based on**: Full Stack FastAPI Template

---

## 1. Development Environment Setup Checklist

### Prerequisites (Install First)

- [ ] **Docker Desktop** - Latest version with Docker Compose V2
  ```bash
  docker --version  # Should be 20.10+
  docker compose version  # Should be v2.0+
  ```

- [ ] **Node.js via fnm/nvm** - For frontend development
  ```bash
  fnm install  # Or: nvm install
  fnm use      # Or: nvm use
  node --version  # Should match .nvmrc (likely v20+)
  ```

- [ ] **Python 3.10+ with uv** - For backend development
  ```bash
  # Install uv: https://docs.astral.sh/uv/
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv --version
  python --version  # Should be 3.10+
  ```

- [ ] **Git** - Version control
  ```bash
  git --version
  ```

### External Services Setup

- [ ] **Create Supabase Project**
  1. Go to https://supabase.com
  2. Create new project: `curriculumextractor-dev`
  3. Note your credentials:
     - **Project URL**: `https://xxxxx.supabase.co`
     - **Anon Public Key**: `eyJhbG...` (for frontend)
     - **Service Role Key**: `eyJhbG...` (for backend, keep secret!)
     - **Database Password**: Set during project creation
  4. Get connection string:
     - Settings → Database → Connection String (URI mode)
     - Example: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

### Environment Configuration

- [ ] **Update `.env` file** with your Supabase credentials:
  ```env
  # Project Info
  PROJECT_NAME="CurriculumExtractor"
  STACK_NAME=curriculum-extractor
  ENVIRONMENT=local
  DOMAIN=localhost
  FRONTEND_HOST=http://localhost:5173

  # Backend
  SECRET_KEY=your-secret-key-here  # Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
  BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173"

  # Supabase (REPLACE WITH YOUR CREDENTIALS)
  SUPABASE_URL=https://xxxxx.supabase.co
  SUPABASE_ANON_KEY=eyJhbG...  # Anon public key
  SUPABASE_SERVICE_KEY=eyJhbG...  # Service role key (backend only)
  DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

  # Redis + Celery (will be added)
  REDIS_URL=redis://:changethis@redis:6379/0
  REDIS_PASSWORD=changethis  # Generate secure password for production
  CELERY_BROKER_URL=${REDIS_URL}
  CELERY_RESULT_BACKEND=${REDIS_URL}

  # Supabase Storage Buckets
  SUPABASE_STORAGE_BUCKET_WORKSHEETS=worksheets
  SUPABASE_STORAGE_BUCKET_EXTRACTIONS=extractions

  # Auth (using existing template structure)
  FIRST_SUPERUSER=admin@curriculumextractor.com
  FIRST_SUPERUSER_PASSWORD=changethis  # Change for production!

  # Email (optional for now)
  SMTP_HOST=
  SMTP_USER=
  SMTP_PASSWORD=
  EMAILS_FROM_EMAIL=noreply@curriculumextractor.com

  # Monitoring (optional)
  SENTRY_DSN=

  # Note: POSTGRES_* vars no longer needed (using Supabase)
  ```

### Initial Setup Commands

- [ ] **Install backend dependencies**:
  ```bash
  cd backend
  uv sync
  source .venv/bin/activate  # Or: .venv\Scripts\activate on Windows
  ```

- [ ] **Install frontend dependencies**:
  ```bash
  cd frontend
  npm install
  ```

- [ ] **Install pre-commit hooks**:
  ```bash
  uv run pre-commit install
  ```

- [ ] **Test basic stack** (before infrastructure changes):
  ```bash
  # Will fail because we haven't updated docker-compose yet
  # Skip for now until we clean up and add Redis/Celery
  ```

---

## 2. Files to DELETE (Template Examples)

### Backend - "Items" CRUD Example

**Purpose**: Template's example feature - not relevant to CurriculumExtractor

```bash
# Delete these files:
rm backend/app/api/routes/items.py
rm backend/tests/api/routes/test_items.py

# Models will be kept but modified (keep user models, remove Item model)
# CRUD will be kept but modified (keep user CRUD, remove item CRUD)
```

### Frontend - "Items" Components

```bash
# Delete entire Items components folder:
rm -rf frontend/src/components/Items/

# Delete Items-related components:
rm frontend/src/components/Common/ItemActionsMenu.tsx
rm frontend/src/components/Pending/PendingItems.tsx

# Delete Items route:
rm frontend/src/routes/_layout/items.tsx
```

### Template Documentation & Images

```bash
# Delete template screenshots (not relevant to your project):
rm -rf img/

# Delete template-specific docs (keep development.md, deployment.md for reference):
rm README.md  # Will be replaced with CurriculumExtractor README
rm release-notes.md  # Template release notes
rm SECURITY.md  # Generic security policy (not project-specific)
```

### Frontend E2E Tests (Template-Specific)

```bash
# Delete template-specific E2E tests:
# Keep user-settings.spec.ts (user management is relevant)
# Keep login.spec.ts, sign-up.spec.ts, reset-password.spec.ts (auth is relevant)
# No items-related tests exist, so nothing to delete here
```

---

## 3. Files to KEEP (Core Infrastructure)

### Backend - Core Structure ✅

**Keep these - they're fundamental to FastAPI + your project:**

```
backend/
├── app/
│   ├── __init__.py ✅
│   ├── main.py ✅ (FastAPI app entry)
│   ├── models.py ✅ (will be extended with Extraction/Question models)
│   ├── crud.py ✅ (will be extended, remove Item CRUD functions)
│   ├── utils.py ✅ (email, passwords, tokens - all relevant)
│   ├── initial_data.py ✅ (creates first superuser)
│   ├── backend_pre_start.py ✅ (DB connection check)
│   ├── tests_pre_start.py ✅ (test setup)
│   ├── core/
│   │   ├── config.py ✅ (will add Supabase/Redis config)
│   │   ├── db.py ✅ (will update for Supabase)
│   │   └── security.py ✅ (password hashing, JWT)
│   ├── api/
│   │   ├── deps.py ✅ (auth dependencies - very useful)
│   │   ├── main.py ✅ (API router)
│   │   └── routes/
│   │       ├── login.py ✅ (authentication)
│   │       ├── users.py ✅ (user management for Content Reviewers)
│   │       ├── utils.py ✅ (health checks)
│   │       └── private.py ✅ (example private route)
│   ├── alembic/ ✅ (database migrations - critical)
│   └── email-templates/ ✅ (password reset emails)
├── tests/ ✅ (testing infrastructure - keep all except test_items.py)
├── scripts/ ✅ (prestart, test scripts)
└── pyproject.toml ✅ (dependencies)
```

### Frontend - Core Structure ✅

```
frontend/
├── src/
│   ├── main.tsx ✅ (entry point)
│   ├── theme.tsx ✅ (Chakra UI theme)
│   ├── utils.ts ✅ (utility functions)
│   ├── routes/
│   │   ├── __root.tsx ✅ (root layout)
│   │   ├── _layout.tsx ✅ (authenticated layout)
│   │   ├── _layout/
│   │   │   ├── index.tsx ✅ (dashboard home)
│   │   │   ├── admin.tsx ✅ (admin panel - useful for Content Admins)
│   │   │   └── settings.tsx ✅ (user settings)
│   │   ├── login.tsx ✅
│   │   ├── signup.tsx ✅
│   │   ├── recover-password.tsx ✅
│   │   └── reset-password.tsx ✅
│   ├── components/
│   │   ├── Common/
│   │   │   ├── Navbar.tsx ✅ (will need to update links)
│   │   │   ├── Sidebar.tsx ✅ (will need to update menu items)
│   │   │   ├── SidebarItems.tsx ✅ (will replace Items link)
│   │   │   ├── UserMenu.tsx ✅
│   │   │   ├── NotFound.tsx ✅
│   │   │   └── DeleteAlert.tsx ✅ (reusable delete confirmation)
│   │   ├── Admin/ ✅ (admin user management)
│   │   ├── UserSettings/ ✅ (user profile editing)
│   │   ├── Pending/ ✅ (loading states)
│   │   └── ui/ ✅ (Chakra UI primitives)
│   ├── hooks/ ✅ (custom React hooks - useAuth, etc.)
│   ├── client/ ✅ (auto-generated OpenAPI client)
│   └── theme/ ✅ (Chakra theme config)
├── tests/ ✅ (Playwright tests - keep auth tests)
├── package.json ✅
└── vite.config.ts ✅
```

### Development Tooling ✅

```
.pre-commit-config.yaml ✅ (Ruff, Biome linting)
.github/workflows/ ✅ (CI/CD - may need updates)
docker-compose.yml ✅ (will be heavily modified)
docker-compose.override.yml ✅ (local dev overrides)
.env ✅ (environment variables - update for Supabase)
```

### Documentation (Newly Created) ✅

```
CLAUDE.md ✅ (will be updated for CurriculumExtractor)
docs/ ✅ (all newly created documentation structure)
development.md ✅ (keep for reference on Docker workflow)
deployment.md ✅ (keep for reference on production deployment)
```

---

## 4. Infrastructure Changes Needed

### A. Docker Compose - Major Overhaul

**Remove**:
- `db` service (local Postgres) → Replaced by Supabase
- `adminer` service (DB admin UI) → Use Supabase dashboard instead

**Add**:
- `redis` service (message broker for Celery)
- `celery-worker` service (background job processing)
- `flower` service (optional - Celery monitoring UI)

**Update**:
- `backend` service: Remove `db` dependency, add `redis` dependency
- Environment variables: Add Supabase + Redis configs

**New docker-compose.yml structure** (see below for full file)

### B. Backend Dependencies (pyproject.toml)

**Add to `[project.dependencies]`**:
```toml
"supabase<3.0.0,>=2.0.0"              # Supabase Python client
"celery[redis]<6.0.0,>=5.3.4"         # Celery with Redis support
"redis<5.0.0,>=4.6.0"                 # Redis client
"boto3<2.0.0,>=1.28.0"                # S3-compatible storage (Supabase)
"pypdf<4.0.0,>=3.0.0"                 # PDF manipulation
"python-docx<1.0.0,>=0.8.11"          # DOCX processing
"pillow<11.0.0,>=10.0.0"              # Image processing
"opencv-python<5.0.0,>=4.8.0"         # Computer vision utilities
```

**Add to `[tool.uv.dev-dependencies]`** (optional):
```toml
"flower<3.0.0,>=2.0.0"                # Celery monitoring
```

### C. Frontend Dependencies (package.json)

**Add to `dependencies`**:
```json
{
  "react-pdf": "^9.2.0",
  "react-pdf-highlighter": "^6.1.0",
  "@supabase/supabase-js": "^2.45.0",
  "katex": "^0.16.9"
}
```

**Add to `devDependencies`**:
```json
{
  "@types/react-pdf": "^7.0.0"
}
```

### D. Backend Code Changes

**1. Update `backend/app/core/config.py`**:
- Add Supabase settings (URL, keys, buckets)
- Add Redis settings
- Remove local Postgres defaults

**2. Update `backend/app/core/db.py`**:
- Update connection string to use Supabase
- Keep Alembic migration logic

**3. Update `backend/app/models.py`**:
- **Remove**: `Item`, `ItemCreate`, `ItemUpdate`, `ItemPublic`, `ItemsPublic`
- **Keep**: All `User*` models (needed for Content Reviewers/Admins)
- **Add** (later): `Extraction`, `Question`, `Ingestion`, `Tag` models

**4. Update `backend/app/crud.py`**:
- **Remove**: All item-related CRUD functions
- **Keep**: User CRUD functions

**5. Create `backend/app/worker.py`** (new file):
- Celery app configuration
- Task imports

**6. Create `backend/app/tasks/` (new directory)**:
- `extraction.py` - Async extraction pipeline tasks

**7. Update `backend/app/api/main.py`**:
- Remove `items` router import/include

### E. Frontend Code Changes

**1. Update `frontend/src/components/Common/SidebarItems.tsx`**:
- Remove "Items" link
- Add "Extractions" link (placeholder for now)

**2. Update `frontend/src/routes/_layout/index.tsx`**:
- Remove Items references
- Update dashboard content for CurriculumExtractor

**3. Create placeholder routes** (optional for now):
- `frontend/src/routes/_layout/extractions.tsx`
- `frontend/src/routes/_layout/questions.tsx`

---

## 5. Recommended Execution Order

### Phase 1: Cleanup Template (30 minutes)

1. **Delete template files**:
   ```bash
   # Backend
   rm backend/app/api/routes/items.py
   rm backend/tests/api/routes/test_items.py

   # Frontend
   rm -rf frontend/src/components/Items/
   rm frontend/src/components/Common/ItemActionsMenu.tsx
   rm frontend/src/components/Pending/PendingItems.tsx
   rm frontend/src/routes/_layout/items.tsx

   # Documentation & images
   rm -rf img/
   rm README.md
   rm release-notes.md
   rm SECURITY.md
   ```

2. **Update models and CRUD** (backend):
   - Edit `backend/app/models.py`: Remove Item models
   - Edit `backend/app/crud.py`: Remove item CRUD functions
   - Edit `backend/app/api/main.py`: Remove items router

3. **Update frontend navigation**:
   - Edit `frontend/src/components/Common/SidebarItems.tsx`: Remove Items link
   - Edit `frontend/src/routes/_layout/index.tsx`: Update dashboard

### Phase 2: Environment Setup (1 hour)

4. **Create Supabase project** and get credentials
5. **Update `.env`** file with Supabase credentials
6. **Run migrations against Supabase**:
   ```bash
   cd backend
   source .venv/bin/activate
   alembic upgrade head
   ```

### Phase 3: Add Infrastructure (2-3 hours)

7. **Update `docker-compose.yml`** with Redis + Celery
8. **Add backend dependencies**:
   ```bash
   cd backend
   # Edit pyproject.toml (add Supabase, Celery, Redis, etc.)
   uv sync
   ```
9. **Add frontend dependencies**:
   ```bash
   cd frontend
   # Edit package.json (add react-pdf, KaTeX, etc.)
   npm install
   ```
10. **Create Celery worker files**:
    - `backend/app/worker.py`
    - `backend/app/tasks/extraction.py`

11. **Test full stack**:
    ```bash
    docker compose up -d
    docker compose logs -f
    ```

### Phase 4: Update Documentation (30 minutes)

12. **Update CLAUDE.md** for CurriculumExtractor
13. **Create new README.md** for the project
14. **Update `docs/` as needed**

---

## 6. Quick Start After Cleanup

Once you complete the cleanup and infrastructure setup:

```bash
# 1. Start all services
docker compose watch

# 2. Access points:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Flower (Celery): http://localhost:5555 (if enabled)

# 3. Create first user (Content Admin):
# Already happens via FIRST_SUPERUSER in .env

# 4. Begin feature development:
# - Create Extraction models
# - Create Ingestion API endpoints
# - Create review UI components
```

---

## Next Steps

After completing this setup, you'll be ready to start implementing the features from your PRD:

1. **Phase 1: Core Models** (Week 1)
   - Create `Extraction`, `Question`, `Ingestion` models
   - Set up Supabase Storage buckets
   - Test file upload flow

2. **Phase 2: Extraction Pipeline** (Weeks 2-3)
   - Implement Celery tasks for PDF processing
   - Integrate ML adapters (OCR, segmentation, tagging)
   - Test async workflow

3. **Phase 3: Review UI** (Weeks 4-5)
   - Build PDF viewer with react-pdf
   - Create question review interface
   - Implement LaTeX rendering with KaTeX

4. **Phase 4: Question Bank** (Week 6)
   - Implement approval workflow
   - Add curriculum tagging UI
   - Create export capabilities

---

**Questions or issues?** Refer to:
- `@docs/getting-started/setup.md` - Detailed setup instructions
- `@docs/architecture/overview.md` - System architecture
- `CLAUDE.md` - Quick reference for development
