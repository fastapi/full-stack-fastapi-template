# 🤖 Reglas de Desarrollo – GENIUS INDUSTRIES

## 📦 Estructura del Proyecto

Este proyecto se divide en:

### Backend
- `backend/app/api/routes`: contiene todos los endpoints REST organizados por dominio (chat, pagos, usuarios, etc.)
- `backend/app/services`: contiene la lógica de negocio para cada módulo
- `backend/app/models.py`: contiene modelos Pydantic (sin ORM)
- `backend/app/core`: configuraciones, seguridad, nhost, etc.

### Frontend
- `frontend/src/client`: contiene todos los clientes API y Nhost organizados por dominio
- `frontend/src/components`: componentes UI reutilizables organizados por dominio
- `frontend/src/routes`: todas las rutas y páginas organizadas por dominio
- `frontend/src/hooks`: hooks personalizados organizados por dominio
- `frontend/src/theme`: configuración de temas y estilos
- `frontend/src/utils`: utilidades y helpers organizados por dominio

## 🧩 Reglas de Arquitectura

### Flujo de comunicación
```
Frontend → Backend → PostgreSQL
PostgreSQL → Backend → Frontend
```
No se permite que el frontend escriba directamente en Nhost excepto para Realtime.

### Backend
- ✅ Usar solo Pydantic (sin ORM como SQLAlchemy o Tortoise)
- ✅ Cada endpoint debe estar en su archivo correspondiente dentro de `api/routes`
- ✅ Toda la lógica de negocio debe estar en `services/`
- ✅ Los modelos deben vivir en `models.py`
- ✅ Cada módulo debe tener su propia carpeta con sus archivos relacionados

### Frontend
- ✅ Usar Chakra UI para estilos manteniendo el orden de los `theme/` & `theme.tsx`
- ✅ Cada módulo debe tener su propia carpeta con sus componentes, hooks y utilidades
- ✅ La lógica para llamadas a API debe ir en `client/` organizada por dominio
- ✅ Componentes reutilizables en `components/` organizados por dominio
- ✅ Hooks reutilizables en `hooks/` organizados por dominio
- ✅ Utilidades en `utils/` organizadas por dominio
- ✅ Cada ruta debe estar en `routes/` organizada por dominio

## 🧼 Buenas prácticas

### Organización de Código
- ✅ Mantener una estructura clara y consistente en todo el proyecto
- ✅ Cada módulo debe tener su propia carpeta con todos sus archivos relacionados
- ✅ Seguir el patrón de organización por dominio tanto en frontend como en backend
- ✅ Mantener la separación de responsabilidades clara

### Desarrollo
- ✅ Escribir código limpio y modular
- ✅ Usar nombres de variables y funciones en inglés
- ✅ No duplicar lógica entre frontend y backend
- ✅ No mezclar UI con lógica de negocio
- ✅ Documentar funciones y componentes públicos

### Frontend Específico
- ✅ Usar TypeScript para todo el código
- ✅ Implementar lazy loading para rutas
- ✅ Usar React Query para gestión de estado y caché
- ✅ Implementar error boundaries
- ✅ Usar componentes atómicos cuando sea posible

### Backend Específico
- ✅ Usar FastAPI para endpoints
- ✅ Implementar validación con Pydantic
- ✅ Usar async/await para operaciones asíncronas
- ✅ Implementar logging apropiado
- ✅ Manejar errores de forma consistente

## 🛠️ Herramientas de Desarrollo

### Backend
- ✅ Usar `uv` para gestión de dependencias
- ✅ Comando: `uv add` para instalar
- ✅ Comando: `uv sync` para sincronizar cambios
- ✅ Activar entorno: `.venv\Scripts\activate`

### Frontend
- ✅ Usar `npm` para gestión de dependencias
- ✅ Comando: `npm install` para instalar
- ✅ Comando: `npm run dev` para desarrollo
- ✅ Comando: `npm run build` para producción

## 🚫 Cosas que deben evitarse

