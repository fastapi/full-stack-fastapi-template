# Development Guide - Lesmee Backend

## Environment Setup

### Prerequisites
- Python 3.11+
- uv package manager

### Setup
```bash
# Clone and navigate to backend directory
cd backend

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

## Running Tests

### IMPORTANT: Environment Issue Fixed
We discovered a critical issue where tests fail when run with global Python (httpx 0.28+) instead of project environment (httpx 0.24.1).

### Correct ways to run tests

1. **Recommended: Use test script**
   ```bash
   ./scripts/run-tests.sh
   ```

2. **Explicit venv usage**
   ```bash
   .venv/bin/python -m pytest tests/
   ```

3. **Activate environment first**
   ```bash
   source .venv/bin/activate
   pytest tests/
   ```

### What NOT to do
```bash
# ❌ DON'T - Uses global Python with incompatible httpx
python -m pytest tests/
pytest tests/
```

## IDE Configuration

### VSCode
- `.vscode/settings.json` is configured to use project interpreter
- Ensure VSCode Python extension is installed
- Reload VSCode after settings change

### PyCharm
- Settings → Project → Python Interpreter
- Select: `/path/to/backend/.venv/bin/python`

## Verification

Check environment before running tests:
```bash
.venv/bin/python -c "import httpx; print(f'httpx: {httpx.__version__}')"
# Should output: httpx: 0.24.1
```

## Troubleshooting

### Tests fail with "TypeError: Client.__init__() got an unexpected keyword argument 'app'"
**Cause**: Running tests with global Python (httpx 0.28+) instead of project environment (httpx 0.24.1)

**Solution**:
```bash
# Fix dependencies
uv sync

# Use correct test command
./scripts/run-tests.sh
```

### httpx version conflict
```bash
# Check versions
.venv/bin/python -c "import httpx; print(httpx.__version__)"  # Should be 0.24.1
python -c "import httpx; print(httpx.__version__)"           # Might be 0.28.x

# Fix: Use project environment
source .venv/bin/activate
```

## Development Workflow

1. Always activate virtual environment before development
2. Use `./scripts/run-tests.sh` for running tests
3. Commit changes from project environment
4. Never use global Python for this project

## API Test Coverage

Current test status:
- ✅ TestClient working (httpx 0.24.1)
- ❌ Authentication fixture needs fixing (separate issue)
- 68+ API route tests ready to run

## Root Cause Analysis

See detailed report: `plans/251119-from-system-to-dev-testclient-typerror-report.md`

**Summary**: httpx 0.28.0+ removed `app` parameter, breaking FastAPI TestClient. Project correctly uses httpx 0.24.1, but environment switching causes failures.