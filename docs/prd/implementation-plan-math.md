# Implementation Plan: Math Question Extraction (MVP)

**Version**: 1.0
**Scope**: Primary Mathematics (P1-P6) only
**Timeline**: 12 weeks (3 phases)
**Last Updated**: 2025-10-22
**Related**: [Product Overview](./overview.md), [Infrastructure Setup](./features/infrastructure-setup.md), [Math Extraction Feature](./features/math-worksheet-question-extractor.md)

---

## Executive Summary

This plan breaks down the Math Question Extraction MVP into **12 epics** organized across **3 phases**. Each epic delivers tangible user value and builds toward the complete extraction pipeline.

**Goal**: Enable Content Reviewers to extract Math questions from PDF worksheets 5x faster than manual entry, with ≥85% extraction accuracy and LaTeX support.

---

## Phase 1: Foundation & Upload (Weeks 1-3)

**Goal**: Reviewers can upload Math PDFs and view them in the system.

### Epic 1: Infrastructure Setup
**User Story**: As a DevOps Engineer, I want all infrastructure services configured, so the development environment is ready for feature implementation.

**Scope**:
- Supabase project setup (Postgres + Storage)
- Redis + Celery worker in Docker Compose
- Environment variables configuration
- Health checks for all services
- Database migrations setup (Alembic)

**Deliverables**:
- [ ] Supabase project created with DATABASE_URL
- [ ] Storage buckets: `worksheets`, `extractions`
- [ ] Redis service running with password auth
- [ ] Celery worker service configured (4 concurrency)
- [ ] `docker compose up` starts all services successfully
- [ ] Health check endpoints return 200 OK

**Acceptance Criteria**:
```gherkin
Given all environment variables are set in .env
When I run docker compose up
Then all services start without errors
And health checks pass for backend, Redis, Celery worker
And backend connects to Supabase Postgres successfully
```

**Estimated Duration**: 3-5 days
**Dependencies**: None (foundational)
**Risks**: Supabase free tier limits; mitigation: monitor usage

---

### Epic 2: Document Upload & Storage
**User Story**: As a Content Reviewer, I want to upload Math PDF worksheets, so they are stored securely for processing.

**Scope**:
- Upload API endpoint (`POST /api/v1/ingestions`)
- Supabase Storage integration
- Presigned URL generation (7-day expiry)
- Basic extraction record creation (status: UPLOADED)
- File validation (PDF/DOCX, max 25MB)

**Deliverables**:
- [ ] `POST /api/v1/ingestions` endpoint with file upload
- [ ] Upload to Supabase `worksheets` bucket
- [ ] Generate presigned URL and store in `extractions` table
- [ ] Extract metadata: filename, file size, page count, MIME type
- [ ] Frontend upload form (drag-and-drop or file picker)
- [ ] Upload progress indicator

**Acceptance Criteria**:
```gherkin
Given I am logged in as a Content Reviewer
When I upload a 5MB Math PDF via the ingestion form
Then the PDF is uploaded to Supabase Storage within 5 seconds
And a presigned URL with 7-day expiry is generated
And an extraction record is created with status "UPLOADED"
And I see a success message with extraction ID
```

**Estimated Duration**: 5-7 days
**Dependencies**: Epic 1 (Infrastructure)
**Risks**: Large file uploads timeout; mitigation: chunk uploads or increase timeout

---

### Epic 3: PDF Viewer Integration
**User Story**: As a Content Reviewer, I want to view uploaded Math PDFs in the browser, so I can visually inspect the document before processing.

**Scope**:
- react-pdf integration with PDF.js worker
- PDF rendering component with pagination
- Lazy loading and virtualization
- Basic navigation (next/prev page, zoom)
- Mobile-responsive layout

**Deliverables**:
- [ ] Install react-pdf and configure PDF.js worker
- [ ] `PDFViewer` component with Document/Page rendering
- [ ] Pagination controls (page X of Y, next/prev buttons)
- [ ] Zoom controls (fit width, fit height, zoom in/out)
- [ ] Lazy page loading (only render visible pages)
- [ ] Loading states and error handling
- [ ] Route: `/ingestions/:id/review` displays PDF

