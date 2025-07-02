# 👑 DOKPLOY - GENIUS INDUSTRIES CON USUARIO CEO

## 🎯 **DOMINIOS CONFIGURADOS**

- **Frontend**: `geniusindustries.org`
- **Backend**: `api.geniusindustries.org`

## 👑 **USUARIO CEO - ACCESO COMPLETO**

### **Credenciales CEO**
```
Email: ceo@geniusindustries.org
Password: GeniusCEO2025!
Role: CEO
Permissions: SUPERUSER (Acceso completo al sistema)
```

## ⚙️ **VARIABLES DE ENTORNO PARA DOKPLOY**

### **Base de Datos**
```bash
DATABASE_URL=postgresql://genius:KhloeMF0911$@localhost:5432/genius_dev
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=genius_dev
POSTGRES_USER=genius
POSTGRES_PASSWORD=KhloeMF0911$
```

### **Usuario CEO y Autenticación**
```bash
CEO_USER=ceo@geniusindustries.org
CEO_USER_PASSWORD=GeniusCEO2025!
ADMIN_USER=ceo@geniusindustries.org
ADMIN_PASSWORD=GeniusCEO2025!
SECRET_KEY=genius-industries-super-secret-key-2025
ACCESS_TOKEN_EXPIRE_MINUTES=43200
FIRST_SUPERUSER=ceo@geniusindustries.org
FIRST_SUPERUSER_PASSWORD=GeniusCEO2025!
```

### **Aplicación**
```bash
ENVIRONMENT=production
DOMAIN=geniusindustries.org
API_DOMAIN=api.geniusindustries.org
BACKEND_CORS_ORIGINS=https://geniusindustries.org,https://www.geniusindustries.org
```

### **Frontend Build**
```bash
VITE_API_URL=https://api.geniusindustries.org
VITE_API_BASE_URL=https://api.geniusindustries.org
VITE_FRONTEND_URL=https://geniusindustries.org
VITE_BACKEND_URL=https://api.geniusindustries.org
NODE_ENV=production
VITE_ENV=production
```

## 🚀 **CONFIGURACIÓN DOKPLOY**

### **1. Crear Aplicación**
1. Ir a Dokploy Dashboard
2. Crear nueva aplicación
3. Conectar repositorio GitHub
4. Configurar build

### **2. Build Settings**
```
Repository: tu-repo/Genius-Industries
Branch: main o develop
Dockerfile: Dockerfile.dokploy
Build Context: /
Port: 80
```

### **3. Dominios**
En **Settings > Domains**:
- Dominio principal: `geniusindustries.org`
- SSL: Automático
- Redirects: www.geniusindustries.org → geniusindustries.org

### **4. DNS Configuration**
```
geniusindustries.org        A    [IP-DOKPLOY]
www.geniusindustries.org    A    [IP-DOKPLOY]
api.geniusindustries.org    A    [IP-DOKPLOY]
```

## 🏗️ **ARQUITECTURA DEL SISTEMA**

```
┌─────────────────────────────────────────┐
│ DOKPLOY CONTAINER (Puerto 80)           │
├─────────────────────────────────────────┤
│ 🌍 Nginx:                              │
│ ├─ geniusindustries.org → Frontend      │
│ └─ api.geniusindustries.org → Backend   │
├─────────────────────────────────────────┤
│ ⚡ Backend FastAPI (Puerto 8000)        │
│ └─ Usuario CEO: ceo@geniusindustries.org│
├─────────────────────────────────────────┤
│ 🗄️  PostgreSQL (Puerto 5432)           │
│ └─ Database: genius_dev                 │
├─────────────────────────────────────────┤
│ 🔧 Supervisor                          │
│ └─ Maneja todos los procesos            │
└─────────────────────────────────────────┘
```

## 👑 **ACCESO CEO COMPLETO**

### **Funcionalidades CEO**
✅ **Dashboard Global**
- KPIs financieros de toda la empresa
- Rendimiento de todas las sucursales
- Estado general del negocio
- Métricas en tiempo real

✅ **Gestión de Usuarios**
- Crear, editar, eliminar usuarios
- Asignar roles y permisos
- Gestión de sucursales
- Auditoría completa

✅ **Configuración del Sistema**
- Parámetros globales
- Integraciones
- Configuración de seguridad
- Backup y mantenimiento

✅ **Reportes Financieros**
- Ingresos/egresos globales
- Análisis de rentabilidad
- Proyecciones financieras
- Reportes de cumplimiento

✅ **Módulos Inmobiliarios**
- Gestión de todas las propiedades
- Análisis de mercado
- Configuración de precios
- Gestión de inventario

✅ **Módulos de Créditos**
- Gestión de cartera completa
- Análisis de riesgo
- Aprobación de créditos
- Configuración de tasas

## 🔐 **SEGURIDAD IMPLEMENTADA**

### **Autenticación CEO**
- Contraseña segura: `GeniusCEO2025!`
- Token JWT con expiración extendida (30 días)
- Rol SUPERUSER con permisos completos
- Sesiones seguras con HTTPS

### **Protección de Datos**
- CORS configurado para dominios específicos
- Headers de seguridad implementados
- Rate limiting en API
- Logs de auditoría completos

## ✅ **VERIFICACIÓN POST-DEPLOY**

### **1. Frontend**
```bash
curl -I https://geniusindustries.org
# Debe responder: 200 OK
```

### **2. Backend API**
```bash
curl https://api.geniusindustries.org/health
# Debe responder: {"status": "healthy"}

curl https://api.geniusindustries.org/docs
# Documentación API disponible
```

### **3. Login CEO**
```bash
curl -X POST https://api.geniusindustries.org/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ceo@geniusindustries.org&password=GeniusCEO2025!"
# Debe retornar access_token
```

### **4. Verificar Usuario CEO**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.geniusindustries.org/api/v1/users/me
# Debe mostrar datos del CEO con role="CEO"
```

## 🎯 **URLS FINALES**

- **🌐 Frontend**: https://geniusindustries.org
- **⚡ Backend API**: https://api.geniusindustries.org
- **📚 Documentación**: https://api.geniusindustries.org/docs
- **👑 Login CEO**: https://geniusindustries.org/sign-in

## 🔧 **COMANDO DE VERIFICACIÓN**

Después del deploy, ejecutar desde el proyecto local:

```bash
# Verificar todo el sistema
python scripts/verify-ceo-user.py

# O verificar manualmente
curl -X POST https://api.geniusindustries.org/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ceo@geniusindustries.org&password=GeniusCEO2025!"
```

---

## 🎉 **¡GENIUS INDUSTRIES LISTO!**

✅ **Usuario CEO configurado con acceso completo**  
✅ **Dominios específicos funcionando**  
✅ **PostgreSQL integrado**  
✅ **SSL automático**  
✅ **Sistema listo para producción**

**El CEO puede acceder con credenciales completas a todo el sistema desde `geniusindustries.org`** 👑 