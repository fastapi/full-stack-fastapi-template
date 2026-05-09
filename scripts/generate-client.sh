#! /usr/bin/env bash

set -e
set -x

cd backend
# Provide safe defaults for CI where ../.env may be missing
export PROJECT_NAME=${PROJECT_NAME:-"full-stack-fastapi-template"}
export POSTGRES_SERVER=${POSTGRES_SERVER:-"localhost"}
export POSTGRES_USER=${POSTGRES_USER:-"postgres"}
export POSTGRES_DB=${POSTGRES_DB:-"app"}
export FIRST_SUPERUSER=${FIRST_SUPERUSER:-"admin@example.com"}
export FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD:-"changethis"}

uv run python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
mv openapi.json frontend/
bun run --filter frontend generate-client
bun run lint
