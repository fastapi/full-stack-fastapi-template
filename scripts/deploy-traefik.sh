#!/bin/bash

# Deployment script for FastAPI project with Traefik
# Usage: ./scripts/deploy-traefik.sh
# This script uses environment variables that should be set by GitHub Actions or manually

set -e  # Exit on error

echo "Starting Traefik-based deployment..."

# Check if traefik-public network exists, create if not
if ! docker network ls | grep -q traefik-public; then
    echo "Creating traefik-public network..."
    docker network create traefik-public
else
    echo "traefik-public network already exists"
fi

# Validate required environment variables
required_vars=(
    "DOMAIN"
    "ENVIRONMENT"
    "STACK_NAME"
    "SECRET_KEY"
    "FIRST_SUPERUSER"
    "FIRST_SUPERUSER_PASSWORD"
    "POSTGRES_PASSWORD"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Set defaults for optional variables
PROJECT_NAME=${PROJECT_NAME:-"Mosaic Project"}
BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS:-"https://dashboard.${DOMAIN},https://api.${DOMAIN}"}
FRONTEND_HOST=${FRONTEND_HOST:-"https://dashboard.${DOMAIN}"}
POSTGRES_SERVER=${POSTGRES_SERVER:-"db"}
POSTGRES_PORT=${POSTGRES_PORT:-"5432"}
POSTGRES_USER=${POSTGRES_USER:-"postgres"}
POSTGRES_DB=${POSTGRES_DB:-"app"}
SMTP_HOST=${SMTP_HOST:-""}
SMTP_USER=${SMTP_USER:-""}
SMTP_PASSWORD=${SMTP_PASSWORD:-""}
EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL:-""}
SENTRY_DSN=${SENTRY_DSN:-""}
DOCKER_IMAGE_BACKEND=${DOCKER_IMAGE_BACKEND:-"mosaic-backend"}
DOCKER_IMAGE_FRONTEND=${DOCKER_IMAGE_FRONTEND:-"mosaic-frontend"}
TAG=${TAG:-"latest"}

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
# Production Environment Variables for Traefik deployment
ENVIRONMENT=${ENVIRONMENT}
DOMAIN=${DOMAIN}
PROJECT_NAME=${PROJECT_NAME}
STACK_NAME=${STACK_NAME}
BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
FRONTEND_HOST=${FRONTEND_HOST}
SECRET_KEY=${SECRET_KEY}
FIRST_SUPERUSER=${FIRST_SUPERUSER}
FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}
SMTP_HOST=${SMTP_HOST}
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL}
POSTGRES_SERVER=${POSTGRES_SERVER}
POSTGRES_PORT=${POSTGRES_PORT}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
SENTRY_DSN=${SENTRY_DSN}
DOCKER_IMAGE_BACKEND=${DOCKER_IMAGE_BACKEND}
DOCKER_IMAGE_FRONTEND=${DOCKER_IMAGE_FRONTEND}
TAG=${TAG}
EOF

echo ".env file created successfully"

# Export environment variables for docker-compose
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Stop existing services
echo "Stopping existing services..."
docker compose -f docker-compose.yml --project-name "${STACK_NAME}" down || true

# Build and start services
echo "Building and starting services..."
docker compose -f docker-compose.yml --project-name "${STACK_NAME}" build
docker compose -f docker-compose.yml --project-name "${STACK_NAME}" up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check service status
echo "Service status:"
docker compose -f docker-compose.yml --project-name "${STACK_NAME}" ps

# Health check
echo "Performing health check..."
if docker compose -f docker-compose.yml --project-name "${STACK_NAME}" exec -T backend curl -f http://localhost:8000/api/v1/utils/health-check/ 2>/dev/null; then
    echo "✅ Backend health check passed"
else
    echo "⚠️  Backend health check failed (service may still be starting)"
fi

echo ""
echo "Deployment complete!"
echo ""
echo "Your application should be available at:"
echo "- Frontend: https://dashboard.${DOMAIN}"
echo "- Backend API: https://api.${DOMAIN}"
echo "- API Docs: https://api.${DOMAIN}/docs"
echo "- Adminer: https://adminer.${DOMAIN}"

