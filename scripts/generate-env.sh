#!/usr/bin/env bash
# Generate a local `.env` file with strong, random secrets.
#
# `.env` is ignored by Git and Docker and must never be committed. This script
# creates it (or refreshes only the missing secret values) so local development
# and CI can start the stack without shipping a known signing key.
#
# Usage:
#   bash scripts/generate-env.sh          # create .env if missing
#   FORCE=1 bash scripts/generate-env.sh  # overwrite an existing .env
set -e

cd "$(dirname "$0")/.."

ENV_FILE=".env"
EXAMPLE_FILE=".env.example"

gen() { python3 -c 'import secrets; print(secrets.token_urlsafe(32))'; }

if [ -f "$ENV_FILE" ] && [ -z "${FORCE:-}" ]; then
    echo "$ENV_FILE already exists; leaving it untouched. Use FORCE=1 to overwrite."
    exit 0
fi

if [ ! -f "$EXAMPLE_FILE" ]; then
    echo "Missing $EXAMPLE_FILE; cannot generate $ENV_FILE." >&2
    exit 1
fi

SECRET_KEY="$(gen)"
FIRST_SUPERUSER_PASSWORD="$(gen)"
POSTGRES_PASSWORD="$(gen)"

# Start from the example and fill in the generated secrets.
sed \
    -e "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" \
    -e "s|^FIRST_SUPERUSER_PASSWORD=.*|FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}|" \
    -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|" \
    "$EXAMPLE_FILE" > "$ENV_FILE"

echo "Wrote $ENV_FILE with freshly generated secrets."
