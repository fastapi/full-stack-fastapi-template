# PRD: CurriculumExtractor - Product Overview

**Version**: 1.2
**Component**: Full-stack (Platform)
**Status**: Active Development
**Last Updated**: 2025-10-22
**Related**: [Math Extraction Feature](./features/math-worksheet-question-extractor.md), [Infrastructure Setup](./features/infrastructure-setup.md)

---

## 1. Overview

### What & Why

CurriculumExtractor is an AI-powered platform that automates the extraction and structuring of educational content from K-12 worksheets, assessments, and teaching materials across all subjects in the Singapore education system. It transforms manual question entry from hours to minutes while ensuring accurate curriculum alignment and maintaining quality through human-in-the-loop review.

### Scope

**In scope**:
- Multi-subject document processing (Math, Science, Languages, Humanities) for K-12 Singapore
- PDF and DOCX upload with OCR for scanned materials
- Intelligent question segmentation with cross-page linking
- Subject-specific content extraction (equations, diagrams, passages, source materials)
- Multi-question type support (MCQ, short answer, structured, essay, practical)
- Curriculum auto-tagging with subject-specific taxonomies
- Human-in-the-loop review interface with side-by-side PDF viewer
- Question bank persistence with version control and audit trail
- Full LaTeX rendering in review UI for mathematical expressions
- Asset management (images, diagrams, tables, charts)
- Export capabilities (JSON, QTI, custom formats)

**Out of scope (v1)**:
- Question authoring from scratch (extraction only)
- Advanced plagiarism detection across large corpora
- Non-Singapore curriculum frameworks (IGCSE/IB deferred to v2)
- Real-time collaborative editing (single reviewer per extraction)
- Public-facing question search (internal tool only)
- Batch re-classification of existing questions

### Living Document

This PRD evolves during development:
- Refinements based on ML model accuracy testing across subjects
- Edge cases discovered during multi-subject worksheet ingestion
- UI/UX improvements from reviewer feedback
- Schema adjustments for new question types and subject taxonomies
- Version updates with phased subject rollout

### Non-Functional Requirements

- **Performance**:
  - Upload processing: <2min for 10-page PDF at p95
  - Review UI loads: <1s initial page, <500ms per question navigation
  - API endpoints: <200ms response time for review CRUD operations
  - LaTeX rendering: <100ms for complex equations
  - PDF rendering: <1s for first page, <500ms for subsequent pages
  - Celery throughput: ≥10 extraction tasks/minute
  - Supabase Storage upload: <5s for 10MB PDF
- **Security**:
  - JWT authentication for all API endpoints
  - Row-level security (RLS) in Supabase for multi-tenancy
  - Uploaded files stored with presigned URLs (7-day expiry for drafts)
  - No PII in documents; PDPA compliance for Singapore
  - Redis password authentication enabled
  - Supabase Service Key server-side only (never exposed to frontend)
- **Accessibility**:
  - WCAG 2.1 Level AA for review UI
  - Keyboard navigation (J/K/E/A shortcuts)
  - Screen reader support for form fields
  - High contrast mode for LaTeX rendering
- **Reliability**:
  - Celery task retry: 3 attempts with exponential backoff
  - Redis persistence: RDB + AOF for durability
  - Graceful worker shutdown on SIGTERM
  - Service health checks: backend, Redis, Celery worker
- **Scalability**:
  - Process 1,000 worksheets/month initially
  - Support concurrent reviewers (5+ simultaneous users)
  - Background job queue for async processing (Celery + Redis)
  - Horizontal Celery worker scaling via Docker Compose replicas
  - Supabase connection pooling (pgBouncer built-in)
  - Redis max memory: 256MB with LRU eviction policy

---

## 2. User Stories

### Primary Story
**As a** Content Operations Reviewer (teacher/editor)
**I want** to upload worksheets from any K-12 subject and see auto-extracted questions with curriculum tags
**So that** I can quickly review, fix tags, and approve questions for the question bank without manual typing