**Acceptance Criteria**:
```gherkin
Given I have an extraction with a valid PDF URL
When I navigate to the review page
Then the PDF renders in the browser within 1 second (first page)
And I can navigate to any page using pagination controls
And subsequent pages load within 500ms
And the PDF is responsive on desktop, tablet, mobile
```

**Estimated Duration**: 5-7 days
**Dependencies**: Epic 2 (Document Upload)
**Risks**: Large PDFs slow performance; mitigation: virtualization, compress on upload

---

## Phase 2: Extraction Pipeline (Weeks 4-8)

**Goal**: Automated extraction of Math questions with LaTeX support and curriculum tagging.

### Epic 4: OCR & Layout Extraction
**User Story**: As a Backend Developer, I want to extract text and images from Math PDFs with bounding boxes, so we have raw data for segmentation.

**Scope**:
- OCR adapter interface (pluggable)
- Mistral OCR or PaddleOCR integration
- Extract text tokens with bounding boxes
- Extract images/diagrams with coordinates
- Store OCR results in `ocr_results` JSONB field
- Celery task: `extract_ocr(extraction_id)`

**Deliverables**:
- [ ] `OCRAdapter` abstract class (pluggable interface)
- [ ] `MistralOCRAdapter` or `PaddleOCRAdapter` implementation
- [ ] Celery task: `tasks.extract_ocr(extraction_id)`
- [ ] Store results: `extraction.ocr_results` (tokens, bboxes, confidence)
- [ ] Extract images and upload to `extractions` bucket
- [ ] Update extraction status: UPLOADED → OCR_PROCESSING → OCR_COMPLETE
- [ ] Error handling and retry logic (3 attempts)

**Acceptance Criteria**:
```gherkin
Given an extraction with status "UPLOADED"
When the OCR task is queued
Then the task completes within 60 seconds for a 10-page PDF
And text tokens with bounding boxes are stored in ocr_results
And images/diagrams are extracted and uploaded to Supabase Storage
And extraction status updates to "OCR_COMPLETE"
And on failure, the task retries up to 3 times
```

**Estimated Duration**: 7-10 days
**Dependencies**: Epic 1 (Infrastructure), Epic 2 (Upload)
**Risks**: OCR model API downtime; mitigation: local fallback model or retry logic

---

### Epic 5: Question Segmentation
**User Story**: As a Backend Developer, I want to segment OCR text into individual Math questions with components, so we can structure the data for review.

**Scope**:
- Segmentation adapter interface (pluggable)
- LayoutLMv3 or rule-based segmentation
- Detect question boundaries (QUES, PART, OPT, ANS, EXPL)
- Handle multi-part questions (a, b, c)
- Cross-page question linking
- Celery task: `segment_questions(extraction_id)`

**Deliverables**:
- [ ] `SegmentationAdapter` abstract class
- [ ] `LayoutLMv3Adapter` or rule-based implementation
- [ ] Celery task: `tasks.segment_questions(extraction_id)`
- [ ] Create `questions` table with extracted data
- [ ] Store bounding boxes for each component (QUES, PART, OPT, ANS, EXPL)
- [ ] Detect multi-part questions (parts array)
- [ ] Cross-page linking (confidence scoring)
- [ ] Update status: OCR_COMPLETE → SEGMENTATION_PROCESSING → SEGMENTATION_COMPLETE

**Acceptance Criteria**:
```gherkin
Given an extraction with status "OCR_COMPLETE"
When the segmentation task is queued
Then the task completes within 90 seconds for a 10-page PDF
And individual questions are created in the questions table
And each question has components: QUES, PART (if multi-part), OPT (if MCQ), ANS, EXPL
And bounding boxes are stored for each component
And multi-part questions are correctly linked (a, b, c)
And extraction status updates to "SEGMENTATION_COMPLETE"
```

**Estimated Duration**: 10-12 days
**Dependencies**: Epic 4 (OCR)
**Risks**: Complex layouts (cross-page, nested parts); mitigation: confidence thresholds, manual review

---

### Epic 6: LaTeX Detection & Extraction
**User Story**: As a Backend Developer, I want to detect and extract LaTeX equations from Math questions, so they can be rendered properly in the review UI.

**Scope**:
- LaTeX detection (heuristic or regex-based)
- Extract inline and display equations
- Validate LaTeX syntax (balanced braces, delimiters)
- Store LaTeX separately in `latex_content` JSONB field
- Integration with segmentation pipeline

