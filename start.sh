#!/bin/bash

set -e  # Exit on error

# Function to clean up background processes
cleanup() {
    echo "Stopping backend and frontend..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    echo "All services stopped."
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM (for graceful shutdown)
trap cleanup SIGINT SIGTERM

# Start Backend
cd backend || exit 1
source .venv/bin/activate
echo "Initializing database..."
python -c "from app.core.db import init_db; init_db()"
echo "Database initialization complete."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &  # Run in background
BACKEND_PID=$!  # Store backend PID
cd ..

# Start Frontend
cd frontend || exit 1
npm run dev -- --host=0.0.0.0 --port=5173 &  # Run in background
FRONTEND_PID=$!  # Store frontend PID
cd ..

# Display PIDs for reference
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

# Wait for both processes
wait "$BACKEND_PID" "$FRONTEND_PID"