### Supporting Stories

**As a** Content Ops Reviewer
**I want** to correct mis-tagged questions across different subjects (e.g., P4 Decimals → P5 Percentage, or S3 History WWI → Geography)
**So that** questions are accurately aligned with the correct subject taxonomy

**As a** Content Ops Reviewer
**I want** to review LaTeX-rendered mathematical expressions in the review UI
**So that** I can verify equations are correctly extracted before approval

**As a** Content Admin
**I want** to configure subject-specific extraction pipelines (Math equations vs Science diagrams vs Language passages)
**So that** each subject uses optimized ML adapters

**As a** Content Admin
**I want** to manage taxonomy versions across all subjects (Math, Science, Languages, Humanities)
**So that** curriculum updates are tracked and questions remain aligned

**As a** Developer/Integrator
**I want** to query approved questions via API by subject, grade, and topic
**So that** I can generate multi-subject worksheets and assessments for the LMS

---

## 3. Acceptance Criteria (Gherkin)

### Scenario: Multi-Subject Upload and Extraction
```gherkin
Given I am logged in as a Content Reviewer
And I have a P5 Science PDF with 8 questions (2 diagram-based, 1 experimental)
When I upload the PDF via the ingestion form
And I select subject "Science" and tagger "deberta-v3-sg-science"
Then the system processes the PDF within 90 seconds
And I see 8 questions listed in the review UI
And each question has suggested Science taxonomy tags (Top-3 themes with confidences)
And diagrams are extracted with labeled components
And the ingestion status is "DRAFT"
```

### Scenario: LaTeX Rendering in Review UI
```gherkin
Given I have a DRAFT extraction with a P6 Math question containing equation "\frac{3x + 2}{5} = 7"
When I view the question in the review UI
Then I see the equation fully rendered as LaTeX with proper formatting
And the LaTeX render time is <100ms
And I can toggle between rendered and raw LaTeX views
```

### Scenario: Subject-Specific Tagging
```gherkin
Given I upload a Secondary 2 English comprehension passage with 5 questions
When the tagging stage completes
Then questions are tagged with English Language taxonomy (e.g., S2.EL.COMP.INF, S2.EL.COMP.MAIN)
And not with Math or Science taxonomies
And confidence scores reflect subject-appropriate classifications
```

### Scenario: Cross-Subject Question Bank Query
```gherkin
Given I am a Developer querying the question bank API
When I request "GET /api/questions?subject=Mathematics&grade=P4&topic=Decimals&limit=10"
Then I receive 10 approved Math questions matching the criteria
And each question includes full LaTeX rendering data for equations
And results do not include Science or Language questions
```

---

## 4. Functional Requirements

### Supported Subjects (K-12 Singapore)

### Primary Level (P1-P6)
- **Mathematics** - Numbers, Algebra, Geometry, Measurement, Statistics
- **Science** - Life Science, Physical Science, Earth & Space
- **English Language** - Comprehension, Grammar, Vocabulary, Composition
- **Mother Tongue Languages** - Chinese, Malay, Tamil (reading comprehension, grammar)

### Secondary Level (S1-S4/S5)
- **Mathematics** - E-Math, A-Math
- **Sciences** - Physics, Chemistry, Biology, Science (lower secondary)
- **Humanities** - History, Geography, Social Studies, Literature
- **Languages** - English, Mother Tongue (Higher/Standard)

### Junior College (JC1-JC2)
- **H1/H2/H3 Subjects** - Mathematics, Sciences, Humanities, Languages

### Curriculum Frameworks
- Singapore Primary Mathematics Syllabus (2025)
- Singapore Primary Science Syllabus
- O-Level syllabuses (MOE)
- A-Level syllabuses (SEAB)
- Cambridge IGCSE (for international schools)

### Core Behavior

### 1. Multi-Subject Document Processing
- PDF and DOCX upload with OCR for scanned materials
- Subject detection from document metadata or user selection
- Adaptive extraction based on subject type (e.g., Math equations, Science diagrams, Language comprehension passages)

