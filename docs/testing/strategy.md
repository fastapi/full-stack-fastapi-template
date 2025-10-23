# Testing Strategy

**CurriculumExtractor Testing Approach**

## Testing Philosophy

- **Test-Driven Development (TDD)**: Write tests before implementation
- **Comprehensive Coverage**: ≥80% for backend, critical paths for frontend
- **Fast Feedback**: Unit tests run quickly, integration tests as needed
- **Database Agnostic**: Tests work with SQLite (CI) and PostgreSQL (local)
- **Mock External Services**: Supabase Storage, ML APIs, email
- **Celery Testing**: Sync execution in tests (`CELERY_TASK_ALWAYS_EAGER=True`)

## Backend Testing

### Framework
- **Pytest** for test execution
- **FastAPI TestClient** for API testing
- **SQLModel** with SQLite (CI) or PostgreSQL (local)
- **pytest-cov** for coverage reporting
- **unittest.mock** for mocking external services

### Test Structure

```
backend/tests/
├── conftest.py          # Shared fixtures
├── api/
│   └── routes/          # API endpoint tests (mirrors app/api/routes/)
├── crud/                # CRUD operation tests
├── utils/               # Test utilities
└── scripts/             # Script tests
```

### Test Naming
- Files: `test_*.py`
- Functions: `test_[action]_[condition]()`

Example:
```python
def test_get_users_superuser_me(
    client: TestClient,
    superuser_token_headers: dict[str, str]
) -> None:
    # Test implementation
```

### Key Fixtures

Defined in `conftest.py`:
- `client`: TestClient instance (FastAPI)
- `db`: Test database session (SQLite or PostgreSQL)
- `superuser_token_headers`: Admin JWT auth headers
- `normal_user_token_headers`: Regular user auth headers
- `test_user`: Factory for creating test users
- `test_extraction`: Factory for creating test extractions (future)

### Test Database Configuration

**Local Development**:
```python
# Uses Supabase PostgreSQL (same as development)
DATABASE_URL=postgresql+psycopg://postgres.wijzypbstiigssjuiuvh:***@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

**CI/GitHub Actions**:
```python
# Uses SQLite for fast, isolated tests
DATABASE_URL=sqlite:///./test.db
```

**Test Isolation**:
- Each test runs in a transaction
- Rollback after each test (no data persists)
- Database state reset between tests

### Running Tests

```bash
# All tests with coverage
bash backend/scripts/test.sh

# In running stack
docker compose exec backend bash scripts/tests-start.sh

# Specific file
docker compose exec backend bash scripts/tests-start.sh tests/api/test_users.py

# Stop on first failure
docker compose exec backend bash scripts/tests-start.sh -x

# With pytest directly
cd backend
pytest tests/api/test_users.py::test_create_user_new_email
```

### Coverage Requirements

- Coverage report generated in `htmlcov/index.html`
- Target: High coverage for `app/` directory
- All CRUD operations must have tests
- All API endpoints must have tests

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

# Mock email sending
def test_create_user_new_email(client, superuser_token_headers, db):
    with patch("app.utils.send_email", return_value=None):
        # Test implementation without sending real emails
        ...

# Mock Supabase Storage
def test_upload_pdf(client, superuser_token_headers):
    with patch("app.api.routes.extractions.supabase.storage") as mock_storage:
        mock_storage.from_().upload.return_value = {"path": "test.pdf"}
        # Test PDF upload without hitting Supabase
        ...

# Mock Celery tasks (run synchronously)
from app.core.config import settings
settings.CELERY_TASK_ALWAYS_EAGER = True  # In conftest.py

def test_process_extraction(client, superuser_token_headers):
    # Task runs immediately in the same process
    response = client.post("/api/v1/extractions/123/process")
    # Task result available immediately
    ...
```

### Testing Celery Tasks

**Option 1: Eager Mode (Recommended for CI)**
```python
# In conftest.py or test file
from app.worker import celery_app

celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
)

# Tasks run synchronously in tests
def test_health_check_task():
    from app.tasks.default import health_check_task
    result = health_check_task.delay()  # Runs immediately
    assert result.result["status"] == "healthy"
```

**Option 2: Real Worker (Integration Tests)**
```python
# Requires Redis running
def test_pdf_extraction_integration():
    from app.tasks.extraction import process_pdf_task
    
    # Queue real task
    task = process_pdf_task.delay("extraction-id")
    
    # Wait for result
    result = task.get(timeout=30)
    assert result["status"] == "completed"
```

## Frontend Testing

### Framework
- **Playwright** for E2E tests
- **TypeScript** for type safety

### Test Structure

