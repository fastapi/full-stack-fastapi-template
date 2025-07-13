#! /usr/bin/env bash

set -e
set -x

# Let the DB start and retry for up to 60 seconds
max_retries=30
counter=0
until python app/backend_pre_start.py || [ $counter -eq $max_retries ]
do
   echo "Waiting for database to be ready... ($counter/$max_retries)"
   sleep 2
   counter=$((counter+1))
done

if [ $counter -eq $max_retries ]; then
    echo "Database connection failed after $max_retries retries"
    exit 1
fi

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py
