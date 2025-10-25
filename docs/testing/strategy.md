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
E2E (10%)        → Full extraction pipeline
Integration (20%) → API + ML + Database + Celery
ML Tests (30%)   → OCR accuracy, Tagging, Cost/Performance
Unit Tests (40%) → Business logic, CRUD, validation
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

### Framework
- **Playwright** for E2E (recommended for PDF/LaTeX in 2025)
- **Why Playwright**: "Everything just worked without complex mocking" (industry feedback)

### Test Structure
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

| Category | Time | Coverage | Examples |
|----------|------|----------|----------|
| Unit Tests | <1s | ≥90% | Model validation, CRUD, utils |
| ML Tests | <5s | ≥85% | OCR accuracy, tagging, cost |
| Integration | <10s | ≥80% | API+DB, Celery, ML pipeline |
| Performance | <2min | 100% NFRs | Latency, throughput benchmarks |
| E2E | <30s | 100% critical | Full user workflows |

---

## Running Tests

```bash
# Backend - all tests with coverage
docker compose exec backend bash scripts/test.sh

# Backend - specific category
pytest tests/ml/ -v                # ML pipeline tests
pytest tests/performance/ -v -m performance  # Performance tests
pytest tests/api/ -v               # API tests

# Frontend - E2E tests
cd frontend && npx playwright test
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
3. **test-frontend** - Playwright E2E (~8 min)
4. **test-docker-compose** - Smoke test (~4 min)

**CI Environment**:
- Database: **PostgreSQL 17 service container** (production parity)
- Redis: Docker Compose service (for Celery tests)
- Celery: Eager mode for unit tests
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
11. **Use Playwright naturally**: Don't over-mock PDF/canvas
12. **Test NFRs**: <1s load, <500ms navigation, <100ms LaTeX
13. **Visual regression**: Optional screenshots for annotations
14. **Error states**: LaTeX fallback, PDF load failures

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
