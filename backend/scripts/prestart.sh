#! /usr/bin/env bash

set -e
set -x

# Run migrations
# alembic upgrade head
# as we are not migrating at all

# Create initial data in DB
python app/initial_data.py
