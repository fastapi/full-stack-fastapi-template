#!/bin/bash

# Test Runner Script - Ensures correct environment usage
# Usage: ./scripts/run-tests.sh [test-path]

set -e

echo "=== Lesmee Backend Test Runner ==="
echo "Date: $(date)"
echo

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: .venv directory not found!"
    echo "Please run: uv sync"
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from backend directory (where pyproject.toml is located)"
    exit 1
fi

# Verify httpx version in .venv
HTTPX_VERSION=$(.venv/bin/python -c "import httpx; print(httpx.__version__)")
echo "✅ Using httpx version: $HTTPX_VERSION"

# Check if httpx version is compatible
if [[ "$HTTPX_VERSION" == "0.28"* ]]; then
    echo "❌ Error: Incompatible httpx version $HTTPX_VERSION detected!"
    echo "This version is incompatible with FastAPI TestClient"
    echo "Please run: uv sync to fix dependencies"
    exit 1
fi

# Check FastAPI version
FASTAPI_VERSION=$(.venv/bin/python -c "import fastapi; print(fastapi.__version__)")
echo "✅ Using FastAPI version: $FASTAPI_VERSION"

echo
echo "🚀 Running tests with project environment..."

# Run tests with the specified path or default to all tests
if [ $# -eq 0 ]; then
    echo "Running all tests..."
    .venv/bin/python -m pytest tests/ -v
else
    echo "Running tests: $@"
    .venv/bin/python -m pytest "$@" -v
fi

echo
echo "✅ Tests completed!"