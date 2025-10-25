# Testing Strategy

**CurriculumExtractor Testing Approach**

**Last Updated**: 2025-10-25 (Optimized with 2025 AI/ML Best Practices)

---

## Testing Philosophy

- **Test-Driven Development (TDD)**: Write tests before implementation
- **Comprehensive Coverage**: ≥80% backend, ≥85% ML pipeline, 100% critical paths
- **Fast Feedback**: Unit tests <1s, integration <10s, E2E <30s
- **AI/ML Testing**: CER, F1, semantic accuracy with labeled datasets (200-500 samples/type)
- **Cost-Aware**: Balance accuracy improvements with computational costs (exponential after 95%)
- **Continuous Improvement**: Human corrections feed back to improve models
- **Mock External Services**: Supabase Storage, ML APIs, email
- **Celery Testing**: Eager mode for unit tests, real worker for integration

---

## Testing Pyramid (AI/ML Systems)

```
E2E (10%)         → Full extraction pipeline (Playwright)
Integration (20%) → API + ML + Database + Celery (Pytest)
ML Tests (30%)    → OCR accuracy, Tagging, Cost/Performance (Pytest)
Unit Tests (40%)  → Business logic, CRUD, validation (Pytest + Vitest)
  ├── Backend:  Pytest for API/CRUD/utils
  └── Frontend: Vitest for utilities/hooks/components
```

---

## Backend Testing

### Framework & Structure
- **Pytest** + FastAPI TestClient + SQLModel
- **Fixtures**: `client`, `db`, `superuser_token_headers`, `normal_user_token_headers`
- **Database**: **PostgreSQL 17** (CI & local) for production parity
- **Coverage Target**: ≥80%, run with `bash backend/scripts/test.sh`

**Why PostgreSQL for Tests?**
- ✅ Production parity - catches PostgreSQL-specific issues
- ✅ SQL dialect consistency - no SQLite surprises
- ✅ Feature coverage - full PostgreSQL capabilities (JSON ops, window functions, etc.)
- ⚠️ Tradeoff: ~30s slower than SQLite, but worth it for reliability

### Key Patterns
```python
# Fixture injection
def test_endpoint(client: TestClient, superuser_token_headers: dict):
    response = client.get("/api/v1/users/", headers=superuser_token_headers)
    assert response.status_code == 200

# Mock external services
with patch("app.utils.send_email", return_value=None):
    # Test without hitting external APIs

# Celery eager mode (runs synchronously)
celery_app.conf.update(task_always_eager=True)
```

### Test Structure
```
backend/tests/
├── conftest.py              # Shared fixtures
├── api/routes/              # API endpoint tests
├── crud/                    # CRUD operation tests
├── ml/                      # ML pipeline tests (NEW)
│   ├── test_ocr_accuracy.py
│   ├── test_segmentation.py
│   ├── test_tagging.py
│   ├── test_model_selection.py
│   └── test_feedback_loop.py
└── performance/             # NFR validation (NEW)
    ├── test_extraction_latency.py
    ├── test_celery_throughput.py
    └── test_api_response_times.py
```

---

## ML Pipeline Testing (Critical for MVP)

### Accuracy Metrics (2025 Standards)

| Metric | Target | Notes |
|--------|--------|-------|
| CER (printed) | <5% | Character Error Rate = (Ins+Del+Sub)/Total |
| CER (handwritten) | <15% | LLM-based: 82-90%, Traditional: 50-70% |
| Word-level accuracy | ≥90% | Complete word recognition |
| Semantic accuracy | 100% | Math expressions preserve meaning |
| Segmentation Precision | ≥85% | Question boundary detection |
| Segmentation Recall | ≥90% | Question boundary detection |
| Tagging Top-1 | ≥75% | Curriculum tag accuracy |
| Tagging Top-3 | ≥90% | Correct tag in top 3 |

