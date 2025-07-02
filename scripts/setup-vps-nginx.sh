#!/bin/bash

# 🌐 GENIUS INDUSTRIES - Setup Nginx on VPS
# Configuración completa de Nginx + SSL para VPS

set -e

# Variables de configuración
DOMAIN=${DOMAIN:-"tudominio.com"}
EMAIL=${EMAIL:-"admin@${DOMAIN}"}

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🌐 Configurando Nginx en VPS para GENIUS INDUSTRIES"
echo "📋 Dominio: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# 1. Verificar si estamos en root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# 2. Actualizar sistema
print_info "Actualizando sistema..."
apt update && apt upgrade -y
print_status "Sistema actualizado"

# 3. Instalar dependencias
print_info "Instalando dependencias..."
apt install -y nginx certbot python3-certbot-nginx curl
print_status "Dependencias instaladas"

# 4. Configurar firewall
print_info "Configurando firewall..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable
print_status "Firewall configurado"

# 5. Detener Nginx temporalmente
systemctl stop nginx

# 6. Crear directorios necesarios
print_info "Creando directorios..."
mkdir -p /var/www/certbot
mkdir -p /etc/nginx/ssl
mkdir -p /var/log/nginx
print_status "Directorios creados"

# 7. Configuración inicial de Nginx (solo HTTP)
print_info "Creando configuración inicial de Nginx..."
cat > /etc/nginx/sites-available/genius-industries << EOF
# Configuración temporal para obtener SSL
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN} api.${DOMAIN};
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Proxy temporal al frontend en Docker
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Proxy temporal al backend
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 8. Habilitar sitio
print_info "Habilitando sitio..."
ln -sf /etc/nginx/sites-available/genius-industries /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
print_status "Sitio habilitado"

# 9. Verificar configuración
print_info "Verificando configuración de Nginx..."
nginx -t
print_status "Configuración válida"

# 10. Iniciar Nginx
systemctl start nginx
systemctl enable nginx
print_status "Nginx iniciado"

# 11. Obtener certificados SSL
print_info "Obteniendo certificados SSL con Let's Encrypt..."
certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} -d api.${DOMAIN} \
    --non-interactive \
    --agree-tos \
    --email ${EMAIL} \
    --redirect

if [ $? -eq 0 ]; then
    print_status "Certificados SSL obtenidos"
else
    print_warning "Error obteniendo SSL. Continuando sin SSL..."
fi

# 12. Configuración final de Nginx con SSL
print_info "Aplicando configuración final de Nginx..."

# Copiar la configuración de producción desde el proyecto
if [ -f "./nginx/vps-production.conf" ]; then
    # Reemplazar el dominio en la configuración
    sed "s/tudominio.com/${DOMAIN}/g" ./nginx/vps-production.conf > /etc/nginx/sites-available/genius-industries
    print_status "Configuración de producción aplicada"
else
    print_warning "No se encontró ./nginx/vps-production.conf, usando configuración básica"
fi

# 13. Verificar configuración final
nginx -t && systemctl reload nginx
print_status "Configuración final aplicada"

# 14. Configurar renovación automática de SSL
print_info "Configurando renovación automática de SSL..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
print_status "Renovación automática configurada"

# 15. Verificar estado de servicios
print_info "Verificando estado de servicios..."
systemctl status nginx --no-pager -l

echo ""
print_status "🎉 Configuración de Nginx completada!"
echo ""
echo "📊 URLs de acceso:"
echo "  🌍 Frontend: https://$DOMAIN"
echo "  ⚡ Backend:  https://api.$DOMAIN"
echo ""
echo "📋 Comandos útiles:"
echo "  Ver logs Nginx: tail -f /var/log/nginx/error.log"
echo "  Recargar Nginx: systemctl reload nginx"
echo "  Verificar SSL: certbot certificates"
echo "  Renovar SSL: certbot renew"
echo ""
print_warning "Asegúrate de que Docker esté ejecutándose en los puertos 3000 y 8000"

# 16. Mostrar estado actual
echo ""
print_info "Estado actual de los servicios:"
echo "Nginx: $(systemctl is-active nginx)"
echo "Docker: $(systemctl is-active docker 2>/dev/null || echo 'no instalado')"

# 17. Test de conectividad
echo ""
print_info "Probando conectividad..."
if curl -f http://localhost:3000 &> /dev/null; then
    print_status "Frontend Docker: ✅ Funcionando"
else
    print_warning "Frontend Docker: ⚠️  No responde en puerto 3000"
fi

if curl -f http://localhost:8000 &> /dev/null; then
    print_status "Backend Docker: ✅ Funcionando"
else
    print_warning "Backend Docker: ⚠️  No responde en puerto 8000"
fi 