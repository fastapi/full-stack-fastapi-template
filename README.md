# CurriculumExtractor

**AI-Powered K-12 Worksheet Question Extraction Platform for Singapore Education**

Extract, structure, and tag educational content from worksheets across all subjects (Math, Science, Languages, Humanities) with AI-powered OCR, segmentation, and curriculum-aligned tagging.

---

## 🎯 What is CurriculumExtractor?

CurriculumExtractor automates the extraction of questions from K-12 worksheets, transforming hours of manual data entry into minutes. It combines:

- **Multi-subject document processing** - Math, Science, Languages, Humanities
- **Intelligent AI pipeline** - OCR → Segmentation → Curriculum Tagging
- **Human-in-the-loop review** - Side-by-side PDF viewer with question editor
- **Singapore curriculum alignment** - Auto-tagging with MOE syllabus taxonomies
- **LaTeX rendering** - Fast mathematical expression display with KaTeX
- **Question bank persistence** - Structured storage with version control

**Target Users**: Content Operations Reviewers, Admins, and Integrators in EdTech

---

## ✨ Key Features

### Infrastructure (Complete ✅)
- ✅ **FastAPI Backend** - Python 3.10 with async support
- ✅ **React Frontend** - React 19 with TypeScript 5.2
- ✅ **Supabase PostgreSQL** - Managed database (Session Mode, ap-south-1)
- ✅ **Celery + Redis** - Async task queue (4 worker processes)
- ✅ **User Authentication** - JWT with 8-day expiry
- ✅ **Task API** - Queue, monitor, and retrieve async task results
- ✅ **Docker Compose** - Full-stack orchestration with hot-reload

### Phase 1: MVP (Primary Mathematics P1-P6) - In Progress
- ✅ Infrastructure complete (Supabase + Celery + Redis)
- ✅ User management and authentication
- ✅ Task queue for async processing
- ⏳ Extraction models (PDF → Question)
- ⏳ OCR and question segmentation (PaddleOCR + docTR)
- ⏳ Review UI with PDF annotation (react-pdf)
- ⏳ LaTeX math rendering (KaTeX)
- ⏳ Curriculum tagging
- ⏳ Question bank export

### Phase 2-4: Future
- Multi-subject expansion (Science, English, Humanities)
- Subject-specific ML adapters (DeBERTa-v3 fine-tuned)
- Advanced question types (essays, practicals)
- Semantic search and difficulty classification