### Evaluation Datasets
- **Requirement**: 200-500 labeled samples per document type
- **Structure**: `backend/tests/fixtures/evaluation_datasets/`
- **Labels**: Ground truth text, question boundaries, curriculum tags
- **Metadata**: Document type, difficulty, subject, handwritten/printed

### Model Selection & Cost Testing
```python
# Test accuracy vs cost tradeoffs (exponential after 95%)
@pytest.mark.parametrize("adapter,accuracy,cost", [
    (TraditionalOCR, 0.85, 0.01),  # $0.01/page, 85% accuracy
    (LLMBasedOCR, 0.92, 0.05),     # $0.05/page, 92% accuracy (5x cost, +7%)
])
def test_cost_accuracy_tradeoff(adapter, accuracy, cost):
    # Validate model selection strategy
```

### Feedback Loop
- **Track corrections**: Store human-reviewed tags vs AI predictions
- **Retrain periodically**: Fine-tune on corrected data
- **Monitor drift**: Alert if accuracy degrades >5% over time
- **A/B test**: Compare model versions before promoting to production

---

## Performance Testing (NFR Validation)

### Key Targets (from PRD)
- PDF processing: `<2min` for 10-page at p95
- Review UI: `<1s` initial load
- Question nav: `<500ms` per question
- LaTeX render: `<100ms` complex equations
- API endpoints: `<200ms` response time
- Celery: `≥10 tasks/min` throughput

### Test Approach
```python
@pytest.mark.performance
def test_pdf_processing_latency_p95():
    latencies = []
    for _ in range(20):  # p95 requires 20+ samples
        start = time.time()
        process_pdf_task.delay(pdf_id).get(timeout=180)
        latencies.append(time.time() - start)

    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    assert p95 < 120, f"P95 {p95:.2f}s exceeds 2min NFR"
```

---

## Frontend Testing

### Testing Layers

Frontend testing follows a two-layer approach:
- **Unit Tests (Vitest)**: Component logic, utilities, hooks (70%)
- **E2E Tests (Playwright)**: Critical user workflows (30%)

### Unit Testing with Vitest

**Framework**: Vitest v4.0+ with jsdom environment
**Why Vitest**:
- ⚡ Lightning-fast with Vite HMR and native ESM
- 🔥 Hot Module Replacement for instant test feedback
- 📦 Zero config TypeScript and ESM support
- 🎯 Jest-compatible API for easy migration
- 🧪 Built-in code coverage with v8

**Test Structure** (Co-location Pattern):
```
frontend/src/
├── utils/
│   ├── fileValidation.ts
│   ├── fileValidation.test.ts      # Co-located unit tests
│   ├── fileFormatting.ts
│   └── fileFormatting.test.ts
├── hooks/
│   ├── useFileUpload.ts
│   └── useFileUpload.test.ts       # Hook testing
├── components/
│   ├── UploadForm.tsx
│   └── UploadForm.test.tsx         # Component tests
└── test/
    └── setup.ts                     # Global test setup

frontend/tests/                      # E2E tests (Playwright)
├── login.spec.ts
├── pdf-viewer.spec.ts
└── extraction-review.spec.ts
```