**Deliverables**:
- [ ] LaTeX detection function (regex patterns for common LaTeX commands)
- [ ] Extract inline equations: `$...$`, `\\(...\\)`
- [ ] Extract display equations: `$$...$$`, `\\[...\\]`, `\begin{equation}...\end{equation}`
- [ ] Validate LaTeX syntax (balanced braces, `\left`/`\right` pairs)
- [ ] Store in `questions.latex_content` JSONB
- [ ] Flag questions with LaTeX for review priority
- [ ] Unit tests for complex equations (fractions, matrices, integrals)

**Acceptance Criteria**:
```gherkin
Given a question with text "Solve \\frac{3x + 2}{5} = 7 for x"
When the LaTeX detection runs
Then the LaTeX "\\frac{3x + 2}{5} = 7" is extracted
And stored in the latex_content field
And LaTeX syntax validation passes
And the question is flagged for LaTeX review
```

**Estimated Duration**: 5-7 days
**Dependencies**: Epic 5 (Segmentation)
**Risks**: Complex LaTeX syntax (nested commands); mitigation: fallback to raw text, manual correction

---

### Epic 7: Math Curriculum Tagging
**User Story**: As a Backend Developer, I want to auto-tag Math questions with Singapore Primary Math taxonomy, so reviewers get suggested tags.

**Scope**:
- Math taxonomy setup (Singapore Primary Math syllabus)
- DeBERTa-v3 Math tagger adapter
- Auto-tag with Top-3 suggestions + confidence scores
- Store tags in `question_tags` table
- Celery task: `tag_questions(extraction_id)`

**Deliverables**:
- [ ] Math taxonomy table: `taxonomies` (code, description, level, strand, topic)
- [ ] Populate with Singapore Primary Math syllabus (e.g., P4.NA.DEC.1.5)
- [ ] `MathTaggerAdapter` with DeBERTa-v3 integration
- [ ] Celery task: `tasks.tag_questions(extraction_id)`
- [ ] Generate Top-3 tag suggestions with confidence scores
- [ ] Store in `question_tags` (question_id, taxonomy_code, confidence, is_primary)
- [ ] Update status: SEGMENTATION_COMPLETE → TAGGING_PROCESSING → DRAFT

**Acceptance Criteria**:
```gherkin
Given an extraction with status "SEGMENTATION_COMPLETE"
When the tagging task is queued
Then the task completes within 45 seconds for 10 questions
And each question has Top-3 taxonomy suggestions
And confidence scores are between 0.0 and 1.0
And the highest confidence tag is marked is_primary=true
And extraction status updates to "DRAFT"
```

**Estimated Duration**: 7-10 days
**Dependencies**: Epic 5 (Segmentation)
**Risks**: Taxonomy misalignment, low accuracy; mitigation: fine-tuning on Singapore Math dataset

---

### Epic 8: Background Job Orchestration
**User Story**: As a Backend Developer, I want the full extraction pipeline (OCR → Segment → Tag) to run automatically in the background, so reviewers don't wait.

**Scope**:
- Celery task orchestration (chain tasks)
- Task: `extract_worksheet_pipeline(extraction_id)`
- Progress tracking (update extraction.progress field)
- Error handling and failure notifications
- Task monitoring (optional: Celery Flower)

**Deliverables**:
- [ ] Celery task: `tasks.extract_worksheet_pipeline(extraction_id)`
- [ ] Chain tasks: OCR → Segmentation → LaTeX → Tagging
- [ ] Progress tracking: update `extraction.progress` (0-100%)
- [ ] On failure: update status to "FAILED", log error
- [ ] Retry logic: 3 attempts with exponential backoff
- [ ] (Optional) Celery Flower dashboard for monitoring
- [ ] Frontend: Poll extraction status (or WebSocket notification)

**Acceptance Criteria**:
```gherkin
Given an extraction with status "UPLOADED"
When the pipeline task is queued via POST /api/ingestions
Then the OCR task starts within 1 second
And the segmentation task runs after OCR completes
And the tagging task runs after segmentation completes
And extraction.progress updates: 0% → 30% → 60% → 100%
And extraction.status updates: UPLOADED → OCR_PROCESSING → SEGMENTATION_PROCESSING → TAGGING_PROCESSING → DRAFT
And on failure, status updates to "FAILED" with error message
```

