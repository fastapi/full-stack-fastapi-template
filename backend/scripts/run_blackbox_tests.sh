#!/bin/bash
# Script to run blackbox tests with a real server and generate a report

set -e  # Exit on error

# Check if we are in the backend directory
if [[ ! -d ./app ]]; then
    echo "Error: This script must be run from the backend directory."
    exit 1
fi

# Create test reports directory if it doesn't exist
mkdir -p test-reports

# Function to check if the server is already running
check_server() {
    curl -s http://localhost:8000/docs > /dev/null
    return $?
}

# Variables for server management
SERVER_HOST="localhost"
SERVER_PORT="8000"
SERVER_PID=""
SERVER_LOG="test-reports/server.log"
STARTED_SERVER=false

# Function to start the server if it's not already running
start_server() {
    if check_server; then
        echo "✓ Server already running at http://${SERVER_HOST}:${SERVER_PORT}"
        return 0
    fi

    echo "Starting FastAPI server for tests..."
    python -m uvicorn app.main:app --host ${SERVER_HOST} --port ${SERVER_PORT} > $SERVER_LOG 2>&1 &
    SERVER_PID=$!
    STARTED_SERVER=true
    
    # Wait for the server to be ready
    MAX_RETRIES=30
    RETRY=0
    while [ $RETRY -lt $MAX_RETRIES ]; do
        if curl -s http://${SERVER_HOST}:${SERVER_PORT}/docs > /dev/null; then
            echo "✓ Server started successfully at http://${SERVER_HOST}:${SERVER_PORT}"
            # Give the server a bit more time to fully initialize
            sleep 1
            return 0
        fi
        
        echo "Waiting for server to start... ($RETRY/$MAX_RETRIES)"
        sleep 1
        RETRY=$((RETRY+1))
    done
    
    echo "✗ Failed to start server after $MAX_RETRIES attempts."
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    exit 1
}

# Function to stop the server if we started it
stop_server() {
    if [ "$STARTED_SERVER" = true ] && [ -n "$SERVER_PID" ]; then
        echo "Stopping FastAPI server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        echo "✓ Server stopped"
    else
        echo "ℹ Leaving external server running"
    fi
}

# Set up a trap to stop the server when the script exits
trap stop_server EXIT

# Start the server
start_server

# Export server URL for tests
export TEST_SERVER_URL="http://${SERVER_HOST}:${SERVER_PORT}"
export TEST_REQUEST_TIMEOUT=5.0  # Shorter timeout for tests

# Run the blackbox tests with the specified server
echo "Running blackbox tests against server at ${TEST_SERVER_URL}..."

# Basic tests first to verify infrastructure
echo "Running basic infrastructure tests..."
cd app/tests/api/blackbox
PYTHONPATH=../../../.. python -m pytest test_basic.py -v --no-header --junitxml=../../../../test-reports/blackbox-basic-results.xml

# If basic tests pass, run the complete test suite
if [ $? -eq 0 ]; then
    echo "Running all blackbox tests..."
    PYTHONPATH=../../../.. python -m pytest -v --no-header --junitxml=../../../../test-reports/blackbox-results.xml
fi

cd ../../../../

# Check the exit code
TEST_EXIT_CODE=$?
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All blackbox tests passed!"
else
    echo "❌ Some blackbox tests failed."
fi

# Generate HTML report if pytest-html is installed
if python -c "import pytest_html" &> /dev/null; then
    echo "Generating HTML report..."
    cd app/tests/api/blackbox
    PYTHONPATH=../../../.. TEST_SERVER_URL=${TEST_SERVER_URL} python -m pytest --no-header -v --html=../../../../test-reports/blackbox-report.html
    cd ../../../../
else
    echo "pytest-html not found. Install with 'uv add pytest-html' to generate HTML reports."
fi

echo "Blackbox tests completed. Results available in test-reports directory."
exit $TEST_EXIT_CODE