**Configuration** (`vitest.config.ts`):
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,                    // No imports needed
    environment: 'jsdom',             // Browser-like DOM
    setupFiles: ['./src/test/setup.ts'],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/tests/**',                  // Exclude Playwright E2E
    ],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**Best Practices**:

1. **Test User Behavior, Not Implementation**
   ```typescript
   // ✅ Good - Tests behavior
   test('shows error for non-PDF files', () => {
     const docxFile = new File(['content'], 'test.docx', {
       type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
     })
     expect(validateFile(docxFile)).toBe('Invalid file type. Only PDF files are supported.')
   })

   // ❌ Avoid - Tests implementation
   test('isPDF returns false', () => {
     expect(component.state.isPDFCalled).toBe(true)
   })
   ```

2. **Co-locate Tests with Source**
   - Place `*.test.ts` files next to source files
   - Improves discoverability and maintenance
   - Scales better for large codebases

3. **Organize with `describe` Blocks**
   ```typescript
   describe('fileValidation', () => {
     describe('isPDF', () => {
       it('should return true for PDF files', () => {
         // Test logic
       })
     })

     describe('isWithinSizeLimit', () => {
       it('should return true for files under 25MB', () => {
         // Test logic
       })
     })
   })
   ```

4. **Use Descriptive Test Names**
   ```typescript
   // ✅ Clear intent
   test('should return error for PDF files over 25MB')

   // ❌ Vague
   test('validates size')
   ```

5. **Test Edge Cases**
   ```typescript
   describe('formatFileSize', () => {
     it('should handle zero bytes', () => {
       expect(formatFileSize(0)).toBe('0.00')
     })

     it('should handle exact 25MB limit', () => {
       const exactFile = new File(['x'.repeat(MAX_FILE_SIZE)], 'exact.pdf')
       expect(isWithinSizeLimit(exactFile)).toBe(true)
     })
   })
   ```

6. **Extract Testable Utilities**
   - Separate pure functions from components
   - Makes testing easier and faster
   - Example: `fileValidation.ts` extracted from `UploadForm.tsx`

7. **Mock External Dependencies**
   ```typescript
   vi.mock('@/client', () => ({
     IngestionsService: {
       createIngestion: vi.fn().mockResolvedValue({ id: '123' })
     }
   }))
   ```

8. **Clean Up After Tests**
   ```typescript
   afterEach(() => {
     vi.clearAllMocks()  // Reset mocks between tests
   })
   ```

**Running Tests**:
```bash
cd frontend

# Run all unit tests once
npm run test:run

# Watch mode (auto-rerun on changes - default for 'test' script)
npm run test

# UI mode (interactive browser)
npm run test:ui

# Run specific file
npm run test -- fileValidation.test.ts

# Coverage report
npm run test -- --coverage
```

**Real-World Example** (from `fileValidation.test.ts`):
```typescript
import { describe, expect, it } from "vitest"
import {
  ALLOWED_MIME_TYPE,
  isPDF,
  isWithinSizeLimit,
  MAX_FILE_SIZE,
  validateFile,
} from "./fileValidation"

describe("fileValidation", () => {
  describe("isPDF", () => {
    it("should return true for PDF files", () => {
      const pdfFile = new File(["content"], "test.pdf", {
        type: "application/pdf",
      })
      expect(isPDF(pdfFile)).toBe(true)
    })

    it("should return false for DOCX files", () => {
      const docxFile = new File(["content"], "test.docx", {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
      expect(isPDF(docxFile)).toBe(false)
    })
  })

  describe("isWithinSizeLimit", () => {
    it("should return true for files under 25MB", () => {
      const smallFile = new File(["x".repeat(5 * 1024 * 1024)], "small.pdf", {
        type: "application/pdf",
      })
      expect(isWithinSizeLimit(smallFile)).toBe(true)
    })

    it("should accept custom size limit", () => {
      const file = new File(["x".repeat(10 * 1024 * 1024)], "test.pdf", {
        type: "application/pdf",
      })
      const customLimit = 5 * 1024 * 1024 // 5MB
      expect(isWithinSizeLimit(file, customLimit)).toBe(false)
    })
  })

  describe("validateFile", () => {
    it("should return null for valid PDF under size limit", () => {
      const validFile = new File(["x".repeat(5 * 1024 * 1024)], "valid.pdf", {
        type: "application/pdf",
      })
      expect(validateFile(validFile)).toBeNull()
    })

    it("should return error for non-PDF files", () => {
      const docxFile = new File(["content"], "test.docx", {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
      const error = validateFile(docxFile)
      expect(error).toBe("Invalid file type. Only PDF files are supported.")
    })

    it("should return error for PDF files over 25MB", () => {
      const largeFile = new File(["x".repeat(30 * 1024 * 1024)], "large.pdf", {
        type: "application/pdf",
      })
      const error = validateFile(largeFile)
      expect(error).toContain("File too large")
      expect(error).toContain("Maximum size: 25MB")
    })
  })

  describe("constants", () => {
    it("should have correct MAX_FILE_SIZE", () => {
      expect(MAX_FILE_SIZE).toBe(25 * 1024 * 1024)
    })

    it("should have correct ALLOWED_MIME_TYPE", () => {
      expect(ALLOWED_MIME_TYPE).toBe("application/pdf")
    })
  })
})
```

**Test Output**:
```
Test Files  2 passed (2)
     Tests  25 passed (25)
  Duration  2.35s
```

### E2E Testing with Playwright

**Framework**: Playwright for end-to-end workflows
**Why Playwright**: "Everything just worked without complex mocking" (industry feedback)

**Test Structure**:
```
frontend/tests/
├── login.spec.ts
├── pdf-viewer.spec.ts        # PDF rendering + annotations
├── latex-rendering.spec.ts   # Performance + error handling
└── extraction-review.spec.ts # Full workflow
```

### PDF Viewer Testing
```typescript
test('PDF loads and displays within 1s', async ({ page }) => {
  await page.goto('/extractions/123/review')
  const startTime = Date.now()
  await expect(page.locator('canvas.react-pdf__Page__canvas').first())
    .toBeVisible({ timeout: 1000 })
  expect(Date.now() - startTime).toBeLessThan(1000) // NFR
})

test('question highlights display correct colors', async ({ page }) => {
  // Green (question), Orange (option), Red (answer) from PRD
  await expect(page.locator('.highlight.question'))
    .toHaveCSS('background-color', 'rgb(0, 255, 0)')
})
```

### LaTeX Rendering Testing
```typescript
test('complex equation renders in <100ms', async ({ page }) => {
  await page.goto('/questions/123')
  const start = performance.now()
  await expect(page.locator('.katex-display').first()).toBeVisible()
  expect(performance.now() - start).toBeLessThan(100) // NFR
})

test('malformed LaTeX shows fallback', async ({ page }) => {
  // Should show raw LaTeX with error, not crash
  await expect(page.locator('.latex-error')).toBeVisible()
})
```

---

## Celery Testing

### Unit Tests (Eager Mode)
```python
# conftest.py
celery_app.conf.update(
    broker_url="memory://",
    task_always_eager=True,
    task_eager_propagates=True,
)
```

### Integration Tests (Real Worker)
```bash
# Requires: docker compose up redis celery-worker
def test_extraction_pipeline_integration():
    task = process_pdf_task.delay("extraction-id")
    result = task.get(timeout=60)
    assert result["status"] == "completed"
```

---

## Test Categories & Coverage

| Category | Time | Coverage | Framework | Examples |
|----------|------|----------|-----------|----------|
| Unit Tests (Backend) | <1s | ≥90% | Pytest | Model validation, CRUD, utils |
| Unit Tests (Frontend) | <1s | ≥85% | Vitest | Utilities, hooks, validation |
| ML Tests | <5s | ≥85% | Pytest | OCR accuracy, tagging, cost |
| Integration | <10s | ≥80% | Pytest | API+DB, Celery, ML pipeline |
| Performance | <2min | 100% NFRs | Pytest | Latency, throughput benchmarks |
| E2E | <30s | 100% critical | Playwright | Full user workflows |

---

## Running Tests

```bash
# Backend - all tests with coverage
docker compose exec backend bash scripts/test.sh

# Backend - specific category
pytest tests/ml/ -v                # ML pipeline tests
pytest tests/performance/ -v -m performance  # Performance tests
pytest tests/api/ -v               # API tests

# Frontend - Unit tests (Vitest)
cd frontend
npm run test                       # Run all unit tests
npm run test -- --watch            # Watch mode
npm run test:ui                    # Interactive UI mode
npm run test -- --coverage         # Coverage report
npm run test -- fileValidation.test.ts  # Specific file

# Frontend - E2E tests (Playwright)
npx playwright test                # All E2E tests
npx playwright test --ui           # Interactive mode
npx playwright test pdf-viewer.spec.ts  # Specific test

# Celery - check registered tasks
docker compose exec celery-worker celery -A app.worker inspect registered
```

---

## CI/CD Testing

GitHub Actions runs on every push/PR:
1. **lint-backend** - Ruff + mypy (~1 min)
2. **test-backend** - Pytest with PostgreSQL (~5 min)
3. **lint-frontend** - Biome linting (~30s)
4. **test-frontend-unit** - Vitest unit tests (~1 min)
5. **test-frontend-e2e** - Playwright E2E (~8 min)
6. **test-docker-compose** - Smoke test (~4 min)

**CI Environment**:
- Database: **PostgreSQL 17 service container** (production parity)
- Redis: Docker Compose service (for Celery tests)
- Celery: Eager mode for unit tests
- Frontend: Node.js with Vitest + Playwright
- Coverage artifact uploaded for review

**PostgreSQL Service Container**:
```yaml
services:
  postgres:
    image: postgres:17
    env:
      POSTGRES_PASSWORD: testpassword
      POSTGRES_DB: test
    options: --health-cmd pg_isready
```

---

## Best Practices

### General
1. **Isolate tests**: No shared state, use fixtures
2. **Mock externals**: Supabase Storage, ML APIs, email
3. **Test error cases**: Not just happy paths
4. **Fast tests**: Unit <1s, integration <10s, E2E <30s
5. **Descriptive names**: `test_create_extraction_with_valid_pdf()`

### AI/ML Specific
6. **Evaluate on labeled data**: 200-500 samples per document type
7. **Monitor cost**: Track cost/accuracy tradeoffs (exponential after 95%)
8. **Test feedback loops**: Corrections should improve future accuracy
9. **Performance matters**: OCR latency, inference time, throughput
10. **Semantic accuracy**: Math expressions must preserve meaning

### Frontend Specific
11. **Separate unit and E2E**: Vitest for logic, Playwright for workflows
12. **Co-locate unit tests**: Place tests next to source files
13. **Test user behavior**: Focus on what users experience, not implementation
14. **Extract testable utilities**: Separate pure functions from components
15. **Mock external dependencies**: Use `vi.mock()` for API calls and services
16. **Use Playwright naturally**: Don't over-mock PDF/canvas in E2E tests
17. **Test NFRs**: <1s load, <500ms navigation, <100ms LaTeX
18. **Visual regression**: Optional screenshots for annotations
19. **Error states**: LaTeX fallback, PDF load failures

---

## Continuous Improvement

### Feedback Loop
```python
# Collect corrections from review UI
correction = {
    "original": question.suggested_tags,
    "corrected": question.approved_tags,
    "reason": question.correction_reason,
}
store_correction(correction)  # For periodic retraining
```

### Monitoring
- **Accuracy drift**: Alert if performance degrades >5%
- **A/B testing**: Compare model versions (50/50 traffic split)
- **Cost tracking**: Monitor per-page processing costs

---

## Future Enhancements

### Phase 2: Advanced ML Tests (Q2 2026)
- Multi-subject tagging comparison
- Cross-lingual OCR (Mother Tongue)
- Diagram segmentation quality

### Phase 3: Load Testing (Q3 2026)
- 1000+ concurrent users (locust/k6)
- Celery stress test (100+ tasks/min)
- Database connection pool limits

### Phase 4: Security (Q3 2026)
- OWASP Top 10 testing
- Malicious PDF validation
- RLS policy enforcement

---

**For detailed test execution, see [development.md](../getting-started/development.md)**
