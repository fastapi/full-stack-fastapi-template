# GENIUS INDUSTRIES - Dockerfile Autocontenido para Dokploy
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

ENV VITE_API_URL=https://api.geniusindustries.org
ENV VITE_API_BASE_URL=https://api.geniusindustries.org  
ENV VITE_FRONTEND_URL=https://geniusindustries.org
ENV VITE_BACKEND_URL=https://api.geniusindustries.org
ENV VITE_ENV=production
ENV NODE_ENV=production

COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    postgresql-15 \
    postgresql-client-15 \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER genius WITH SUPERUSER PASSWORD 'KhloeMF0911\$';" && \
    createdb -O genius genius_dev
USER root

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app

ENV DATABASE_URL="postgresql://genius:KhloeMF0911\$@localhost:5432/genius_dev"
ENV POSTGRES_SERVER="localhost"
ENV POSTGRES_PORT="5432" 
ENV POSTGRES_DB="genius_dev"
ENV POSTGRES_USER="genius"
ENV ENVIRONMENT="production"
ENV BACKEND_CORS_ORIGINS="https://geniusindustries.org"

COPY --from=frontend-builder /app/dist /var/www/html

# Configurar Nginx directamente
RUN echo 'server { listen 80; server_name _; root /var/www/html; index index.html; location / { try_files $uri $uri/ /index.html; } location /api/ { proxy_pass http://localhost:8000; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; } }' > /etc/nginx/sites-available/default

# Configurar Supervisor directamente
RUN echo -e '[supervisord]\nnodaemon=true\n\n[program:postgresql]\ncommand=/usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/15/main\nuser=postgres\nautostart=true\nautorestart=true\n\n[program:nginx]\ncommand=/usr/sbin/nginx -g "daemon off;"\nautostart=true\nautorestart=true\n\n[program:fastapi]\ncommand=python -m uvicorn app.main:app --host 0.0.0.0 --port 8000\ndirectory=/app\nautostart=true\nautorestart=true' > /etc/supervisor/conf.d/supervisord.conf

# Script de inicio directo
RUN echo -e '#!/bin/bash\nset -e\nservice postgresql start\nuntil pg_isready -h localhost -p 5432 -U postgres; do\n  sleep 2\ndone\nexec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf' > /start.sh && chmod +x /start.sh

RUN mkdir -p /var/log/supervisor /var/log/nginx /var/log/postgresql /run/postgresql && \
    chown postgres:postgres /run/postgresql

EXPOSE 80
CMD ["/start.sh"]