```
frontend/tests/
├── login.spec.ts
├── sign-up.spec.ts
├── user-settings.spec.ts
└── reset-password.spec.ts
```

### Test Naming
- Files: `*.spec.ts`
- Tests: Descriptive scenarios

### Running E2E Tests

```bash
# Ensure backend is running
docker compose up -d --wait backend

# Run tests
cd frontend
npx playwright test

# Interactive mode
npx playwright test --ui

# Specific test
npx playwright test login.spec.ts

# Cleanup
docker compose down -v
```

### E2E Test Patterns

```typescript
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('http://localhost:5173/login')
  await page.fill('input[name="email"]', 'user@example.com')
  await page.fill('input[name="password"]', 'password')
  await page.click('button[type="submit"]')

  await expect(page).toHaveURL('/items')
})
```

---

## Testing Celery Tasks

### Test Strategy

**Unit Tests**: Eager mode (synchronous)
```python
# conftest.py
from app.worker import celery_app

@pytest.fixture(autouse=True)
def celery_eager_mode():
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
```

**Integration Tests**: Real worker
```python
def test_extraction_pipeline_integration():
    # Requires: docker compose up -d redis celery-worker
    from app.tasks.extraction import process_pdf_task
    
    task = process_pdf_task.delay("test-extraction-id")
    result = task.get(timeout=60)
    
    assert result["status"] == "completed"
```

### Task Test Structure

```
backend/tests/tasks/
├── test_default.py          # health_check, test_task
├── test_extraction.py       # process_pdf_task
└── conftest.py              # Celery fixtures
```

---

## Testing with Supabase

### Mocking Supabase Client

```python
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_supabase():
    with patch("app.api.routes.extractions.create_client") as mock:
        # Mock storage operations
        mock_client = MagicMock()
        mock_client.storage.from_().upload.return_value = {
            "path": "test/file.pdf"
        }
        mock_client.storage.from_().create_signed_url.return_value = {
            "signedURL": "https://test.supabase.co/storage/..."
        }
        mock.return_value = mock_client
        yield mock_client

def test_upload_pdf(client, mock_supabase, superuser_token_headers):
    # Test uploads without hitting real Supabase Storage
    response = client.post(
        "/api/v1/extractions/",
        files={"file": ("test.pdf", b"PDF content")},
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    mock_supabase.storage.from_().upload.assert_called_once()
```

### Using Supabase MCP for Test Data

```python
# Setup test data via MCP (one-time)
mcp_supabase_execute_sql(
    project_id="wijzypbstiigssjuiuvh",
    query="""
    INSERT INTO users (email, hashed_password, is_superuser)
    VALUES ('test@example.com', 'hashed', false);
    """
)

# Cleanup after tests
mcp_supabase_execute_sql(
    project_id="wijzypbstiigssjuiuvh",
    query="DELETE FROM users WHERE email LIKE 'test%';"
)
```

---

## Testing Workflow

### TDD Cycle

1. **Write failing test** that defines expected behavior
2. **Implement minimum code** to pass the test
3. **Run tests** with `pytest` or `playwright test`
4. **Verify test passes** (green)
5. **Refactor** while keeping tests green
6. **Add edge case tests** as discovered
7. **Check coverage** - aim for ≥80%

### Example: Adding Extraction Model

```bash
# 1. Write test first
# backend/tests/api/routes/test_extractions.py
def test_create_extraction(client, superuser_token_headers):
    response = client.post(
        "/api/v1/extractions/",
        json={"filename": "test.pdf"},
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "DRAFT"

# 2. Run test (should fail)
pytest tests/api/routes/test_extractions.py::test_create_extraction

# 3. Implement model, route, CRUD
# backend/app/models.py, app/api/routes/extractions.py, app/crud.py

# 4. Run test again (should pass)
pytest tests/api/routes/test_extractions.py::test_create_extraction

# 5. Add more tests, refactor
```

---

## CI/CD Testing

### GitHub Actions Workflows

**On every push/PR, runs**:
1. **lint-backend.yml** - Ruff + mypy (~1 min)
2. **test-backend.yml** - Pytest with coverage (~4 min)
3. **test-docker-compose.yml** - Smoke test (~4 min)
4. **test-frontend.yml** - Playwright E2E (~8 min)
5. **generate-client.yml** - TypeScript client (~2 min)

**Test Environment (CI)**:
```yaml
DATABASE_URL: sqlite:///./test.db  # Fast, isolated
REDIS_URL: redis://:test@redis:6379/0  # Real Redis
CELERY_BROKER_URL: redis://:test@redis:6379/0
# Mock Supabase values
SUPABASE_URL: https://test.supabase.co
```

### Coverage Requirements