### 2. Intelligent Question Segmentation
- Multi-part question detection (a/b/c or 1/2/3 sub-parts)
- Cross-page question linking with confidence scoring
- Subject-specific content extraction:
  - **Math**: Equations, diagrams, graphs, tables
  - **Science**: Diagrams, experimental data, charts
  - **Languages**: Passages, comprehension questions, grammar exercises
  - **Humanities**: Maps, timelines, source materials, essays

### 3. Question Type Support
- **Multiple Choice (MCQ)**: Single/multi-select with options
- **Short Answer**: Text, numeric, fill-in-the-blank
- **Structured Answer**: Multi-part responses with marking schemes
- **Essay/Open-ended**: With sample responses and rubrics
- **Practical/Experimental**: Science practicals, math problem-solving steps

### 4. Curriculum Auto-Tagging
- **Subject-specific taxonomies**:
  - **Math**: Strand → Topic → Learning Objective (e.g., P4.NA.DEC.1.5 - Decimals, Rounding)
  - **Science**: Theme → Topic → Concept (e.g., P5.LS.SYS.2.1 - Life Systems, Human Body)
  - **Languages**: Skill → Component → Standard (e.g., S2.EL.COMP.INF - Comprehension, Inference)
  - **Humanities**: Domain → Theme → Outcome (e.g., S3.HIS.WWI.CAUSES - History, WW1, Causes)
- **Multi-label support**: Questions can span multiple topics/skills
- **Confidence scoring**: AI suggests Top-3 tags with confidence levels
- **Taxonomy versioning**: Track curriculum updates (e.g., 2013 vs 2025 syllabus)

### 5. Human-in-the-Loop Review Interface
- Side-by-side PDF viewer with extracted content editor
- Visual overlays for detected blocks (questions, options, answers, diagrams)
- Tag picker with hierarchical curriculum search across subjects
- Cross-page seam controls (merge/split questions)
- Batch approval with confidence thresholds
- Keyboard shortcuts for rapid review (J/K navigation, E edit, A approve)

### 6. Asset Management
- Image/diagram extraction with bounding boxes
- Block-level positioning (before/after text, as options)
- Support for tables, equations, charts
- LaTeX detection for mathematical expressions
- Object storage integration (Supabase Storage)

### 7. Question Bank Persistence
- Structured storage with complete metadata
- Version control and audit trail
- Multi-label curriculum tagging
- Full-text search with embedding support (future)
- Export capabilities (JSON, QTI, custom formats)

### Business Rules

1. **Subject Selection**: Each extraction must specify a primary subject (Math, Science, Language, Humanities)
2. **Subject-Specific Taxonomies**: Tags must match the subject's curriculum framework (no cross-subject tagging)
3. **LaTeX Validation**: All Math/Science equations must pass LaTeX syntax validation before approval
4. **Multi-Label Support**: Questions can have 1-5 taxonomy tags within the same subject
5. **Primary Tag Constraint**: Each question must have exactly 1 tag marked `is_primary=true`
6. **Taxonomy Versioning**: All tags reference the active curriculum version for that subject
7. **File Retention**: Draft PDFs stored for 30 days; approved PDFs archived indefinitely

### Permissions

- **Access**:
  - Content Reviewer: Upload, review, approve/reject across all subjects
  - Content Admin: All reviewer actions + taxonomy management, bulk operations, pipeline configuration
  - Developer: Read-only API access to approved questions (via API key)
- **Visibility**:
  - Reviewers see only their own drafts unless admin
  - Approved questions visible to all authenticated users
  - Rejected/archived visible to admins only

---

## 5. Technical Specification

### User Roles

### Content Operations Reviewer (Primary User)
- Uploads worksheets across all subjects
- Reviews auto-extracted questions
- Corrects tags and content
- Approves for question bank ingestion
- **Subjects**: All K-12 subjects (Math, Science, Languages, Humanities)

