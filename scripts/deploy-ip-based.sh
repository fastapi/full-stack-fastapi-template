#!/bin/bash

# Deployment script for FastAPI project with IP-based deployment (no Traefik)
# Usage: ./scripts/deploy-ip-based.sh [EC2_IP]
# If EC2_IP is not provided, it will try to detect it automatically

set -e  # Exit on error

echo "Starting IP-based deployment..."

# Get EC2 IP - either from argument or auto-detect
if [ -z "$1" ]; then
    echo "No IP provided, attempting to auto-detect..."
    EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")
    if [ -z "$EC2_IP" ]; then
        echo "Error: Could not auto-detect EC2 IP. Please provide it as an argument."
        echo "Usage: ./scripts/deploy-ip-based.sh YOUR_EC2_IP"
        exit 1
    fi
    echo "Auto-detected IP: $EC2_IP"
else
    EC2_IP=$1
    echo "Using provided IP: $EC2_IP"
fi

# Validate required environment variables
required_vars=(
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
BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS:-"http://${EC2_IP}:80,http://${EC2_IP}"}
FRONTEND_HOST=${FRONTEND_HOST:-"http://${EC2_IP}"}
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
# Production Environment Variables for IP-based deployment
ENVIRONMENT=${ENVIRONMENT}
DOMAIN=${EC2_IP}
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

# Create docker-compose.production.yml
echo "Creating docker-compose.production.yml..."
cat > docker-compose.production.yml << 'COMPOSEEOF'
services:
  db:
    image: postgres:17
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s
    volumes:
      - app-db-data:/var/lib/postgresql/data/pgdata
    environment:
      - PGDATA=/var/lib/postgresql/data/pgdata
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "5432:5432"

  adminer:
    image: adminer
    restart: always
    depends_on:
      - db
    environment:
      - ADMINER_DESIGN=pepa-linha-dark
    ports:
      - "8080:8080"

  prestart:
    image: ${DOCKER_IMAGE_BACKEND}:${TAG}
    build:
      context: ./backend
    depends_on:
      db:
        condition: service_healthy
        restart: true
    command: bash scripts/prestart.sh
    environment:
      - PROJECT_NAME=${PROJECT_NAME}
      - DOMAIN=${DOMAIN}
      - FRONTEND_HOST=${FRONTEND_HOST}
      - ENVIRONMENT=${ENVIRONMENT}
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - SECRET_KEY=${SECRET_KEY}
      - FIRST_SUPERUSER=${FIRST_SUPERUSER}
      - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL}
      - POSTGRES_SERVER=db
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

  backend:
    image: ${DOCKER_IMAGE_BACKEND}:${TAG}
    restart: always
    depends_on:
      db:
        condition: service_healthy
        restart: true
      prestart:
        condition: service_completed_successfully
    build:
      context: ./backend
    command: fastapi run --workers 4 app/main.py
    volumes:
      - ./backend/app_data:/app/app_data
    environment:
      - PROJECT_NAME=${PROJECT_NAME}
      - DOMAIN=${DOMAIN}
      - FRONTEND_HOST=${FRONTEND_HOST}
      - ENVIRONMENT=${ENVIRONMENT}
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - SECRET_KEY=${SECRET_KEY}
      - FIRST_SUPERUSER=${FIRST_SUPERUSER}
      - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL}
      - POSTGRES_SERVER=db
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - SENTRY_DSN=${SENTRY_DSN}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - "8000:8000"

  frontend:
    image: ${DOCKER_IMAGE_FRONTEND}:${TAG}
    restart: always
    build:
      context: ./frontend
      args:
        - VITE_API_URL=http://EC2_IP_PLACEHOLDER:8000
        - NODE_ENV=production
    ports:
      - "80:80"

volumes:
  app-db-data:
COMPOSEEOF

# Replace EC2_IP_PLACEHOLDER in the frontend build args
sed -i "s/EC2_IP_PLACEHOLDER/${EC2_IP}/g" docker-compose.production.yml

echo "docker-compose.production.yml created successfully"

# Export environment variables for docker-compose
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Stop existing services
echo "Stopping existing services..."
docker compose -f docker-compose.production.yml --project-name "${STACK_NAME}" down || true

# Build and start services
echo "Building and starting services..."
docker compose -f docker-compose.production.yml --project-name "${STACK_NAME}" build
docker compose -f docker-compose.production.yml --project-name "${STACK_NAME}" up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check service status
echo "Service status:"
docker compose -f docker-compose.production.yml --project-name "${STACK_NAME}" ps

# Health check
echo "Performing health check..."
if curl -f http://localhost:8000/api/v1/utils/health-check/ 2>/dev/null; then
    echo "✅ Backend health check passed"
else
    echo "⚠️  Backend health check failed (service may still be starting)"
fi

echo ""
echo "Deployment complete!"
echo ""
echo "Your application should be available at:"
echo "- Frontend: http://${EC2_IP}"
echo "- Backend API: http://${EC2_IP}:8000"
echo "- API Docs: http://${EC2_IP}:8000/docs"
echo "- Adminer: http://${EC2_IP}:8080"

