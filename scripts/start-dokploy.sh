#!/bin/bash

# 🚀 GENIUS INDUSTRIES - Script de inicio para Dokploy
# Frontend: geniusindustries.org
# Backend: api.geniusindustries.org
# PostgreSQL: Integrado

set -e

echo "🚀 Iniciando GENIUS INDUSTRIES en Dokploy..."

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 1. Configurar PostgreSQL
log "🐘 Configurando PostgreSQL..."

# Inicializar cluster si no existe
if [ ! -d "/var/lib/postgresql/14/main" ]; then
    log "🔧 Inicializando cluster PostgreSQL..."
    su - postgres -c "/usr/lib/postgresql/14/bin/initdb -D /var/lib/postgresql/14/main"
fi

# Configurar PostgreSQL
mkdir -p /etc/postgresql/14/main
cat > /etc/postgresql/14/main/postgresql.conf << EOF
listen_addresses = '*'
port = 5432
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
log_timezone = 'UTC'
datestyle = 'iso, mdy'
timezone = 'UTC'
lc_messages = 'en_US.utf8'
lc_monetary = 'en_US.utf8'
lc_numeric = 'en_US.utf8'
lc_time = 'en_US.utf8'
default_text_search_config = 'pg_catalog.english'
EOF

cat > /etc/postgresql/14/main/pg_hba.conf << EOF
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5
EOF

# Iniciar PostgreSQL
log "🐘 Iniciando PostgreSQL..."
su - postgres -c "pg_ctl -D /var/lib/postgresql/14/main -l /var/log/postgresql/postgresql.log start"

# Esperar a que PostgreSQL esté listo
log "⏳ Esperando PostgreSQL..."
for i in {1..30}; do
    if su - postgres -c "pg_isready -d postgres"; then
        log "✅ PostgreSQL está listo!"
        break
    fi
    log "PostgreSQL no está listo (intento $i/30), esperando..."
    sleep 2
done

# 2. Configurar base de datos y usuario
log "📊 Configurando base de datos..."
su - postgres -c "psql -c \"CREATE USER genius WITH SUPERUSER PASSWORD 'KhloeMF0911$';\"" 2>/dev/null || true
su - postgres -c "createdb -O genius genius_dev" 2>/dev/null || true
su - postgres -c "psql -d genius_dev -c 'SELECT version();'" && log "✅ Base de datos verificada"

# 3. Configurar variables de entorno para el backend
export DATABASE_URL="postgresql://genius:KhloeMF0911$@localhost:5432/genius_dev"
export POSTGRES_SERVER="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="genius_dev"
export POSTGRES_USER="genius"
export POSTGRES_PASSWORD="KhloeMF0911$"
export ENVIRONMENT="production"
export DOMAIN="geniusindustries.org"
export API_DOMAIN="api.geniusindustries.org"
export BACKEND_CORS_ORIGINS="https://geniusindustries.org,https://www.geniusindustries.org"

# ⭐ USUARIO CEO - ACCESO COMPLETO AL SISTEMA
export CEO_USER="ceo@geniusindustries.org"
export CEO_USER_PASSWORD="GeniusCEO2025!"
export ADMIN_USER="ceo@geniusindustries.org"
export ADMIN_PASSWORD="GeniusCEO2025!"

# Configuración de autenticación
export SECRET_KEY="genius-industries-super-secret-key-2025"
export ACCESS_TOKEN_EXPIRE_MINUTES="43200"
export FIRST_SUPERUSER="ceo@geniusindustries.org"
export FIRST_SUPERUSER_PASSWORD="GeniusCEO2025!"

log "👑 Usuario CEO configurado: ${CEO_USER}"

# 4. Ejecutar migraciones si existen
log "📊 Ejecutando migraciones..."
cd /app
if [ -d "app/alembic" ]; then
    python -m alembic upgrade head || log "⚠️  Error en migraciones, continuando..."
else
    log "ℹ️  No se encontraron migraciones Alembic"
fi

# 5. Crear usuario CEO si no existe
log "👑 Verificando usuario CEO..."
python -c "
import asyncio
import sys
sys.path.append('/app')

