# GENIUS INDUSTRIES - Dockerfile Autocontenido para Dokploy
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

# Configurar variables de entorno para el build
ENV VITE_API_URL=https://api.geniusindustries.org
ENV VITE_API_BASE_URL=https://api.geniusindustries.org  
ENV VITE_FRONTEND_URL=https://geniusindustries.org
ENV VITE_BACKEND_URL=https://api.geniusindustries.org
ENV VITE_ENV=production
ENV NODE_ENV=production
ENV VITE_CLERK_PUBLISHABLE_KEY=pk_test_Y3V0ZS1yYXR0bGVyLTU5LmNsZXJrLmFjY291bnRzLmRldiQ

COPY frontend/ ./
RUN npm run build

# Backend con UV
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-15 \
    postgresql-client-15 \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Configurar PostgreSQL
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER genius WITH SUPERUSER PASSWORD 'KhloeMF0911\$';" && \
    createdb -O genius genius_dev
USER root

# Configurar backend con UV
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-cache

# Copiar el código del backend
COPY backend/app ./app

# Variables de entorno del backend
ENV DATABASE_URL="postgresql://genius:KhloeMF0911\$@localhost:5432/genius_dev"
ENV POSTGRES_SERVER="localhost"
ENV POSTGRES_PORT="5432" 
ENV POSTGRES_DB="genius_dev"
ENV POSTGRES_USER="genius"
ENV POSTGRES_PASSWORD="KhloeMF0911\$"
ENV ENVIRONMENT="production"
ENV BACKEND_CORS_ORIGINS="https://geniusindustries.org"

# Copiar frontend build
COPY --from=frontend-builder /app/dist /var/www/html

# Configurar Nginx directamente
RUN echo 'server { listen 80; server_name _; root /var/www/html; index index.html; location / { try_files $uri $uri/ /index.html; } location /api/ { proxy_pass http://localhost:8000; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; } }' > /etc/nginx/sites-available/default

# Configurar Supervisor directamente con UV
RUN echo -e '[supervisord]\nnodaemon=true\n\n[program:postgresql]\ncommand=/usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/15/main\nuser=postgres\nautostart=true\nautorestart=true\n\n[program:nginx]\ncommand=/usr/sbin/nginx -g "daemon off;"\nautostart=true\nautorestart=true\n\n[program:fastapi]\ncommand=uv run uvicorn app.main:app --host 0.0.0.0 --port 8000\ndirectory=/app\nautostart=true\nautorestart=true' > /etc/supervisor/conf.d/supervisord.conf

# Script de inicio directo
RUN echo -e '#!/bin/bash\nset -e\nservice postgresql start\nuntil pg_isready -h localhost -p 5432 -U postgres; do\n  sleep 2\ndone\nexec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf' > /start.sh && chmod +x /start.sh

RUN mkdir -p /var/log/supervisor /var/log/nginx /var/log/postgresql /run/postgresql && \
    chown postgres:postgres /run/postgresql

EXPOSE 80
CMD ["/start.sh"]
