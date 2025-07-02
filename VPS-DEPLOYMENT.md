# 🚀 GENIUS INDUSTRIES - Despliegue en VPS

## 📋 **ESTRATEGIA: PostgreSQL Docker en VPS**

Esta guía te ayuda a desplegar **GENIUS INDUSTRIES** en tu VPS usando **PostgreSQL en Docker** con la **misma configuración que tienes localmente**.

### ✅ **VENTAJAS DE ESTA ESTRATEGIA**

1. **🎯 Consistencia Total**: Misma BD local = producción
2. **💰 Económico**: Sin costos de Railway/servicios externos  
3. **⚡ Performance**: BD en el mismo servidor (latencia cero)
4. **🔧 Control Total**: Tu manejas todo el stack
5. **📊 Backup Propio**: Copias de seguridad controladas

---

## 🛠️ **REQUISITOS PREVIOS**

### **En tu VPS:**
- Ubuntu 20.04+ o Debian 11+
- 2GB+ RAM (recomendado 4GB)
- 20GB+ espacio en disco
- Docker y Docker Compose instalados
- Nginx instalado
- Dominio configurado apuntando al VPS

### **Información que necesitas:**
- IP del VPS: `tu.ip.del.vps`
- Dominio: `tudominio.com`
- Email: `tu@email.com`

---

## 📦 **PASO 1: Preparar VPS**

### **1.1 Instalar Docker**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### **1.2 Clonar proyecto**
```bash
# En tu VPS
git clone https://github.com/tu-usuario/Genius-Industries.git
cd Genius-Industries
```

---

## 🌐 **PASO 2: Configurar DNS**

En tu proveedor de dominio (Hostinger, Cloudflare, etc.):

```
Tipo  | Nombre | Valor           | TTL
------|--------|-----------------|----
A     | @      | TU.IP.DEL.VPS  | 14400
A     | www    | TU.IP.DEL.VPS  | 14400  
A     | api    | TU.IP.DEL.VPS  | 14400
```

**⏳ Espera 5-30 minutos para propagación DNS**

---

## 🐘 **PASO 3: Desplegar PostgreSQL + App**

### **3.1 Configurar variables de entorno**
```bash
# Crear archivo de producción
cp .env .env.production

# Editar configuración
nano .env.production
```

```env
# Configuración de Producción VPS
SECRET_KEY=tu-secret-key-super-seguro
CLERK_SECRET_KEY=tu-clerk-secret-key
CLERK_PUBLISHABLE_KEY=tu-clerk-publishable-key
DOMAIN=tudominio.com
ENVIRONMENT=production

# PostgreSQL (MISMA CONFIGURACIÓN QUE LOCAL) 
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_DB=genius_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=KhloeMF0911$
DATABASE_URL=postgresql://postgres:KhloeMF0911$@postgres:5432/genius_dev

# CORS
FRONTEND_HOST=https://tudominio.com
BACKEND_CORS_ORIGINS=https://tudominio.com,https://api.tudominio.com
```

### **3.2 Ejecutar despliegue**
```bash
# Hacer ejecutable el script
chmod +x scripts/deploy-vps.sh

# Ejecutar despliegue
DOMAIN=tudominio.com ./scripts/deploy-vps.sh
```

**🎯 Este script hace:**
1. ✅ Detiene contenedores existentes
2. ✅ Construye imágenes de frontend y backend  
3. ✅ Levanta PostgreSQL con la **misma contraseña** que local
4. ✅ Ejecuta migraciones automáticamente
5. ✅ Levanta backend y frontend
6. ✅ Configura Redis cache
7. ✅ Verifica que todo funcione

---

## 🌍 **PASO 4: Configurar Nginx + SSL**

### **4.1 Configurar Nginx**
```bash
# Hacer ejecutable el script
chmod +x scripts/setup-vps-nginx.sh

# Ejecutar configuración (COMO ROOT)
sudo DOMAIN=tudominio.com EMAIL=tu@email.com ./scripts/setup-vps-nginx.sh
```

**🎯 Este script hace:**
1. ✅ Instala Nginx y Certbot
2. ✅ Configura firewall
3. ✅ Crea configuración de proxy para Docker
4. ✅ Obtiene certificados SSL automáticamente
5. ✅ Configura renovación automática de SSL
6. ✅ Aplica configuración de producción optimizada

---

## 🔍 **PASO 5: Verificar Despliegue**

### **5.1 Verificar servicios Docker**
```bash
# Ver estado de contenedores
docker-compose -f docker-compose.production.yml ps

# Ver logs si hay problemas
docker-compose -f docker-compose.production.yml logs -f
```

