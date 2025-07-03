# 🏢 GENIUS INDUSTRIES - Guía de Deployment

## 📋 Resumen de Arquitectura

Esta aplicación está compuesta por:

### **Frontend** (React + Vite + TypeScript)
- **Framework**: React 18 con Vite
- **UI**: Chakra UI + Tailwind CSS  
- **Routing**: TanStack Router
- **Auth**: Clerk
- **Puerto**: 3000 (desarrollo) / 80 (producción)

### **Backend** (FastAPI + Python 3.11)
- **Framework**: FastAPI con Python 3.11
- **ORM**: SQLModel + Alembic
- **Auth**: Clerk + JWT
- **Dependencies**: uv (package manager)
- **Puerto**: 8000

### **Base de Datos**
- **PostgreSQL 14** con persistencia de datos
- **Usuario**: genius / postgres
- **Base de datos**: genius_prod / genius_dev

---

## 🚀 Deployment en Dokploy

### 1. **Configuración en Dokploy**

#### Crear Nueva Aplicación:
1. Accede a tu panel de Dokploy
2. Crea una nueva aplicación **Docker**
3. Conecta tu repositorio de GitHub/GitLab

#### Configuración del Build:
```yaml
# En Dokploy, configura:
Build Method: Dockerfile
Dockerfile Path: ./Dockerfile
Port: 8080
```

### 2. **Variables de Entorno Requeridas**

Configura estas variables en Dokploy:

#### **🔐 Autenticación (Clerk)**
```bash
CLERK_SECRET_KEY=sk_live_tu_secret_key_aqui
CLERK_PUBLISHABLE_KEY=pk_live_tu_publishable_key_aqui  
CLERK_WEBHOOK_SECRET=whsec_tu_webhook_secret_aqui
```

#### **🗄️ Base de Datos**
```bash
POSTGRES_USER=genius
POSTGRES_PASSWORD=tu_password_super_seguro
POSTGRES_DB=genius_prod
DATABASE_URL=postgresql://genius:tu_password_super_seguro@localhost:5432/genius_prod
```

#### **🌐 Dominio y Seguridad**
```bash
DOMAIN=geniusindustries.org
SECRET_KEY=tu-secret-key-super-seguro-2025
ENVIRONMENT=production
```

#### **📧 Email (Opcional)**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
EMAILS_FROM_EMAIL=noreply@geniusindustries.org
EMAILS_FROM_NAME=Genius Industries
```

#### **📊 Monitoreo (Opcional)**
```bash
SENTRY_DSN=https://tu_sentry_dsn_aqui
LOG_LEVEL=INFO
ENABLE_DOCS=false
```

### 3. **Configuración de Dominios en Dokploy**

#### Para una sola aplicación (recomendado):
- **Dominio principal**: `geniusindustries.org`
- **Puerto**: 8080
- El Dockerfile unificado maneja frontend y backend en un solo contenedor

#### Para separar frontend/backend (avanzado):
- **Frontend**: `geniusindustries.org` (puerto 3000)
- **Backend**: `api.geniusindustries.org` (puerto 8000)

---

## 🐳 Opciones de Deployment

### **Opción 1: Dockerfile Unificado (Recomendado para Dokploy)**

Usa el `Dockerfile` en la raíz que incluye:
- ✅ Frontend construido con Vite
- ✅ Backend FastAPI con uv  
- ✅ PostgreSQL 14
- ✅ Nginx como proxy
- ✅ Supervisor para orquestar servicios

```bash
# Deployment automático en Dokploy
docker build -t genius-industries .
docker run -p 8080:8080 genius-industries
```

### **Opción 2: Docker Compose Multi-contenedor**

Para desarrollo local o VPS manual:

```bash
# Desarrollo
docker-compose up -d

# Producción  
docker-compose -f docker-compose.production.yml up -d
```

---

## 🔧 Configuración de SSL (Dokploy)

Dokploy maneja automáticamente SSL con Let's Encrypt. Solo asegúrate de:

1. **Dominio apuntando** al servidor Dokploy
2. **Puerto 80 y 443** abiertos en el firewall
3. **Configurar el dominio** en la aplicación Dokploy

---

## 📱 Health Checks

La aplicación incluye health checks automáticos:

- **General**: `https://geniusindustries.org/health`
- **Nginx**: `https://geniusindustries.org/nginx-health`  
- **API**: `https://geniusindustries.org/api/v1/health`

---

## 🔍 Logs y Monitoreo

### Ver logs en Dokploy:
```bash
# Ver logs de la aplicación
dokploy logs genius-industries

# Ver logs específicos
docker logs genius-industries-container
```

### Estructura de logs:
```
/var/log/
├── supervisor/          # Logs de Supervisor
├── genius/             # Logs del backend
├── nginx/              # Logs de Nginx  
└── postgresql/         # Logs de PostgreSQL
```

---

## 🚨 Solución de Problemas

### **Error: Cannot connect to database**
```bash
# Verificar variables de entorno
echo $DATABASE_URL

# Verificar PostgreSQL
docker exec -it container_name pg_isready -U genius
```

### **Error: Frontend not loading**
```bash
# Verificar build del frontend
docker exec -it container_name ls -la /var/www/html

# Verificar Nginx
docker exec -it container_name nginx -t
```

### **Error: 502 Bad Gateway**
```bash
# Verificar backend
docker exec -it container_name curl localhost:8000/health

# Verificar supervisor
docker exec -it container_name supervisorctl status
```

---

## 🔄 Actualizaciones

### Deployment automático:
1. Push al branch `main`
2. Dokploy detecta cambios automáticamente
3. Rebuild y redeploy automático

### Deployment manual:
```bash
# En Dokploy
1. Go to Applications > genius-industries
2. Click "Rebuild"
3. Wait for deployment to complete
```

---

## 🎯 Checklist de Deployment

### Pre-deployment:
- [ ] Variables de entorno configuradas
- [ ] Dominio apuntando al servidor
- [ ] SSL configurado (automático en Dokploy)
- [ ] Clerk configurado con dominios de producción

### Post-deployment:
- [ ] Health checks funcionando
- [ ] Frontend carga correctamente  
- [ ] API responde en `/docs`
- [ ] Autenticación funciona
- [ ] Base de datos conectada

### Monitoreo continuo:
- [ ] Logs sin errores críticos
- [ ] Performance acceptable  
- [ ] Backups automáticos configurados
- [ ] Alertas configuradas (opcional)

---

## 📞 Soporte

Para problemas específicos de deployment:

1. **Logs**: Revisa los logs en Dokploy
2. **Health checks**: Verifica endpoints de salud
3. **Variables**: Confirma todas las variables de entorno
4. **Dominio**: Verifica configuración DNS

---

**¡Tu aplicación Genius Industries está lista para producción!** 🚀
