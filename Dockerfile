# 🏢 GENIUS INDUSTRIES - Dockerfile para Dokploy
# Multi-stage build: Frontend + Backend + PostgreSQL + Nginx

# =============================================================================
# ETAPA 1: Construir Frontend
# =============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /build

# Copiar archivos de dependencias
COPY frontend/package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY frontend/ ./

# Construir frontend
RUN npm run build

# =============================================================================
# ETAPA 2: Construir Backend
# =============================================================================
FROM python:3.11-slim AS backend-builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Instalar uv
RUN pip install uv

WORKDIR /backend-build

# Copiar archivos de configuración
COPY backend/pyproject.toml backend/uv.lock ./

# Instalar dependencias
RUN uv sync --frozen --no-dev

# =============================================================================
# ETAPA 3: Imagen de Producción Unificada
# =============================================================================
FROM ubuntu:22.04

# Variables de entorno
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Crear usuarios del sistema
RUN groupadd -r postgres && useradd -r -g postgres postgres && \
    groupadd -r appuser && useradd -r -g appuser appuser

# Actualizar sistema e instalar dependencias
RUN apt-get update && apt-get install -y \
    # PostgreSQL 14
    postgresql-14 \
    postgresql-client-14 \
    postgresql-contrib-14 \
    # Python 3.11
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    # Nginx
    nginx \
    # Supervisor
    supervisor \
    # Utilidades
    curl \
    wget \
    unzip \
    build-essential \
    libpq-dev \
    # Limpieza
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear enlaces simbólicos para Python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Instalar uv para Python
RUN pip install uv

# =============================================================================
# CONFIGURAR POSTGRESQL
# =============================================================================
RUN mkdir -p /var/lib/postgresql/14/main \
             /var/log/postgresql \
             /etc/postgresql/14/main \
             /var/run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql \
                                /var/log/postgresql \
                                /var/run/postgresql \
                                /etc/postgresql

# =============================================================================
# CONFIGURAR BACKEND
# =============================================================================
WORKDIR /app

# Copiar entorno virtual y código desde builders
COPY --from=backend-builder --chown=appuser:appuser /backend-build/.venv /app/.venv
COPY --chown=appuser:appuser backend/app /app/app
COPY --chown=appuser:appuser backend/alembic.ini ./

# =============================================================================
# CONFIGURAR FRONTEND
# =============================================================================
RUN mkdir -p /var/www/html
COPY --from=frontend-builder /build/dist /var/www/html/
RUN chown -R www-data:www-data /var/www/html

# =============================================================================
# CONFIGURAR NGINX
# =============================================================================
RUN rm -f /etc/nginx/sites-enabled/default

# Crear configuración de Nginx para Dokploy
RUN printf 'upstream backend {\n\
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;\n\
}\n\
\n\
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;\n\
limit_req_zone $binary_remote_addr zone=general:10m rate=5r/s;\n\
\n\
server {\n\
    listen 8080;\n\
    server_name _;\n\
    \n\
    add_header X-Frame-Options DENY always;\n\
    add_header X-Content-Type-Options nosniff always;\n\
    add_header X-XSS-Protection "1; mode=block" always;\n\
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;\n\
    \n\
    add_header Access-Control-Allow-Origin "*" always;\n\
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH" always;\n\
    add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With, X-CSRF-Token" always;\n\
    add_header Access-Control-Allow-Credentials true always;\n\
    add_header Access-Control-Max-Age 1728000 always;\n\
    \n\
    if ($request_method = OPTIONS) {\n\
        add_header Access-Control-Allow-Origin "*";\n\
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH";\n\
        add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With, X-CSRF-Token";\n\
        add_header Access-Control-Allow-Credentials true;\n\
        add_header Access-Control-Max-Age 1728000;\n\
        add_header Content-Length 0;\n\
        add_header Content-Type text/plain;\n\
        return 204;\n\
    }\n\
    \n\
    location /api/ {\n\
        limit_req zone=api burst=20 nodelay;\n\
        proxy_pass http://backend/api/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
        proxy_connect_timeout 60s;\n\
        proxy_send_timeout 120s;\n\
        proxy_read_timeout 120s;\n\
        proxy_buffering off;\n\
        proxy_request_buffering off;\n\
    }\n\
    \n\
    location ~ ^/(docs|openapi\\.json|health)$ {\n\
        proxy_pass http://backend;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
    \n\
    location / {\n\
        root /var/www/html;\n\
        try_files $uri $uri/ /index.html;\n\
        \n\
        gzip on;\n\
        gzip_vary on;\n\
        gzip_min_length 1024;\n\
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;\n\
        \n\
        location ~* \\.html$ {\n\
            expires -1;\n\
            add_header Cache-Control "no-cache, no-store, must-revalidate";\n\
        }\n\
        \n\
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {\n\
            expires 1y;\n\
            add_header Cache-Control "public, immutable";\n\
        }\n\
    }\n\
    \n\
    location /nginx-health {\n\
        access_log off;\n\
        return 200 "healthy\\n";\n\
        add_header Content-Type text/plain;\n\
    }\n\
}\n' > /etc/nginx/sites-available/default

RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# =============================================================================
# CONFIGURAR SUPERVISOR
# =============================================================================
RUN mkdir -p /etc/supervisor/conf.d