### Content Admin
- Manages taxonomy versions across subjects
- Performs bulk operations (re-tag, re-classify)
- Configures extraction pipelines per subject
- Monitors quality metrics
- Manages user permissions

### Developer/Integrator
- Queries question bank via API
- Generates worksheets and assessments
- Integrates with LMS platforms
- Builds subject-specific tools

### Architecture Pattern

### Modular ML Pipeline
- **Stage 1 - OCR & Layout**: Text + image extraction (Mistral OCR, PaddleOCR)
- **Stage 2 - Segmentation**: Question boundary detection (LayoutLMv3)
- **Stage 3 - Tagging**: Subject-specific classifiers (DeBERTa-v3 fine-tuned per subject)
- **Stage 4 - Review & Approve**: Human validation + persistence

### Subject-Specific Adaptations
- **Math**: LaTeX parsing, equation recognition, diagram labeling
- **Science**: Diagram annotation, experimental procedure extraction
- **Languages**: Passage-question linking, grammar rule identification
- **Humanities**: Source material extraction, essay rubric parsing

### Technology Stack

**Backend**:
- **FastAPI** 0.114+ - Python web framework with automatic OpenAPI docs
- **SQLModel** 0.0.21 - SQL ORM with Pydantic integration
- **PostgreSQL** 17 via **Supabase** - Managed Postgres with RLS and pgBouncer
- **Celery** 5.3+ - Distributed task queue for async extraction pipeline
- **Redis** 7 - Message broker and result backend for Celery
- **Supabase Storage** - S3-compatible object storage for PDFs and assets

**Frontend**:
- **React** 19 + **TypeScript** 5.2 - UI framework with type safety
- **Vite** 7 - Fast build tool with hot module replacement
- **TanStack Router/Query** - Type-safe routing and data fetching
- **Chakra UI** 3 - Accessible component library
- **react-pdf** 9.x - PDF rendering via PDF.js
- **react-pdf-highlighter** 6.x - Annotation layer for question highlights
- **KaTeX** - Fast LaTeX rendering (<100ms)

**ML Pipeline**:
- **Mistral OCR** / **PaddleOCR** - Text extraction with bounding boxes
- **LayoutLMv3** - Document layout understanding and segmentation
- **DeBERTa-v3** - Subject-specific curriculum tagging (fine-tuned per subject)

**Infrastructure**:
- **Docker Compose** - Development and production deployment
- **Supabase** - Managed Postgres + Storage + Auth platform
- **Traefik** - Reverse proxy with automatic HTTPS (production)
- **GitHub Actions** - CI/CD pipelines for testing and deployment

**Rationale**:
- Supabase provides managed Postgres + Storage + Auth in one platform, reducing DevOps overhead
- Redis + Celery is industry-standard for Python async tasks, battle-tested at scale
- react-pdf uses PDF.js (Mozilla) for robust, cross-browser PDF rendering
- Modular architecture enables subject-specific ML model swapping without changing business logic
- KaTeX provides fast (<100ms), accessible LaTeX rendering in review UI

---

## 6. Integration Points

### Dependencies

**Internal**:
- `app/models.py`: Extend with subject-specific extraction models
- `app/api/routes/ingestions.py`: Multi-subject ingestion endpoints
- `app/ml/adapters/`: Subject-specific ML adapters (math, science, language, humanities)
- `app/worker.py`: Celery worker configuration and task imports
- `app/tasks/extraction.py`: Async extraction pipeline tasks
- Frontend: KaTeX/MathJax integration + react-pdf for LaTeX and PDF rendering

**External Services**:
- **Supabase**:
  - **Postgres**: Managed PostgreSQL 17 with Row-Level Security (RLS)
  - **Storage**: S3-compatible buckets (`worksheets`, `extractions`)
  - **Auth**: JWT-based authentication (future)
- **Redis**: Message broker for Celery (in-memory, password-protected)
- **ML Model Servers** (HTTP APIs):
  - Subject-specific taggers (DeBERTa-v3 fine-tuned per subject)
  - OCR engines (Mistral OCR, PaddleOCR)
  - Segmentation models (LayoutLMv3)

