#!/bin/bash

# Deployment script for FastAPI project on EC2 with IP address
# Usage: ./deploy-ip.sh YOUR_EC2_IP

if [ -z "$1" ]; then
    echo "Usage: ./deploy-ip.sh YOUR_EC2_IP"
    echo "Example: ./deploy-ip.sh 54.123.45.67"
    exit 1
fi

EC2_IP=$1

echo "Deploying to EC2 IP: $EC2_IP"

# Create environment file
cat > .env << EOF
# Production Environment Variables for IP-based deployment
ENVIRONMENT=production
DOMAIN=$EC2_IP
PROJECT_NAME=Mosaic Project
STACK_NAME=mosaic-project-production
BACKEND_CORS_ORIGINS=http://$EC2_IP:5173,http://$EC2_IP:80,http://$EC2_IP
FRONTEND_HOST=http://$EC2_IP:5173
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
POSTGRES_DB=app
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=
DOCKER_IMAGE_BACKEND=mosaic-backend
DOCKER_IMAGE_FRONTEND=mosaic-frontend
TAG=latest
EOF

echo "Environment file created with secure random keys"

# Create simplified docker-compose for IP deployment
cat > docker-compose.production.yml << EOF
services:
  db:
    image: postgres:17
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER} -d \${POSTGRES_DB}"]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s
    volumes:
      - app-db-data:/var/lib/postgresql/data/pgdata
    environment:
      - PGDATA=/var/lib/postgresql/data/pgdata
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
      - POSTGRES_USER=\${POSTGRES_USER}
      - POSTGRES_DB=\${POSTGRES_DB}
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
    image: \${DOCKER_IMAGE_BACKEND}:\${TAG}
    build:
      context: ./backend
    depends_on:
      db:
        condition: service_healthy
        restart: true
    command: bash scripts/prestart.sh
    environment:
      - DOMAIN=\${DOMAIN}
      - FRONTEND_HOST=\${FRONTEND_HOST}
      - ENVIRONMENT=\${ENVIRONMENT}
      - BACKEND_CORS_ORIGINS=\${BACKEND_CORS_ORIGINS}
      - SECRET_KEY=\${SECRET_KEY}
      - FIRST_SUPERUSER=\${FIRST_SUPERUSER}
      - FIRST_SUPERUSER_PASSWORD=\${FIRST_SUPERUSER_PASSWORD}
      - SMTP_HOST=\${SMTP_HOST}
      - SMTP_USER=\${SMTP_USER}
      - SMTP_PASSWORD=\${SMTP_PASSWORD}
      - EMAILS_FROM_EMAIL=\${EMAILS_FROM_EMAIL}
      - POSTGRES_SERVER=db
      - POSTGRES_PORT=\${POSTGRES_PORT}
      - POSTGRES_DB=\${POSTGRES_DB}
      - POSTGRES_USER=\${POSTGRES_USER}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}

  backend:
    image: \${DOCKER_IMAGE_BACKEND}:\${TAG}
    restart: always
    depends_on:
      db:
        condition: service_healthy
        restart: true
      prestart:
        condition: service_completed_successfully
    build:
      context: ./backend
    environment:
      - DOMAIN=\${DOMAIN}
      - FRONTEND_HOST=\${FRONTEND_HOST}
      - ENVIRONMENT=\${ENVIRONMENT}
      - BACKEND_CORS_ORIGINS=\${BACKEND_CORS_ORIGINS}
      - SECRET_KEY=\${SECRET_KEY}
      - FIRST_SUPERUSER=\${FIRST_SUPERUSER}
      - FIRST_SUPERUSER_PASSWORD=\${FIRST_SUPERUSER_PASSWORD}
      - SMTP_HOST=\${SMTP_HOST}
      - SMTP_USER=\${SMTP_USER}
      - SMTP_PASSWORD=\${SMTP_PASSWORD}
      - EMAILS_FROM_EMAIL=\${EMAILS_FROM_EMAIL}
      - POSTGRES_SERVER=db
      - POSTGRES_PORT=\${POSTGRES_PORT}
      - POSTGRES_DB=\${POSTGRES_DB}
      - POSTGRES_USER=\${POSTGRES_USER}
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - "8000:8000"

  frontend:
    image: \${DOCKER_IMAGE_FRONTEND}:\${TAG}
    restart: always
    build:
      context: ./frontend
      args:
        - VITE_API_URL=http://$EC2_IP:8000
        - NODE_ENV=production
    ports:
      - "80:80"

volumes:
  app-db-data:
EOF

echo "Production docker-compose file created"

echo "Deployment files created successfully!"
echo ""
echo "Next steps:"
echo "1. Copy your project files to the EC2 instance"
echo "2. Run: docker compose -f docker-compose.production.yml up -d"
echo ""
echo "Your application will be available at:"
echo "- Frontend: http://$EC2_IP"
echo "- Backend API: http://$EC2_IP:8000"
echo "- API Docs: http://$EC2_IP:8000/docs"
echo "- Adminer: http://$EC2_IP:8080"
