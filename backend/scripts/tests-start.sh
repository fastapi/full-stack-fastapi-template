#!/bin/bash

# Development test setup script for backend project
# This script starts necessary services for testing

set -e

echo "🚀 Starting development environment for testing..."

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ ERROR: Virtual environment not activated!"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ ERROR: uv is not installed!"
    echo "Please install uv: pip install uv"
    exit 1
fi

echo "✅ Environment checks passed"

# Sync dependencies if needed
echo "📦 Syncing dependencies..."
uv sync

# Validate critical versions
echo "🔍 Validating critical dependency versions..."

# Check httpx version
HTTPX_VERSION=$(uv run python -c "import httpx; print(httpx.__version__)" 2>/dev/null || echo "not installed")
if [[ "$HTTPX_VERSION" == "0.24.1" ]]; then
    echo "✅ httpx version: $HTTPX_VERSION (correct)"
else
    echo "❌ httpx version: $HTTPX_VERSION (expected: 0.24.1)"
    echo "Please run: uv sync"
    exit 1
fi

# Check fastapi version
FASTAPI_VERSION=$(uv run python -c "import fastapi; print(fastapi.__version__)" 2>/dev/null || echo "not installed")
if [[ "$FASTAPI_VERSION" == "0.109.2" ]]; then
    echo "✅ fastapi version: $FASTAPI_VERSION (correct)"
else
    echo "❌ fastapi version: $FASTAPI_VERSION (expected: 0.109.2)"
    echo "Please run: uv sync"
    exit 1
fi

# Run pre-start script if it exists
if [[ -f "app/tests_pre_start.py" ]]; then
    echo "🔧 Running test pre-start script..."
    python app/tests_pre_start.py
fi

echo "✅ All validations passed!"
echo "🎯 Development environment ready for testing!"
echo ""
echo "Usage:"
echo "  ./scripts/run-tests.sh                    # Run all tests"
echo "  ./scripts/run-tests.sh test_file.py       # Run specific test"
echo "  ./scripts/run-tests.sh -v                 # Verbose output"