- ❌ Usar ORMs en el backend
- ❌ Acceder directamente a Nhost desde frontend (excepto suscripciones)
- ❌ Crear carpetas nuevas fuera del estándar sin razón
- ❌ Mezclar lógica de negocio con UI
- ❌ Duplicar código entre módulos
- ❌ Ignorar el tipado en TypeScript
- ❌ Olvidar el manejo de errores
- ❌ Omitir documentación importante

## 👥 Roles y Permisos del Sistema

### Estructura de Roles
- ✅ CEO
  - Acceso total al sistema
  - Gestión de roles y permisos
  - Reportes financieros globales
  - Configuración del sistema
  - Gestión de sucursales

- ✅ Gerente
  - Gestión de sucursal
  - Reportes de rendimiento
  - Gestión de supervisores
  - Aprobación de operaciones
  - Gestión de presupuestos

- ✅ Supervisor
  - Gestión de agentes
  - Reportes de equipo
  - Validación de operaciones
  - Gestión de cartera
  - Monitoreo de KPIs

- ✅ Recursos Humanos
  - Gestión de empleados
  - Nómina y beneficios
  - Capacitación
  - Evaluaciones
  - Documentación laboral

- ✅ Atención al Cliente
  - Gestión de tickets
  - Soporte a clientes
  - Resolución de incidencias
  - Seguimiento de casos
  - Feedback de clientes

- ✅ Agentes
  - Gestión de propiedades
  - Gestión de clientes
  - Proceso de ventas
  - Reportes de actividades
  - Seguimiento de leads

### Implementación de Roles

#### Backend
- ✅ Implementar middleware de roles
- ✅ Configurar permisos en Nhost
- ✅ Validar permisos en endpoints
- ✅ Documentar políticas de acceso
- ✅ Implementar auditoría de acciones

#### Frontend
- ✅ Implementar guardias de ruta por rol
- ✅ Mostrar/ocultar componentes por rol
- ✅ Personalizar dashboards por rol
- ✅ Implementar navegación dinámica
- ✅ Validar acciones por rol

### Reglas de Acceso

#### CEO
- [ ] Acceso a todas las funcionalidades
- [ ] Gestión de configuración global
- [ ] Reportes financieros completos
- [ ] Gestión de usuarios y roles
- [ ] Monitoreo de todas las sucursales

#### Gerente
- [ ] Gestión de su sucursal
- [ ] Reportes de rendimiento
- [ ] Aprobación de operaciones
- [ ] Gestión de presupuestos
- [ ] Monitoreo de supervisores

#### Supervisor
- [ ] Gestión de su equipo
- [ ] Validación de operaciones
- [ ] Reportes de rendimiento
- [ ] Gestión de cartera
- [ ] Monitoreo de agentes

#### Recursos Humanos
- [ ] Gestión de empleados
- [ ] Procesos de nómina
- [ ] Capacitación
- [ ] Evaluaciones
- [ ] Documentación

#### Atención al Cliente
- [ ] Gestión de tickets
- [ ] Soporte a clientes
- [ ] Resolución de casos
- [ ] Feedback
- [ ] Reportes de servicio

#### Agentes
- [ ] Gestión de propiedades
- [ ] Gestión de clientes
- [ ] Proceso de ventas
- [ ] Reportes de actividades
- [ ] Seguimiento de leads

### Implementación Técnica

#### Nhost
- ✅ Configurar políticas RLS por rol
- ✅ Implementar validaciones de permisos
- ✅ Configurar webhooks por rol
- ✅ Implementar auditoría de acciones
- ✅ Configurar notificaciones por rol

#### Frontend
- ✅ Implementar guardias de ruta
- ✅ Componentes condicionales por rol
- ✅ Navegación dinámica
- ✅ Validación de acciones
- ✅ UI adaptativa por rol

#### Backend
- ✅ Middleware de autenticación
- ✅ Validación de permisos
- ✅ Logging de acciones
- ✅ Auditoría de cambios
- ✅ Manejo de errores por rol