async def create_ceo_user():
    try:
        from app.core.db import database, get_session
        from app.models import User
        from sqlalchemy import select
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        
        async with get_session() as session:
            # Verificar si existe el usuario CEO
            stmt = select(User).where(User.email == '${CEO_USER}')
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if not existing_user:
                # Crear usuario CEO
                hashed_password = pwd_context.hash('${CEO_USER_PASSWORD}')
                ceo_user = User(
                    email='${CEO_USER}',
                    hashed_password=hashed_password,
                    full_name='Chief Executive Officer',
                    role='CEO',
                    is_active=True,
                    is_superuser=True,
                    phone='+57 300 123 4567'
                )
                session.add(ceo_user)
                await session.commit()
                print('✅ Usuario CEO creado exitosamente')
            else:
                print('ℹ️  Usuario CEO ya existe')
                
    except Exception as e:
        print(f'⚠️  Error creando usuario CEO: {e}')

asyncio.run(create_ceo_user())
" || log "⚠️  Error configurando usuario CEO, continuando..."

# 6. Crear directorios de logs
mkdir -p /var/log/supervisor
mkdir -p /var/log/genius
mkdir -p /var/log/nginx
mkdir -p /var/log/postgresql

# 7. Configurar Nginx con dominios específicos
log "🌍 Configurando Nginx para dominios..."
cat > /etc/nginx/sites-available/default << 'EOF'
# GENIUS INDUSTRIES - Configuración Nginx para Dokploy
# Frontend: geniusindustries.org
# Backend: api.geniusindustries.org

upstream backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general:10m rate=5r/s;

# Backend API - api.geniusindustries.org
server {
    listen 80;
    server_name api.geniusindustries.org;
    
    # Logs específicos
    access_log /var/log/nginx/api.geniusindustries.org.access.log;
    error_log /var/log/nginx/api.geniusindustries.org.error.log;
    
    # Headers de seguridad
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # CORS para API - Permitir desde frontend
    add_header Access-Control-Allow-Origin "https://geniusindustries.org" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH" always;
    add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With, X-CSRF-Token" always;
    add_header Access-Control-Allow-Credentials true always;
    add_header Access-Control-Max-Age 1728000 always;
    
    # Handle preflight requests
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "https://geniusindustries.org";
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH";
        add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With, X-CSRF-Token";
        add_header Access-Control-Allow-Credentials true;
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Length 0;
        add_header Content-Type text/plain;
        return 204;
    }
    
    # Rate limiting para API
    limit_req zone=api burst=20 nodelay;
    
    # Proxy a backend FastAPI
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts para API
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check (sin rate limiting)
    location /health {
        proxy_pass http://backend/health;
        proxy_set_header Host $host;
        access_log off;
    }
    
    # Documentación API
    location /docs {
        proxy_pass http://backend/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # OpenAPI JSON
    location /openapi.json {
        proxy_pass http://backend/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header Cache-Control "public, max-age=3600";
    }
}

# Frontend - geniusindustries.org
server {
    listen 80;
    server_name geniusindustries.org www.geniusindustries.org;
    
    root /var/www/html;
    index index.html index.htm;
    
    # Logs específicos
    access_log /var/log/nginx/geniusindustries.org.access.log;
    error_log /var/log/nginx/geniusindustries.org.error.log;
    
    # Headers de seguridad
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting general
    limit_req zone=general burst=10 nodelay;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Servir frontend SPA
    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache para HTML (sin cache para development)
        location ~* \.html$ {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }
    
    # Assets estáticos con cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
    }
    
    # Deny access a archivos sensibles
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# Redirect www para API
server {
    listen 80;
    server_name www.api.geniusindustries.org;
    return 301 https://api.geniusindustries.org$request_uri;
}
EOF

# Verificar configuración de Nginx
nginx -t && log "✅ Configuración de Nginx válida" || log "⚠️  Error en configuración de Nginx"

log "✅ Configuración completada, iniciando servicios con Supervisor..."

# 8. Iniciar Supervisor para manejar todos los procesos
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 