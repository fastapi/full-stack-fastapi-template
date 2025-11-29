#! /usr/bin/env bash

set -e
set -x

echo "Starting prestart script..."

# Let the DB start
echo "Waiting for database to be ready..."
python app/backend_pre_start.py || {
    echo "ERROR: Failed to connect to database"
    exit 1
}

# Run migrations
echo "Running database migrations..."
alembic upgrade head || {
    echo "ERROR: Database migrations failed"
    exit 1
}

# Create initial data in DB
echo "Creating initial data..."
python app/initial_data.py || {
    echo "ERROR: Failed to create initial data"
    exit 1
}

echo "Prestart script completed successfully!"