**Backend Python Packages** (add to `pyproject.toml`):
```toml
[project.dependencies]
# Existing: fastapi, sqlmodel, pydantic, alembic, psycopg, ...

# Infrastructure additions:
"supabase<3.0.0,>=2.0.0"              # Supabase Python client
"celery[redis]<6.0.0,>=5.3.4"         # Celery with Redis support
"redis<5.0.0,>=4.6.0"                 # Redis client
"boto3<2.0.0,>=1.28.0"                # S3-compatible storage (Supabase)
"flower<3.0.0,>=2.0.0"                # Celery monitoring (optional)

# Document processing:
"pypdf<4.0.0,>=3.0.0"                 # PDF manipulation
"python-docx<1.0.0,>=0.8.11"          # DOCX processing
"pillow<11.0.0,>=10.0.0"              # Image processing
"opencv-python<5.0.0,>=4.8.0"         # Computer vision utilities
```

**Frontend Packages** (add to `package.json`):
```json
{
  "dependencies": {
    "react-pdf": "^9.2.0",
    "react-pdf-highlighter": "^6.1.0",
    "@supabase/supabase-js": "^2.45.0",
    "katex": "^0.16.9"
  },
  "devDependencies": {
    "@types/react-pdf": "^7.0.0"
  }
}
```

**Environment Variables**:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key  # Backend only
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# Redis + Celery
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=changethis
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# Supabase Storage Buckets
SUPABASE_STORAGE_BUCKET_WORKSHEETS=worksheets
SUPABASE_STORAGE_BUCKET_EXTRACTIONS=extractions
```

---

## 7. UX Specifications

### Key UI States

1. **Subject Selection**: Dropdown to select subject before upload (Math, Science, English, etc.)
2. **LaTeX Rendering**: Inline KaTeX rendering in review UI with toggle to raw LaTeX
3. **Subject-Specific Tag Picker**: Hierarchical taxonomy search filtered by selected subject
4. **Multi-Subject Question Bank**: Filter and search across subjects with visual subject badges
5. **PDF Viewer with Annotations**: Side-by-side PDF viewer with color-coded question region highlights

### PDF Viewer UI (React)

**Component Structure**:
```tsx
import { Document, Page } from 'react-pdf'
import { PdfHighlighter, Highlight } from 'react-pdf-highlighter'

<PdfHighlighter
  pdfUrl={extractionPdfUrl}
  highlights={questionRegions}  // [{page, bbox, color, id}]
  onSelectionFinished={(highlight) => handleQuestionSelect(highlight)}
>
  {/* Rendered pages with color-coded annotations */}
</PdfHighlighter>
```

**Annotation Colors** (Question Components):
- **Green**: QUES (question text)
- **Blue**: PART (multi-part sub-question)
- **Orange**: OPT (MCQ option)
- **Red**: ANS (answer)
- **Purple**: EXPL (explanation)

**Layout**:
- **Desktop**: Side-by-side PDF (left 60%) + question list (right 40%), split pane resizable
- **Tablet**: PDF takes 40%, question list 60%, touch-friendly zoom controls
- **Mobile**: Tab switcher ("PDF" / "Questions"), swipe to navigate pages

**Performance**:
- Lazy page loading with virtualization (only render visible pages)
- PDF.js worker runs in Web Worker (non-blocking UI)
- <1s first page load, <500ms subsequent pages

### LaTeX Rendering Specifications

- **Renderer**: KaTeX (faster) or MathJax (more complete)
- **Inline equations**: Rendered within question text
- **Display equations**: Centered, full-width rendering
- **Error handling**: Show raw LaTeX with error message if rendering fails
- **Accessibility**: Provide MathML output for screen readers
- **Performance**: <100ms render time for complex equations (50+ symbols)

---

## 8. Implementation Guidance

### Infrastructure Setup

See **[Infrastructure Setup PRD](./features/infrastructure-setup.md)** for comprehensive step-by-step implementation (5 phases over 6 days):

**Phase 1: Supabase Database Migration**
- Create Supabase project and obtain credentials
- Update DATABASE_URL in .env
- Run Alembic migrations against Supabase Postgres

**Phase 2: Supabase Storage Setup**
- Create storage buckets (`worksheets`, `extractions`)
- Configure Row-Level Security (RLS) policies
- Test file upload and presigned URL generation

**Phase 3: Redis + Celery**
- Add Redis service to docker-compose.yml
- Create Celery worker service
- Implement sample extraction task
- Test task queueing and execution

**Phase 4: React PDF Integration**
- Install react-pdf and react-pdf-highlighter packages
- Configure PDF.js worker
- Create PDF viewer component with annotation layer
- Test rendering performance

**Phase 5: Integration Testing**
- End-to-end test: Upload PDF → Queue task → Render with annotations
- Verify all services start with health checks passing
- Performance benchmarking

### LaTeX Integration

**Frontend** (`frontend/src/components/LatexRenderer.tsx`):
```typescript
import katex from 'katex'
import 'katex/dist/katex.min.css'