**Estimated Duration**: 5-7 days
**Dependencies**: Epic 4, 5, 6, 7 (All pipeline tasks)
**Risks**: Task failures block pipeline; mitigation: retry logic, fallback to partial results

---

## Phase 3: Review & Approval (Weeks 9-12)

**Goal**: Reviewers can view extracted questions with LaTeX, correct tags, and approve for question bank.

### Epic 9: PDF Viewer with Annotations
**User Story**: As a Content Reviewer, I want to see color-coded question highlights on the PDF, so I can visually verify extraction accuracy.

**Scope**:
- react-pdf-highlighter integration
- Render annotations (bounding boxes) as colored overlays
- Color coding: Green=QUES, Blue=PART, Orange=OPT, Red=ANS, Purple=EXPL
- Click annotation to select corresponding question
- Synchronized scrolling (PDF ↔ Question list)

**Deliverables**:
- [ ] Install react-pdf-highlighter
- [ ] `PDFViewerWithAnnotations` component
- [ ] Render highlights from question bounding boxes
- [ ] Color-coded overlays (Green, Blue, Orange, Red, Purple)
- [ ] Click highlight → select question in right panel
- [ ] Synchronized scrolling: scroll PDF to question, or vice versa
- [ ] Performance: <100ms to render 50 annotations

**Acceptance Criteria**:
```gherkin
Given an extraction with status "DRAFT" and 8 questions
When I view the review page
Then I see the PDF with 8 color-coded highlights
And clicking a green QUES highlight selects the question in the right panel
And the question list scrolls to the selected question
And the PDF scrolls to the selected annotation when I click a question
And annotations render within 100ms
```

**Estimated Duration**: 7-10 days
**Dependencies**: Epic 3 (PDF Viewer), Epic 5 (Segmentation)
**Risks**: Performance with many annotations; mitigation: virtualization, canvas rendering

---

### Epic 10: Question Editor with LaTeX Rendering
**User Story**: As a Content Reviewer, I want to edit extracted Math questions and see LaTeX equations rendered, so I can fix errors before approval.

**Scope**:
- Question list panel (right side of PDF viewer)
- Display question text, parts, options, answer, explanation
- KaTeX integration for LaTeX rendering
- Inline edit mode (click to edit text)
- LaTeX toggle (rendered ↔ raw LaTeX)
- Save edits (debounced auto-save or manual save button)

**Deliverables**:
- [ ] Install KaTeX and configure
- [ ] `LatexRenderer` component (inline and display equations)
- [ ] `QuestionEditor` component with editable fields
- [ ] Display question components: QUES, PART, OPT, ANS, EXPL
- [ ] Inline editing: click to edit, ESC to cancel, Enter to save
- [ ] LaTeX toggle button (switch between rendered and raw LaTeX)
- [ ] Auto-save edits after 2s of inactivity
- [ ] Error handling: show raw LaTeX if rendering fails

**Acceptance Criteria**:
```gherkin
Given a question with LaTeX "\\frac{3x + 2}{5} = 7"
When I view the question in the editor
Then I see the equation rendered as a fraction
And the render time is <100ms
And I can toggle to raw LaTeX view
And I can edit the question text by clicking on it
And edits are auto-saved after 2 seconds
And if LaTeX rendering fails, I see the raw LaTeX with an error message
```

**Estimated Duration**: 7-10 days
**Dependencies**: Epic 6 (LaTeX Detection), Epic 9 (PDF Annotations)
**Risks**: Complex LaTeX fails to render; mitigation: error handling, fallback to raw text

---

### Epic 11: Tag Management & Approval Workflow
**User Story**: As a Content Reviewer, I want to correct taxonomy tags and approve questions, so they are saved to the question bank.

**Scope**:
- Tag picker component (hierarchical search)
- Display Top-3 suggested tags with confidence
- Edit tags: add/remove, mark primary
- Approve/reject individual questions or batch approval
- Update extraction status: DRAFT → IN_REVIEW → APPROVED
- Save approved questions to question bank

