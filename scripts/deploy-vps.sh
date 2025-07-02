#!/bin/bash

# 🚀 GENIUS INDUSTRIES - Deploy to VPS with PostgreSQL Docker
# Este script despliega PostgreSQL + Backend + Frontend en VPS

set -e

echo "🚀 Iniciando despliegue de GENIUS INDUSTRIES en VPS..."

# Variables de configuración
PROJECT_NAME="genius-industries"
DOMAIN=${DOMAIN:-"tu-dominio.com"}

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificar Docker y Docker Compose
echo "🔍 Verificando dependencias..."
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    exit 1
fi

print_status "Docker y Docker Compose están instalados"

# 2. Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose -f docker-compose.production.yml down --remove-orphans || true
print_status "Contenedores detenidos"

# 3. Limpiar recursos no utilizados
echo "🧹 Limpiando recursos Docker..."
docker system prune -f
print_status "Limpieza completada"

# 4. Crear variables de entorno si no existen
if [ ! -f .env.production ]; then
    print_warning "Creando archivo .env.production..."
    cat > .env.production << EOF
# Configuración de Producción VPS
SECRET_KEY=your-secret-key-here
CLERK_SECRET_KEY=your-clerk-secret-key
CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key
DOMAIN=${DOMAIN}
ENVIRONMENT=production

# PostgreSQL (Misma configuración que local)
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_DB=genius_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=KhloeMF0911$
DATABASE_URL=postgresql://postgres:KhloeMF0911$@postgres:5432/genius_dev
EOF
    print_warning "Edita .env.production con tus claves reales"
fi

# 5. Construir imágenes
echo "🔨 Construyendo imágenes..."
docker-compose -f docker-compose.production.yml build --no-cache
print_status "Imágenes construidas"

# 6. Crear red si no existe
echo "🌐 Creando red Docker..."
docker network create genius-network 2>/dev/null || true
print_status "Red creada"

# 7. Levantar PostgreSQL primero
echo "🐘 Iniciando PostgreSQL..."
docker-compose -f docker-compose.production.yml up -d postgres
print_status "PostgreSQL iniciado"

# 8. Esperar a que PostgreSQL esté listo
echo "⏳ Esperando PostgreSQL..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker exec genius-postgres-prod pg_isready -U postgres -d genius_dev &> /dev/null; then
        print_status "PostgreSQL está listo!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL no respondió después de $max_attempts intentos"
        exit 1
    fi
    
    echo "  Intento $attempt/$max_attempts..."
    sleep 2
    ((attempt++))
done

# 9. Ejecutar migraciones (si existen)
echo "📊 Ejecutando migraciones..."
if [ -d "backend/app/alembic" ]; then
    docker-compose -f docker-compose.production.yml run --rm backend python -m alembic upgrade head || true
    print_status "Migraciones ejecutadas"
else
    print_warning "No se encontraron migraciones"
fi

# 10. Levantar todos los servicios
echo "🚀 Levantando todos los servicios..."
docker-compose -f docker-compose.production.yml up -d
print_status "Servicios iniciados"

# 11. Verificar estado de servicios
echo "🔍 Verificando estado de servicios..."
sleep 5
docker-compose -f docker-compose.production.yml ps

# 12. Verificar conectividad
echo "🔗 Verificando conectividad..."

# PostgreSQL
if docker exec genius-postgres-prod pg_isready -U postgres -d genius_dev &> /dev/null; then
    print_status "PostgreSQL: ✅ Funcionando"
else
    print_error "PostgreSQL: ❌ Error"
fi

# Backend
if curl -f http://localhost:8000/health &> /dev/null; then
    print_status "Backend: ✅ Funcionando"
else
    print_warning "Backend: ⚠️  Verificar manualmente"
fi

# Frontend
if curl -f http://localhost:3000 &> /dev/null; then
    print_status "Frontend: ✅ Funcionando"
else
    print_warning "Frontend: ⚠️  Verificar manualmente"
fi

echo ""
print_status "🎉 Despliegue completado!"
echo ""
echo "📊 URLs de acceso:"
echo "  🌍 Frontend: http://$DOMAIN (puerto 3000)"
echo "  ⚡ Backend:  http://api.$DOMAIN (puerto 8000)"
echo "  🐘 PostgreSQL: localhost:5432"
echo "  📦 Redis: localhost:6379"
echo ""
echo "📋 Comandos útiles:"
echo "  Ver logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  Reiniciar: docker-compose -f docker-compose.production.yml restart"
echo "  Detener: docker-compose -f docker-compose.production.yml down"
echo ""
print_warning "Configura Nginx como reverse proxy para HTTPS" 