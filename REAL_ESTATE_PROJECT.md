# 🏠 Plataforma Inmobiliaria - Genius Industries

## 📦 Estructura del Proyecto

```
LM_Mobile/
├── backend/
│   └── app/
│       ├── api/routes/
│       │   ├── properties/     # Endpoints para propiedades
│       │   ├── users/         # Gestión de usuarios y perfiles
│       │   ├── transactions/  # Compras, ventas, alquileres
│       │   ├── credits/       # Gestión de créditos inmobiliarios
│       │   ├── appraisals/    # Avalúos y tasaciones
│       │   ├── management/    # Administración de propiedades
│       │   └── advisory/      # Asesorías inmobiliarias
│       ├── core/
│       │   ├── config.py      # Configuraciones generales
│       │   ├── security.py    # Autenticación y autorización
│       │   └── supabase.py    # Configuración de Supabase
│       ├── services/
│       │   ├── property_service.py
│       │   ├── credit_service.py
│       │   ├── appraisal_service.py
│       │   └── management_service.py
│       └── models.py
├── frontend/
│   ├── components/
│   │   ├── properties/        # Componentes de propiedades
│   │   ├── credits/          # Componentes de créditos
│   │   ├── management/       # Componentes de administración
│   │   └── common/           # Componentes compartidos
│   ├── screens/
│   │   ├── properties/       # Pantallas de propiedades
│   │   ├── credits/         # Pantallas de créditos
│   │   ├── management/      # Pantallas de administración
│   │   └── profile/         # Perfil y configuración
│   ├── services/
│   │   ├── api/            # Cliente API
│   │   └── supabase/       # Cliente Supabase
│   └── utils/
```

## 🎯 Funcionalidades Principales

### 1. Gestión de Propiedades
- Listado de propiedades con filtros avanzados
- Detalles completos de cada propiedad
- Sistema de búsqueda inteligente
- Galería de imágenes y videos
- Ubicación y mapas interactivos

### 2. Sistema de Créditos
- Simulador de créditos
- Gestión de solicitudes
- Seguimiento de estado
- Documentación digital
- Historial de transacciones

### 3. Administración de Propiedades
- Dashboard de administración
- Gestión de inquilinos
- Control de pagos
- Reportes y estadísticas
- Mantenimiento y reparaciones

### 4. Avalúos y Tasaciones
- Solicitud de avalúos
- Historial de tasaciones
- Reportes detallados
- Comparativas de mercado
- Documentación legal

### 5. Asesoría Inmobiliaria
- Consultas personalizadas
- Asesoría legal
- Análisis de inversión
- Estudios de mercado
- Recomendaciones personalizadas

## 🔐 Seguridad y Autenticación

- Autenticación con Supabase
- OAuth para redes sociales
- Roles y permisos
- Protección de datos sensibles
- Encriptación de información

## 📱 Características Técnicas

### Frontend
- React Native con Expo
- NativeWind para estilos
- Componentes reutilizables
- Diseño responsive
- Optimización de rendimiento

### Backend
- FastAPI
- Pydantic para validaciones
- Integración con Supabase
- API RESTful
- Documentación automática

## 🎨 UI/UX

- Diseño moderno y profesional
- Interfaz intuitiva
- Experiencia de usuario fluida
- Accesibilidad
- Modo oscuro/claro

## 📊 Base de Datos (Supabase)

### Tablas Principales
- properties
- users
- transactions
- credits
- appraisals
- management_contracts
- advisory_sessions

## 🚀 Despliegue

- Backend: FastAPI en servidor dedicado
- Frontend: Expo para iOS/Android
- Base de datos: Supabase
- CDN para assets
- Monitoreo y logs 