**Deliverables**:
- [ ] `TagPicker` component (hierarchical dropdown with search)
- [ ] Display suggested tags with confidence badges
- [ ] Add custom tags (search taxonomy, multi-select)
- [ ] Remove tags (X button)
- [ ] Mark primary tag (radio button or star icon)
- [ ] Approve button (per question) → status: APPROVED
- [ ] Reject button (per question) → status: REJECTED
- [ ] Batch approve: "Approve All High Confidence (>0.8)"
- [ ] Update extraction status: DRAFT → IN_REVIEW → APPROVED/REJECTED

**Acceptance Criteria**:
```gherkin
Given a question with suggested tags ["P4.NA.DEC.1.5" (0.85), "P4.NA.DEC.1.3" (0.72), "P5.NA.DEC.2.1" (0.68)]
When I view the tag picker
Then I see the 3 suggested tags with confidence badges
And I can search for additional tags (e.g., "P4 Fractions")
And I can add a new tag "P4.NA.FRA.2.1" and mark it as primary
And I can remove the lowest confidence tag
And I can click "Approve" to save the question with final tags
And the question status updates to "APPROVED"
And the extraction status updates to "IN_REVIEW" (if any question is approved)
```

**Estimated Duration**: 7-10 days
**Dependencies**: Epic 7 (Tagging), Epic 10 (Question Editor)
**Risks**: Taxonomy search performance; mitigation: index taxonomy table, autocomplete

---

### Epic 12: Question Bank API & Export
**User Story**: As a Developer, I want to query approved Math questions via API and export them in JSON format, so I can integrate with the LMS.

**Scope**:
- REST API for approved questions
- Query by grade, topic, taxonomy code
- Pagination and sorting
- Export endpoints (JSON, QTI format optional)
- API authentication (JWT)
- API documentation (OpenAPI/Swagger)

**Deliverables**:
- [ ] `GET /api/v1/questions` - List approved questions
- [ ] Query params: `grade`, `topic`, `taxonomy_code`, `difficulty`, `limit`, `offset`
- [ ] Response: paginated list with full question data (text, LaTeX, images, tags)
- [ ] `GET /api/v1/questions/:id` - Get single question
- [ ] `GET /api/v1/questions/export` - Export as JSON
- [ ] (Optional) `GET /api/v1/questions/export/qti` - Export as QTI 2.1
- [ ] JWT authentication for all endpoints
- [ ] OpenAPI docs auto-generated at `/docs`

**Acceptance Criteria**:
```gherkin
Given I am a Developer with a valid API key
When I request "GET /api/v1/questions?grade=P4&topic=Decimals&limit=10"
Then I receive 10 approved Math questions matching the criteria
And each question includes full data: text, LaTeX, images, tags, metadata
And the response includes pagination metadata (total, page, limit)
And the API response time is <200ms
And I can export all results as JSON via /api/v1/questions/export
```

**Estimated Duration**: 5-7 days
**Dependencies**: Epic 11 (Approval Workflow)
**Risks**: API performance with large datasets; mitigation: pagination, caching, database indexing

---

## Epic Summary Table

| Epic | Phase | Duration | Dependencies | Priority |
|------|-------|----------|--------------|----------|
| 1. Infrastructure Setup | 1 | 3-5 days | None | P0 (Blocker) |
| 2. Document Upload & Storage | 1 | 5-7 days | Epic 1 | P0 (Blocker) |
| 3. PDF Viewer Integration | 1 | 5-7 days | Epic 2 | P1 (High) |
| 4. OCR & Layout Extraction | 2 | 7-10 days | Epic 1, 2 | P0 (Blocker) |
| 5. Question Segmentation | 2 | 10-12 days | Epic 4 | P0 (Blocker) |
| 6. LaTeX Detection & Extraction | 2 | 5-7 days | Epic 5 | P1 (High) |
| 7. Math Curriculum Tagging | 2 | 7-10 days | Epic 5 | P0 (Blocker) |
| 8. Background Job Orchestration | 2 | 5-7 days | Epic 4, 5, 6, 7 | P1 (High) |
| 9. PDF Viewer with Annotations | 3 | 7-10 days | Epic 3, 5 | P1 (High) |
| 10. Question Editor with LaTeX | 3 | 7-10 days | Epic 6, 9 | P0 (Blocker) |
| 11. Tag Management & Approval | 3 | 7-10 days | Epic 7, 10 | P0 (Blocker) |
| 12. Question Bank API & Export | 3 | 5-7 days | Epic 11 | P2 (Medium) |

**Total Estimated Duration**: 72-102 days (10-14 weeks with parallelization)