export function LatexRenderer({ latex }: { latex: string }) {
  try {
    const html = katex.renderToString(latex, {
      throwOnError: false,
      displayMode: true
    })
    return <div dangerouslySetInnerHTML={{ __html: html }} />
  } catch (error) {
    return <pre className="latex-error">{latex}</pre>
  }
}
```

**Backend** (validation only, rendering is client-side):
```python
import re

def validate_latex(text: str) -> bool:
    """Basic LaTeX syntax validation"""
    # Check for balanced braces
    open_braces = text.count('{')
    close_braces = text.count('}')
    if open_braces != close_braces:
        return False

    # Check for balanced delimiters
    if text.count('\\left') != text.count('\\right'):
        return False

    return True
```

### Subject-Specific Adapter Pattern

Each subject has dedicated ML adapters:
- `MathTaggerAdapter`: Fine-tuned for Math taxonomy
- `ScienceTaggerAdapter`: Fine-tuned for Science themes
- `LanguageTaggerAdapter`: Fine-tuned for Language skills
- `HumanitiesTaggerAdapter`: Fine-tuned for Humanities domains

Configured via `app/core/config.py`:
```python
SUBJECT_TAGGERS = {
    "Mathematics": "deberta-v3-sg-math",
    "Science": "deberta-v3-sg-science",
    "English": "deberta-v3-sg-english",
    "History": "deberta-v3-sg-history",
    # ... other subjects
}
```

### Docker Compose Infrastructure

**Services** (docker-compose.yml):
```yaml
services:
  # Backend API (FastAPI)
  backend:
    build: ./backend
    depends_on:
      redis: { condition: service_healthy }
    environment:
      - DATABASE_URL=${DATABASE_URL}  # Supabase Postgres
      - SUPABASE_URL=${SUPABASE_URL}
      - REDIS_URL=${REDIS_URL}

  # Redis (Message Broker)
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]

  # Celery Worker (Background Jobs)
  celery-worker:
    build: ./backend
    command: celery -A app.worker worker --loglevel=info --concurrency=4
    depends_on:
      redis: { condition: service_healthy }
      backend: { condition: service_healthy }
    environment:
      - CELERY_BROKER_URL=${REDIS_URL}
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}

  # Frontend (React)
  frontend:
    build: ./frontend
    depends_on:
      - backend

volumes:
  redis-data:
```

**Note**: Local Postgres `db` service removed - using Supabase managed Postgres instead.

---

## 9. Testing Strategy

### Unit Tests
- [ ] LaTeX renderer handles complex equations (fractions, matrices, integrals)
- [ ] LaTeX validator detects malformed syntax
- [ ] Subject-specific taggers return correct taxonomy codes
- [ ] Multi-subject question filtering works correctly
- [ ] Supabase client initializes with correct credentials
- [ ] Celery task serialization/deserialization works correctly
- [ ] Redis connection pool handles concurrent connections
- [ ] PDF.js worker loads correctly in React

### Integration Tests
- [ ] Upload Math worksheet → LaTeX renders in review UI
- [ ] Upload Science worksheet → diagrams extract correctly
- [ ] Cross-subject API queries return only matching subject questions
- [ ] Upload PDF → Supabase Storage → Presigned URL accessible
- [ ] Queue Celery task → Worker processes → Result stored in Redis
- [ ] Backend connects to Supabase Postgres → Alembic migrations run
- [ ] Frontend fetches PDF from presigned URL → react-pdf renders

### E2E Tests
- [ ] Full workflow: Upload P4 Math PDF → review with LaTeX → approve → verify in question bank
- [ ] Subject switching: Upload different subjects, verify correct taxonomies applied
- [ ] Infrastructure: Upload PDF → Queue extraction → Worker processes → Frontend displays PDF with annotations
- [ ] Docker Compose startup: All services (backend, redis, celery-worker) start with health checks passing

---

## 10. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **LaTeX rendering performance issues** | Medium (slow UI) | Low | Use KaTeX for speed, cache rendered equations, lazy load |
| **Subject taxonomy drift across updates** | High (mis-tagged questions) | Medium | Version all taxonomies, migration scripts for updates |
| **ML model accuracy varies by subject** | High (unusable extractions) | Medium | Subject-specific benchmarking, fallback to manual tagging |
| **Complex multi-subject worksheets** | Medium (tagging confusion) | Low | Require single subject per extraction, flag mixed-subject for manual review |
| **Supabase free tier limits exceeded** | High (service disruption) | Medium | Monitor storage/bandwidth usage; upgrade to paid tier if needed |
| **Celery worker memory leak** | High (worker crash) | Medium | Set task time limits, monitor memory, restart workers daily |
| **Redis out of memory** | High (task queue failure) | Medium | Set maxmemory policy to LRU eviction; monitor queue depth |
| **PDF rendering performance on large files** | Medium (slow UI) | High | Implement lazy loading, virtualization; compress PDFs on upload |

---

## 11. Rollout Plan

### Success Metrics

### Productivity
- **Baseline**: 10 questions/hour (manual entry)
- **Target**: 50+ questions/hour (5x improvement)
- **Approval rate**: ≥80% of drafts approved within 24 hours

### Quality
- **Extraction accuracy**: ≥85% correct question segmentation
- **Tagging accuracy**:
  - Top-1: ≥75% match with manual gold labels
  - Top-3: ≥90% includes correct tag
- **Cross-page linking**: ≥80% precision, ≥85% recall

### Scale
- **Volume**: 1,000 worksheets/month (Year 1)
- **Subjects**: Primary Math → Primary Science → Secondary subjects (phased rollout)
- **Curriculum coverage**: All Singapore MOE syllabuses by Year 2

### Phased Rollout

**Phase 1: MVP (Current - Weeks 1-6)**
**Focus**: Primary Mathematics (P1-P6)
- Complete extraction pipeline
- Review UI with curriculum tagging
- Question bank persistence
- **Status**: In Development

### Phase 2: Multi-Subject Expansion (Weeks 7-14)
**Focus**: Primary Science + English
- Subject-specific ML adapters
- Expanded taxonomy management
- Multi-subject question bank
- **Timeline**: After MVP completion

### Phase 3: Secondary & Beyond (Weeks 15-26)
**Focus**: Secondary Math/Science, Humanities
- Advanced question types (essays, practicals)
- Marking scheme extraction
- QTI export for LMS integration
- **Timeline**: Q2 2026

### Phase 4: Intelligence Layer (Q3-Q4 2026)
**Focus**: Advanced features
- Semantic search across question bank
- Difficulty auto-classification (beyond easy/medium/hard)
- Question generation from topics
- Duplicate/plagiarism detection
- **Timeline**: Q3-Q4 2026

---

## 12. References

### Related Documents

### Feature Specifications
- **[Math Worksheet Extraction](./features/math-worksheet-question-extractor.md)** - Detailed PRD for Primary Math (reference implementation)
- **Science Extraction** (Planned - Phase 2)
- **Language Comprehension Extraction** (Planned - Phase 2)

### Technical Documentation
- **[Architecture Overview](../architecture/overview.md)** - System design
- **[Question Bank Schema](../data/Questionbank_data_schema.md)** - Complete data model
- **[API Documentation](../api/overview.md)** - REST API reference

### Getting Started
- **[Setup Guide](../getting-started/setup.md)** - Installation
- **[Development Workflow](../getting-started/development.md)** - Daily development

---

## Appendix: Subject-Specific Considerations

### Mathematics
- **Challenges**: Equation parsing, diagram labeling, multi-step solutions
- **Special handling**: LaTeX detection, symbolic math validation
- **Taxonomy**: 5-level hierarchy (Level → Strand → Sub-strand → Topic → LO)
- **Example**: P4.NA.DEC.1.5 = P4 → Number & Algebra → Decimals → Rounding → 1 d.p.

### Science
- **Challenges**: Experimental diagrams, data tables, practical procedures
- **Special handling**: Diagram annotation, variable extraction
- **Taxonomy**: Theme-based (Diversity, Cycles, Systems, Energy, Interactions)
- **Example**: P5.LS.SYS.2.1 = P5 → Life Science → Systems → Human Body → Digestive System

### Languages (English/Mother Tongue)
- **Challenges**: Long comprehension passages, context-dependent questions
- **Special handling**: Passage-question linking, grammar rule tagging
- **Taxonomy**: Skill-based (Reading, Writing, Oral, Listening)
- **Example**: S2.EL.COMP.INF = S2 → English → Comprehension → Inference

### Humanities (History/Geography/Social Studies)
- **Challenges**: Source materials (maps, documents, images), essay questions
- **Special handling**: Source-question linking, rubric extraction
- **Taxonomy**: Domain-based (History, Geography, Social Studies)
- **Example**: S3.HIS.WWI.CAUSES = S3 → History → World War I → Causes & Outbreak

---

---

## Change Log

### [2025-10-22] v1.2
- Status: Active Development
- Changes:
  - **Added** comprehensive infrastructure specifications from [Infrastructure Setup PRD](./features/infrastructure-setup.md)
  - **Enhanced** Non-Functional Requirements with infrastructure metrics (Celery, Redis, Supabase)
  - **Updated** Technology Stack with detailed infrastructure components (Supabase, Redis, Celery, react-pdf)
  - **Expanded** Integration Points with backend/frontend packages and environment variables
  - **Added** PDF Viewer UI specifications with annotation colors and responsive layouts
  - **Added** Docker Compose infrastructure section with service definitions
  - **Enhanced** Testing Strategy with infrastructure-specific tests (Supabase, Celery, Redis, react-pdf)
  - **Added** Infrastructure risks to Risks & Mitigation table
  - **Added** Infrastructure Setup section to Implementation Guidance with 5-phase plan

### [2025-10-22] v1.1
- Status: Active Development
- Changes:
  - **Removed** "Full LaTeX rendering" from non-goals - now in scope with full KaTeX/MathJax support
  - **Restructured** document to follow standard PRD template (12 numbered sections)
  - **Added** LaTeX rendering specifications and implementation guidance
  - **Added** Acceptance Criteria with Gherkin scenarios for multi-subject and LaTeX features
  - **Added** detailed User Stories for multi-subject workflows
  - **Enhanced** Technical Specification with LaTeX integration patterns
  - **Clarified** subject-specific adapter pattern and taxonomy management

### [2025-10-22] v1.0
- Status: Active Development
- Initial product overview created
- Multi-subject vision established
- Phased rollout plan defined

---

**Next Review**: After infrastructure setup completion (Supabase + Redis + Celery + react-pdf)