### **5.2 Verificar conectividad**
```bash
# PostgreSQL
docker exec genius-postgres-prod pg_isready -U postgres -d genius_dev

# Backend
curl http://localhost:8000/health

# Frontend  
curl http://localhost:3000

# HTTPS (después de configurar Nginx)
curl https://tudominio.com
curl https://api.tudominio.com/health
```

### **5.3 URLs finales**
- 🌍 **Frontend**: `https://tudominio.com`
- ⚡ **Backend**: `https://api.tudominio.com` 
- 📊 **API Docs**: `https://api.tudominio.com/docs`
- 🐘 **PostgreSQL**: `localhost:5432` (solo interno)

---

## 📊 **CONFIGURACIÓN DE BASE DE DATOS**

### **Datos de conexión (idénticos a local):**
```
Host: postgres (dentro de Docker)
Port: 5432
Database: genius_dev  
User: postgres
Password: KhloeMF0911$
```

### **Conexión externa (para herramientas como DBeaver):**
```
Host: TU.IP.DEL.VPS
Port: 5432
Database: genius_dev
User: postgres  
Password: KhloeMF0911$
```

### **Backup y restore:**
```bash
# Backup
docker exec genius-postgres-prod pg_dump -U postgres genius_dev > backup.sql

# Restore  
docker exec -i genius-postgres-prod psql -U postgres genius_dev < backup.sql
```

---

## 🔧 **COMANDOS ÚTILES**

### **Docker:**
```bash
# Ver logs
docker-compose -f docker-compose.production.yml logs -f [servicio]

# Reiniciar servicios
docker-compose -f docker-compose.production.yml restart

# Reconstruir imagen
docker-compose -f docker-compose.production.yml build [servicio] --no-cache

# Acceder a PostgreSQL
docker exec -it genius-postgres-prod psql -U postgres -d genius_dev
```

### **Nginx:**
```bash
# Ver logs
sudo tail -f /var/log/nginx/error.log

# Recargar configuración
sudo systemctl reload nginx

# Verificar SSL
sudo certbot certificates

# Renovar SSL manualmente
sudo certbot renew
```

### **Sistema:**
```bash
# Ver espacio en disco
df -h

# Ver uso de memoria
free -h

# Ver procesos Docker
docker stats
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **PostgreSQL no conecta:**
```bash
# Verificar contenedor
docker exec genius-postgres-prod pg_isready -U postgres

# Ver logs
docker logs genius-postgres-prod

# Reiniciar
docker-compose -f docker-compose.production.yml restart postgres
```

### **Backend no responde:**
```bash
# Ver logs
docker logs genius-backend-prod

# Verificar variables de entorno
docker exec genius-backend-prod env | grep POSTGRES

# Reiniciar
docker-compose -f docker-compose.production.yml restart backend
```

### **Frontend no carga:**
```bash
# Ver logs  
docker logs genius-frontend-prod

# Verificar build
docker-compose -f docker-compose.production.yml build frontend --no-cache
```

### **SSL no funciona:**
```bash
# Verificar dominio
nslookup tudominio.com

# Reiniciar certificación
sudo certbot delete --cert-name tudominio.com
sudo certbot --nginx -d tudominio.com
```

---

## 📈 **MONITOREO Y MANTENIMIENTO**

### **Logs automáticos:**
```bash
# Configurar logrotate para Docker
sudo tee /etc/logrotate.d/docker-logs > /dev/null <<EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
EOF
```

### **Backup automático:**
```bash
# Crear script de backup
sudo tee /usr/local/bin/genius-backup.sh > /dev/null <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec genius-postgres-prod pg_dump -U postgres genius_dev > /backups/genius_${DATE}.sql
find /backups -name "genius_*.sql" -mtime +7 -delete
EOF

# Hacer ejecutable
sudo chmod +x /usr/local/bin/genius-backup.sh

# Agregar a crontab (backup diario a las 2am)
echo "0 2 * * * /usr/local/bin/genius-backup.sh" | sudo crontab -
```

---

## 🎉 **RESULTADO FINAL**

Con esta configuración tendrás:

- ✅ **PostgreSQL 15** idéntico al local
- ✅ **Contraseña unificada** `KhloeMF0911$`
- ✅ **HTTPS automático** con Let's Encrypt
- ✅ **Performance óptimo** (todo en el mismo servidor)
- ✅ **Backup controlado** por ti
- ✅ **Costo cero** en base de datos externa
- ✅ **Escalabilidad** fácil

**🚀 Tu aplicación estará disponible en `https://tudominio.com` con máximo rendimiento!** 