---

## Success Metrics

### Phase 1 (Foundation)
- [ ] All services start successfully on `docker compose up`
- [ ] Upload a 10MB PDF in <5 seconds
- [ ] View PDF in browser with <1s first page load

### Phase 2 (Extraction)
- [ ] Process 10-page Math PDF in <2 minutes (OCR + Segment + Tag)
- [ ] ≥85% question segmentation accuracy (vs manual gold labels)
- [ ] ≥75% Top-1 tagging accuracy
- [ ] ≥90% Top-3 tagging accuracy (includes correct tag)

### Phase 3 (Review)
- [ ] Reviewers can approve 50+ questions/hour (5x improvement over 10 questions/hour manual entry)
- [ ] LaTeX renders in <100ms for 95% of equations
- [ ] ≥80% of drafts approved within 24 hours
- [ ] API response time <200ms for question queries

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
|------|--------|------------|------------|-------|
| **OCR accuracy <80% for scanned PDFs** | High | Medium | Fine-tune OCR model on Singapore Math worksheets, preprocess images | Backend Dev |
| **Segmentation fails on complex layouts** | High | Medium | Fallback to rule-based segmentation, confidence thresholds, manual review | Backend Dev |
| **LaTeX rendering errors** | Medium | Low | Fallback to raw LaTeX, error logging, manual correction | Frontend Dev |
| **Celery worker memory leaks** | High | Medium | Set task time limits, monitor memory, restart workers daily | DevOps |
| **Supabase free tier limits exceeded** | High | Medium | Monitor usage, upgrade to paid tier before limits hit | DevOps |
| **Taxonomy misalignment with MOE syllabus** | High | Low | Review taxonomy with Math teachers, version control for updates | Product Owner |
| **Review UI performance with 100+ questions** | Medium | High | Virtualization, lazy loading, pagination | Frontend Dev |

---

## Dependencies & Sequencing

### Critical Path
1. **Epic 1 (Infrastructure)** → Blocks all other epics
2. **Epic 2 (Upload)** → Blocks Epic 3, 4
3. **Epic 4 (OCR)** → Blocks Epic 5
4. **Epic 5 (Segmentation)** → Blocks Epic 6, 7, 9
5. **Epic 7 (Tagging)** → Blocks Epic 11
6. **Epic 11 (Approval)** → Blocks Epic 12

### Parallelization Opportunities
- **Phase 1**: Epic 3 (PDF Viewer) can start immediately after Epic 2 (Upload) completes
- **Phase 2**: Epic 6 (LaTeX) and Epic 7 (Tagging) can run in parallel after Epic 5 (Segmentation)
- **Phase 3**: Epic 9 (PDF Annotations) and Epic 10 (Question Editor) can overlap by 50%

---

## Next Steps

1. **Review this plan** with stakeholders (Product, Engineering, Content Ops)
2. **Prioritize epics** - Confirm P0/P1/P2 priorities
3. **Create Linear epics** - Break down into issues (see next section)
4. **Set up Linear project** - Create milestones for Phase 1, 2, 3
5. **Kick off Epic 1** - Infrastructure setup (first sprint)

---

## Appendix: Issue Breakdown Example (Epic 1)

For each epic, create approximately 8-15 Linear issues. Example for **Epic 1: Infrastructure Setup**:

- [ ] **ENG-101**: Create Supabase project and configure environment variables
- [ ] **ENG-102**: Set up Supabase Storage buckets (`worksheets`, `extractions`)
- [ ] **ENG-103**: Add Redis service to docker-compose.yml with health check
- [ ] **ENG-104**: Add Celery worker service to docker-compose.yml
- [ ] **ENG-105**: Create `app/worker.py` with Celery configuration
- [ ] **ENG-106**: Test Celery worker startup and task registration
- [ ] **ENG-107**: Update backend health check endpoint to verify Supabase connection
- [ ] **ENG-108**: Add integration test: Docker Compose startup with all services
- [ ] **ENG-109**: Update CLAUDE.md and README.md with infrastructure setup instructions
- [ ] **ENG-110**: Document environment variables in `.env.example`

Each issue should be **1-3 days** of work for a single developer.

---

**Status**: Draft - Ready for Review
**Owner**: Product Manager
**Next Review**: Before Phase 1 kickoff
