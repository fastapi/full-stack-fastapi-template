# 🚀 GENIUS INDUSTRIES - Dockerfile para Dokploy
# Versión simplificada y funcional

FROM node:18-alpine AS frontend-builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

# Variables de entorno para build
ENV VITE_API_URL=https://api.geniusindustries.org
ENV VITE_API_BASE_URL=https://api.geniusindustries.org  
ENV VITE_FRONTEND_URL=https://geniusindustries.org
ENV VITE_BACKEND_URL=https://api.geniusindustries.org
ENV VITE_ENV=production
ENV NODE_ENV=production

COPY frontend/ ./
RUN npm run build

# Imagen principal con Python y servicios
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-15 \
    postgresql-client-15 \
    postgresql-contrib-15 \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar PostgreSQL
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER genius WITH SUPERUSER PASSWORD 'KhloeMF0911$';" && \
    createdb -O genius genius_dev
USER root

# Configurar backend
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY backend/app ./app

# Variables de entorno para producción
ENV DATABASE_URL="postgresql://genius:KhloeMF0911$@localhost:5432/genius_dev"
ENV POSTGRES_SERVER="localhost"
ENV POSTGRES_PORT="5432" 
ENV POSTGRES_DB="genius_dev"
ENV POSTGRES_USER="genius"
ENV POSTGRES_PASSWORD="KhloeMF0911$"
ENV ENVIRONMENT="production"
ENV BACKEND_CORS_ORIGINS="https://geniusindustries.org,https://www.geniusindustries.org"

# Copiar frontend construido
COPY --from=frontend-builder /app/dist /var/www/html

# Configurar Nginx (copiar archivos de configuración)
COPY nginx/dokploy.conf /etc/nginx/sites-available/default

# Configurar Supervisor
COPY scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copiar script de inicio
COPY scripts/start-dokploy.sh /start.sh
RUN chmod +x /start.sh

# Crear directorios necesarios
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/log/postgresql
RUN mkdir -p /run/postgresql && chown postgres:postgres /run/postgresql

# Exponer puerto
EXPOSE 80

# Comando de inicio
CMD ["/start.sh"]
