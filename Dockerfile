# 🚀 GENIUS INDUSTRIES - Dockerfile Unificado  
# Desarrollo: Backend + Frontend
# Dokploy: PostgreSQL + Backend + Frontend + Nginx

FROM node:18-alpine AS frontend-builder

# Construir Frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

# Variables de entorno para build
ENV VITE_API_URL=https://api.geniusindustries.org \
    VITE_API_BASE_URL=https://api.geniusindustries.org \
    VITE_FRONTEND_URL=https://geniusindustries.org \
    VITE_BACKEND_URL=https://api.geniusindustries.org \
    VITE_ENV=production \
    NODE_ENV=production

COPY frontend/ ./
RUN npm run build

# Imagen principal para Dokploy (unificada)
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-15 \
    postgresql-client-15 \
    postgresql-contrib-15 \
    nginx \
    supervisor \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configurar PostgreSQL
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER genius WITH SUPERUSER PASSWORD 'KhloeMF0911$';" && \
    createdb -O genius genius_dev
USER root

# Configurar backend Python
WORKDIR /app
COPY backend/requirements.txt backend/pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código del backend
COPY backend/app ./app

# Variables de entorno para producción
ENV DATABASE_URL="postgresql://genius:KhloeMF0911$@localhost:5432/genius_dev" \
    POSTGRES_SERVER="localhost" \
    POSTGRES_PORT="5432" \
    POSTGRES_DB="genius_dev" \
    POSTGRES_USER="genius" \
    POSTGRES_PASSWORD="KhloeMF0911$" \
    ENVIRONMENT="production" \
    DOMAIN="geniusindustries.org" \
    API_DOMAIN="api.geniusindustries.org" \
    BACKEND_CORS_ORIGINS="https://geniusindustries.org,https://www.geniusindustries.org"

# Copiar frontend construido
COPY --from=frontend-builder /frontend/dist /var/www/html

# Configurar Nginx
COPY nginx/dokploy.conf /etc/nginx/sites-available/default

# Configurar Supervisor
COPY scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Crear script de inicio
COPY scripts/start-dokploy.sh /start-dokploy.sh
RUN chmod +x /start-dokploy.sh

# Crear directorios y permisos
RUN mkdir -p /var/log/supervisor /var/log/genius /var/log/nginx /var/log/postgresql
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
RUN chown -R postgres:postgres /var/lib/postgresql

# Exponer puerto
EXPOSE 80

# Comando de inicio
CMD ["/start-dokploy.sh"]