# Crear configuración de Supervisor
RUN printf '[supervisord]\n\
nodaemon=true\n\
user=root\n\
logfile=/var/log/supervisor/supervisord.log\n\
pidfile=/var/run/supervisord.pid\n\
loglevel=info\n\
\n\
[unix_http_server]\n\
file=/var/run/supervisor.sock\n\
chmod=0700\n\
\n\
[supervisorctl]\n\
serverurl=unix:///var/run/supervisor.sock\n\
\n\
[rpcinterface:supervisor]\n\
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface\n\
\n\
[program:postgresql]\n\
command=/usr/lib/postgresql/14/bin/postgres -D /var/lib/postgresql/14/main\n\
user=postgres\n\
autostart=true\n\
autorestart=true\n\
priority=100\n\
stdout_logfile=/var/log/postgresql/postgres.log\n\
stderr_logfile=/var/log/postgresql/postgres.error.log\n\
redirect_stderr=true\n\
\n\
[program:backend]\n\
command=/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1\n\
directory=/app\n\
user=appuser\n\
autostart=true\n\
autorestart=true\n\
priority=200\n\
stdout_logfile=/var/log/genius/backend.log\n\
stderr_logfile=/var/log/genius/backend.error.log\n\
redirect_stderr=true\n\
environment=PATH="/app/.venv/bin:%%(ENV_PATH)s"\n\
\n\
[program:nginx]\n\
command=/usr/sbin/nginx -g "daemon off;"\n\
autostart=true\n\
autorestart=true\n\
priority=300\n\
stdout_logfile=/var/log/nginx/nginx.log\n\
stderr_logfile=/var/log/nginx/nginx.error.log\n\
redirect_stderr=true\n' > /etc/supervisor/conf.d/supervisord.conf

# =============================================================================
# SCRIPT DE INICIO
# =============================================================================
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Iniciando GENIUS INDUSTRIES..."\n\
\n\
# Crear directorios de logs\n\
mkdir -p /var/log/supervisor /var/log/genius /var/log/nginx /var/log/postgresql\n\
\n\
# Configurar PostgreSQL si no existe\n\
if [ ! -d "/var/lib/postgresql/14/main/base" ]; then\n\
    echo "🐘 Inicializando PostgreSQL..."\n\
    su - postgres -c "/usr/lib/postgresql/14/bin/initdb -D /var/lib/postgresql/14/main --encoding=UTF-8 --locale=C"\n\
    \n\
    # Configurar PostgreSQL\n\
    printf "listen_addresses = '\''*'\''\nport = 5432\nmax_connections = 100\nshared_buffers = 128MB\ndynamic_shared_memory_type = posix\nlog_timezone = '\''UTC'\''\ndatestyle = '\''iso, mdy'\''\ntimezone = '\''UTC'\''\ndefault_text_search_config = '\''pg_catalog.english'\''\n" > /var/lib/postgresql/14/main/postgresql.conf\n\
    \n\
    printf "local   all             postgres                                peer\nlocal   all             all                                     md5\nhost    all             all             127.0.0.1/32            md5\nhost    all             all             ::1/128                 md5\nhost    all             all             0.0.0.0/0               md5\n" > /var/lib/postgresql/14/main/pg_hba.conf\n\
    \n\
    chown postgres:postgres /var/lib/postgresql/14/main/postgresql.conf\n\
    chown postgres:postgres /var/lib/postgresql/14/main/pg_hba.conf\n\
fi\n\
\n\
# Configurar variables de entorno por defecto\n\
export DATABASE_URL="${DATABASE_URL:-postgresql://genius:KhloeMF0911$@localhost:5432/genius_prod}"\n\
export POSTGRES_USER="${POSTGRES_USER:-genius}"\n\
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-KhloeMF0911$}"\n\
export POSTGRES_DB="${POSTGRES_DB:-genius_prod}"\n\
export SECRET_KEY="${SECRET_KEY:-genius-industries-super-secret-key-2025}"\n\
export ENVIRONMENT="${ENVIRONMENT:-production}"\n\
export DOMAIN="${DOMAIN:-geniusindustries.org}"\n\
\n\
echo "✅ Configuración completada, iniciando servicios..."\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf\n' > /usr/local/bin/start-genius.sh

RUN chmod +x /usr/local/bin/start-genius.sh

# =============================================================================
# CONFIGURACIÓN FINAL
# =============================================================================

# Crear directorios de logs
RUN mkdir -p /var/log/supervisor /var/log/genius /var/log/nginx /var/log/postgresql

# Exponer puerto para Dokploy
EXPOSE 8080

# Volúmenes para persistencia
VOLUME ["/var/lib/postgresql/14/main", "/var/log"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/nginx-health && curl -f http://localhost:8080/health || exit 1

# Variables de entorno por defecto
ENV DATABASE_URL="postgresql://genius:KhloeMF0911$@localhost:5432/genius_prod" \
    ENVIRONMENT="production" \
    DOMAIN="geniusindustries.org" \
    PROJECT_NAME="Genius Industries" \
    API_V1_STR="/api/v1"

# Comando de entrada
ENTRYPOINT ["/usr/local/bin/start-genius.sh"]