See **[Product Requirements](docs/prd/overview.md)** for complete feature list.

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Node.js](https://nodejs.org/) v20+ (via nvm/fnm)
- [Python](https://www.python.org/) 3.10+ with [uv](https://docs.astral.sh/uv/)
- [Supabase](https://supabase.com) account (free tier)

### Setup

**For detailed setup instructions**, see:
- **[Setup Guide](docs/getting-started/setup.md)** - Complete installation guide
- **[Supabase Setup Guide](docs/getting-started/supabase-setup-guide.md)** - Database configuration

**Quick Start**:

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd CurriculumExtractor
   ```

2. **Configure Supabase**
   - Project ID: `wijzypbstiigssjuiuvh` (ap-south-1 region)
   - Connection: Session Mode (port 5432)
   - Update `.env` with your credentials
   
3. **Start development**
   ```bash
   docker compose watch
   ```

4. **Access application**
   - **Frontend**: http://localhost:5173
   - **Backend**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   
5. **Login**
   - Email: `admin@curriculumextractor.com`
   - Password: From `FIRST_SUPERUSER_PASSWORD` in `.env`

**All services (7)** will start automatically:
- Backend (FastAPI), Frontend (React), Database (Supabase)
- Redis, Celery Worker, Proxy (Traefik), MailCatcher

---

## 🏗️ Technology Stack

**Backend** (Python 3.10):
- **FastAPI** 0.115+ - Async web framework with OpenAPI docs
- **SQLModel** 0.0.24 - ORM combining Pydantic + SQLAlchemy
- **PostgreSQL** 17 via **Supabase** - Managed database (Session Mode)
- **Celery** 5.5 + **Redis** 7 - Distributed task queue (4 workers)
- **psycopg3** - PostgreSQL driver with prepared statement support
- **Alembic** - Database migrations
- **pyjwt** - JWT authentication

**Frontend** (TypeScript 5.2):
- **React** 19 - UI framework
- **Vite** 7 - Build tool with HMR
- **TanStack Router** - File-based routing
- **TanStack Query** - Server state management
- **Chakra UI** 3 - Component library
- **react-pdf** 9.x (planned) - PDF viewing
- **KaTeX** (planned) - LaTeX math rendering

**ML Pipeline** (Phase 2):
- **PaddleOCR** - Text extraction with bounding boxes
- **docTR** - Document layout analysis
- **DeBERTa-v3** - Curriculum tagging (fine-tuned for Singapore syllabus)

**Infrastructure**:
- **Docker Compose** - Development orchestration (7 services)
- **Supabase** - Managed PostgreSQL 17 + S3-compatible Storage
  - Project: wijzypbstiigssjuiuvh
  - Region: ap-south-1 (Mumbai, India)
  - Mode: Session pooler (10 base + 20 overflow connections)
- **Redis** 7 - Message broker for Celery
- **GitHub Actions** - CI/CD with 7 workflows
- **Traefik** - Reverse proxy (production)

---

## 📁 Project Structure

```
CurriculumExtractor/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Config, security, DB
│   │   ├── models.py     # SQLModel schemas
│   │   ├── crud.py       # Database operations
│   │   ├── worker.py     # Celery configuration
│   │   └── tasks/        # Async extraction tasks
│   ├── tests/            # Pytest tests
│   └── scripts/          # Utility scripts
├── frontend/             # React application
│   ├── src/
│   │   ├── routes/       # TanStack Router pages
│   │   ├── components/   # React components
│   │   ├── client/       # Auto-generated OpenAPI client
│   │   └── hooks/        # Custom React hooks
│   └── tests/            # Playwright E2E tests
├── docs/                 # Documentation
│   ├── getting-started/  # Setup and development guides
│   ├── prd/             # Product requirements
│   ├── architecture/    # System design
│   └── api/             # API documentation
├── scripts/             # Project scripts
└── docker-compose.yml   # Service orchestration
```

---

## 📖 Documentation

### Getting Started
- **[Setup Guide](docs/getting-started/setup.md)** - Installation instructions
- **[Supabase Setup](docs/getting-started/supabase-setup-guide.md)** - Database configuration
- **[Development Workflow](docs/getting-started/development.md)** - Daily development
- **[Environment Status](ENVIRONMENT_READY.md)** - Current setup status

### Product & Architecture
- **[Product Overview](docs/prd/overview.md)** - Complete PRD
- **[Architecture Overview](docs/architecture/overview.md)** - System design
- **[Data Models](docs/data/models.md)** - Database schema
- **[API Documentation](docs/api/overview.md)** - REST API reference

### Development
- **[CLAUDE.md](CLAUDE.md)** - Quick reference for AI-assisted development
- **[SETUP_PLAN.md](SETUP_PLAN.md)** - Template cleanup and implementation phases
- **[SETUP_STATUS.md](SETUP_STATUS.md)** - Detailed environment status

---

## 🧪 Testing

### Backend (Pytest)
```bash
cd backend
bash scripts/test.sh
```

### Frontend (Playwright)
```bash
cd frontend
npx playwright test
```

### Linting & Type Checking
```bash
# Pre-commit hooks (recommended)
uv run pre-commit install
uv run pre-commit run --all-files

# Manual checks
cd backend && uv run ruff check . && uv run mypy .
cd frontend && npm run lint
```

---

## 🔄 Development Workflow

1. **Start services**
   ```bash
   docker compose watch  # Hot-reload enabled
   ```

2. **Make changes** - Edit code, changes auto-reload

3. **Run tests**
   ```bash
   bash backend/scripts/test.sh
   cd frontend && npx playwright test
   ```

4. **Database migrations** (when models change)
   ```bash
   docker compose exec backend bash
   alembic revision --autogenerate -m "Description"
   alembic upgrade head
   ```

5. **Update frontend client** (when API changes)
   ```bash
   ./scripts/generate-client.sh
   ```

See **[Development Guide](docs/getting-started/development.md)** for more.

---

## 🗂️ Current Status

**Updated**: October 23, 2025  
**Phase**: MVP Development (Primary Mathematics)  
**Environment**: ✅ **Fully Operational**

### ✅ Infrastructure Complete (100%)

- [x] **FastAPI Backend** - Python 3.10, async, JWT auth
- [x] **React Frontend** - React 19, TypeScript, TanStack Router/Query
- [x] **Supabase PostgreSQL** - Session Mode, 10+20 connection pool
- [x] **Celery Worker** - 4 processes, tested with health_check + test_task
- [x] **Redis** - Message broker, result backend
- [x] **Docker Compose** - 7 services orchestrated with hot-reload
- [x] **GitHub Actions** - 7 CI/CD workflows (lint, test, generate client)
- [x] **Documentation** - CLAUDE.md, development.md, API docs, architecture

### ✅ Development Environment (100%)

- [x] Supabase project created (wijzypbstiigssjuiuvh, ap-south-1)
- [x] Database connected (PostgreSQL 17.6.1)
- [x] Migrations working (Alembic + Supabase MCP)
- [x] Admin user created (admin@curriculumextractor.com)
- [x] Celery tasks tested (health_check: 0.005s, test_task: 10s)
- [x] Task API endpoints (/api/v1/tasks/)
- [x] Template cleanup (Item model removed)
- [x] All services healthy

### ⏳ Feature Development (0% - Ready to Start)

**Next Milestones**:
1. Create core models (Extraction, Question, Ingestion, Tag)
2. Set up Supabase Storage buckets (worksheets, extractions)
3. Add document processing libraries (PaddleOCR, docTR, pypdf)
4. Install PDF viewing libraries (react-pdf, KaTeX)
5. Build review UI components
6. Implement extraction Celery task
7. Create question bank API

**Current Focus**: Creating Extraction/Question data models ← **YOU ARE HERE**

### 📊 Progress Summary

```
✅ Environment Setup        - 100% (All services operational)
✅ Infrastructure           - 100% (Supabase + Celery working)
✅ Documentation           - 100% (2,405+ lines updated)
✅ CI/CD                   - 100% (7 workflows configured)
⏳ Core Models             -   0% (Next step)
⏳ Document Processing     -   0% (Libraries ready to add)
⏳ Review UI               -   0% (After models)
⏳ ML Integration          -   0% (Phase 2)
```

**Track detailed progress**: See [CLAUDE.md](CLAUDE.md#project-specific-notes)

---

## 📊 Roadmap

### Phase 1: MVP (Weeks 1-6) - Current
- Primary Math extraction pipeline
- Review UI with PDF viewer
- Curriculum tagging
- Question bank persistence

### Phase 2: Multi-Subject (Weeks 7-14)
- Primary Science + English support
- Subject-specific ML adapters
- Expanded taxonomy management

### Phase 3: Secondary & Beyond (Weeks 15-26)
- Secondary Math/Science/Humanities
- Advanced question types
- QTI export for LMS

### Phase 4: Intelligence Layer (Q3-Q4 2026)
- Semantic search
- Difficulty classification
- Question generation
- Duplicate detection

See **[Product Roadmap](docs/prd/overview.md#11-rollout-plan)** for details.

---

## 🤝 Contributing

See **[Contributing Guide](docs/getting-started/contributing.md)**

### Development Setup
1. Follow [Setup Guide](docs/getting-started/setup.md)
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run `uv run pre-commit run --all-files`
5. Submit pull request

### Code Standards
- **Backend**: Ruff + mypy (enforced by pre-commit)
- **Frontend**: Biome linting (enforced by pre-commit)
- **Tests**: ≥80% coverage target
- **Commits**: Conventional commits format

---

## 📄 License

[License information to be added]

---

## 🆘 Support

### Common Issues

**Setup Problems**:
- See [Setup Guide](docs/getting-started/setup.md#troubleshooting)
- See [Development Workflow](docs/getting-started/development.md#troubleshooting)

**Supabase Issues**:
- See [Supabase Setup Guide](docs/getting-started/supabase-setup-guide.md)
- Use MCP: `mcp_supabase_get_project(id="wijzypbstiigssjuiuvh")`
- Check logs: `mcp_supabase_get_logs(project_id="wijzypbstiigssjuiuvh", service="postgres")`

**Celery Issues**:
- Check worker: `docker compose logs celery-worker -f`
- Test Redis: `docker compose exec redis redis-cli -a <password> PING`
- Inspect tasks: `docker compose exec celery-worker celery -A app.worker inspect registered`

**Docker Issues**:
- View logs: `docker compose logs -f`
- Restart service: `docker compose restart backend`
- Rebuild: `docker compose build backend && docker compose up -d`

### Resources

- **Documentation**: [docs/](docs/) - Complete guides
- **API Docs**: http://localhost:8000/docs - Interactive API explorer
- **Supabase Dashboard**: https://app.supabase.com/project/wijzypbstiigssjuiuvh
- **Development Guide**: [CLAUDE.md](CLAUDE.md) - AI-assisted development
- **Architecture**: [docs/architecture/overview.md](docs/architecture/overview.md)

---

## 🎯 Project Goals

**Mission**: Transform manual question entry from hours to minutes while maintaining curriculum alignment accuracy.

**Success Metrics**:
- 5x productivity improvement (10 → 50+ questions/hour)
- ≥85% extraction accuracy
- ≥90% curriculum tagging accuracy (Top-3)
- 1,000 worksheets/month capacity (Year 1)

**Impact**: Enable EdTech platforms to scale content operations efficiently across all K-12 subjects in Singapore.

---

---

## 📈 Development Environment

**Status**: ✅ **All Systems Operational**

```
Services Running:
✅ Backend (FastAPI)      - http://localhost:8000 (healthy)
✅ Frontend (React)       - http://localhost:5173
✅ Database (Supabase)    - PostgreSQL 17.6.1 (Session Mode)
✅ Redis                  - localhost:6379 (healthy)
✅ Celery Worker          - 4 processes (ready)
✅ Proxy (Traefik)        - localhost:80
✅ MailCatcher            - localhost:1080

Configuration:
✅ Supabase Project       - wijzypbstiigssjuiuvh (ap-south-1)
✅ Connection Pooling     - 10 base + 20 overflow = 30 max
✅ Task Queue             - Celery 5.5 with Redis broker
✅ Authentication         - JWT with bcrypt password hashing
✅ CI/CD                  - 7 GitHub Actions workflows
✅ Documentation          - 2,405+ lines (CLAUDE.md, docs/)
```

**Ready for feature development!** Start building extraction models →

---

**Built with FastAPI + React + Supabase + Celery**  
**Powered by AI for Singapore Education** 🚀

---

## 🔗 Quick Links

### Documentation

| Resource | Link | Purpose |
|----------|------|---------|
| **CLAUDE.md** | [CLAUDE.md](CLAUDE.md) | AI development guide (Supabase MCP, patterns, quick ref) |
| **Setup Guide** | [docs/getting-started/setup.md](docs/getting-started/setup.md) | Installation & Supabase setup |
| **Development Workflow** | [docs/getting-started/development.md](docs/getting-started/development.md) | Daily development guide |
| **Product PRD** | [docs/prd/overview.md](docs/prd/overview.md) | Complete product requirements |
| **Architecture** | [docs/architecture/overview.md](docs/architecture/overview.md) | System design & data flow |
| **API Reference** | [docs/api/overview.md](docs/api/overview.md) | API endpoints & examples |
| **Testing Strategy** | [docs/testing/strategy.md](docs/testing/strategy.md) | Testing guide |
| **Deployment** | [docs/deployment/environments.md](docs/deployment/environments.md) | Environment setup |

### Live Services (When Running)

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React application |
| **Backend API** | http://localhost:8000 | FastAPI server |
| **API Docs** | http://localhost:8000/docs | Swagger UI (try it out!) |
| **MailCatcher** | http://localhost:1080 | Email testing |
| **Traefik Dashboard** | http://localhost:8090 | Proxy stats |
| **Supabase Dashboard** | https://app.supabase.com/project/wijzypbstiigssjuiuvh | Database & storage management |

### Commands

```bash
# Start development
docker compose watch

# View logs
docker compose logs -f backend
docker compose logs -f celery-worker

# Test Celery
curl -X POST http://localhost:8000/api/v1/tasks/health-check

# Run tests
cd backend && bash scripts/test.sh
cd frontend && npx playwright test

# Database migration
docker compose exec backend alembic revision --autogenerate -m "Add model"
docker compose exec backend alembic upgrade head
```

