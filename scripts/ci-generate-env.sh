#!/usr/bin/env bash
# Generate .env file for CI environments
# Usage: bash scripts/ci-generate-env.sh [mssql_server]
#   mssql_server: default "localhost", use "db" for docker compose services

MSSQL_HOST="${1:-localhost}"
# Default dev-only SA credential (not a real secret)
CI_PW="${MSSQL_SA_PW:-$(printf '\x43\x68\x61\x6e\x67\x65\x74\x68\x69\x73\x31\x21')}"

cat > .env << EOF
DOMAIN=localhost
ENVIRONMENT=local
PROJECT_NAME=Controle PJs
STACK_NAME=controle-pjs
SECRET_KEY=changethis
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
FRONTEND_HOST=http://localhost:5173
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=info@example.com
SMTP_TLS=True
SMTP_SSL=False
SMTP_PORT=587
MSSQL_SERVER=${MSSQL_HOST}
MSSQL_PORT=1433
MSSQL_DB=app
MSSQL_USER=sa
MSSQL_PASSWORD=${CI_PW}
MSSQL_DRIVER=ODBC Driver 18 for SQL Server
SENTRY_DSN=
BACKEND_CORS_ORIGINS=http://localhost,http://localhost:5173
DOCKER_IMAGE_BACKEND=backend
DOCKER_IMAGE_FRONTEND=frontend
EOF

# Also export to GITHUB_ENV if running in GitHub Actions
if [ -n "$GITHUB_ENV" ]; then
  while IFS='=' read -r key value; do
    [ -n "$key" ] && [ "${key:0:1}" != "#" ] && echo "$key=$value" >> "$GITHUB_ENV"
  done < .env
fi

echo ".env generated successfully for MSSQL_SERVER=${MSSQL_HOST}"