- **Target**: ≥80% coverage for `app/` directory
- **Critical paths**: 100% coverage
  - Authentication (login, token validation)
  - User management (CRUD operations)
  - Extraction lifecycle (upload, process, approve)
- **Generated files**: Excluded from coverage (client/, migrations/)

**View coverage report**:
```bash
cd backend
uv run bash scripts/test.sh
open htmlcov/index.html
```

---

## Test Data Management

### Backend Test Data

**SQLite (CI)**:
- In-memory database
- Fresh for each test
- Fast (<100ms per test)

**PostgreSQL (Local)**:
- Uses Supabase test database (optional)
- Transaction rollback after each test
- Isolated from development data

### Frontend Test Data

```typescript
// tests/utils/user.ts
export async function createTestUser() {
  const email = `test-${Date.now()}@example.com`
  const password = 'test-password-123'
  
  await api.post('/api/v1/users/signup', {
    email,
    password,
    full_name: 'Test User'
  })
  
  return { email, password }
}

// Cleanup after test
test.afterEach(async () => {
  // Delete test users created during test
})
```

---

## Best Practices

### General
1. **Isolate tests**: Each test independent, no shared state
2. **Use fixtures**: Share setup logic via pytest fixtures
3. **Mock external services**: Supabase Storage, ML APIs, email
4. **Test error cases**: Not just happy paths
5. **Keep tests fast**: Unit tests <1s each, E2E <10s each
6. **Descriptive names**: `test_create_extraction_with_valid_pdf()`

### Backend-Specific
7. **Use SessionDep**: Leverage dependency injection in tests
8. **Test with both databases**: SQLite (fast) and PostgreSQL (accuracy)
9. **Mock Celery in unit tests**: Use eager mode for sync execution
10. **Test Celery in integration**: Use real worker for pipeline tests

### Frontend-Specific
11. **Wait for API responses**: Use Playwright's auto-waiting
12. **Test authentication flows**: Login, logout, token refresh
13. **Mock slow operations**: PDF rendering, large file uploads
14. **Test responsive design**: Different viewport sizes

### Celery-Specific
15. **Eager mode for unit tests**: Fast, synchronous execution
16. **Real worker for integration**: Test full async pipeline
17. **Test retries**: Simulate failures and retry logic
18. **Monitor task queue**: Ensure tasks don't pile up in tests

---

## Coverage Reporting

### Running with Coverage

```bash
# Backend
cd backend
uv run bash scripts/test.sh

# Generates:
# - Terminal report (shows % coverage)
# - htmlcov/index.html (interactive HTML report)
# - .coverage (data file for CI)

# View HTML report
open htmlcov/index.html
```

### Coverage in CI

GitHub Actions uploads coverage as artifact:
```yaml
- name: Store coverage files
  uses: actions/upload-artifact@v4
  with:
    name: coverage-html
    path: backend/htmlcov
```

**Download from**:
- Actions tab → Workflow run → Artifacts → coverage-html

---

## Testing Workflow

For detailed test execution commands, see [../getting-started/development.md](../getting-started/development.md)

### Quick Commands

```bash
# Backend - all tests
docker compose exec backend bash scripts/test.sh

# Backend - specific file
docker compose exec backend pytest tests/api/routes/test_users.py -v

# Backend - with logs
docker compose exec backend pytest -s

# Frontend - all tests
cd frontend && npx playwright test

# Frontend - specific test
npx playwright test login.spec.ts

# Frontend - UI mode
npx playwright test --ui
```

---

## Test Categories

### Unit Tests (Fast - <1s each)
- Model validation
- CRUD operations
- Utility functions
- Task logic (eager mode)

### Integration Tests (Medium - <10s each)
- API endpoints with database
- Authentication flows
- Celery tasks with real worker
- File upload/download

### E2E Tests (Slow - <30s each)
- Complete user workflows
- PDF upload → extraction → review
- Multi-page navigation
- Form submissions

---

## Future Testing Enhancements

### Phase 2: ML Pipeline Tests
- [ ] OCR accuracy tests (PaddleOCR)
- [ ] Segmentation quality tests (docTR)
- [ ] Tagging accuracy tests (DeBERTa-v3)
- [ ] End-to-end extraction pipeline test

### Phase 3: Performance Tests
- [ ] Load testing (locust/k6)
- [ ] Database query performance
- [ ] Celery throughput testing
- [ ] PDF rendering performance

### Phase 4: Security Tests
- [ ] Authentication bypass attempts
- [ ] SQL injection tests
- [ ] File upload validation (malicious PDFs)
- [ ] Rate limiting tests

---

**For test execution and debugging, see [development.md](../getting-started/development.md)**
