# 🛠️ Development Guide – GENIUS INDUSTRIES

Esta guía está diseñada para mantener un estilo de desarrollo coherente y escalable dentro del proyecto `LM_Mobile`, que incluye un backend con FastAPI, frontend con Expo (React Native + TypeScript + NativeWind) y Nhost como backend as a service.

---

## 📦 Estructura del Proyecto

```
LM_Mobile/
├── backend/
│   └── app/
│       ├── api/routes/         # Endpoints por dominio (chat, pagos, auth, etc.)
│       ├── core/               # Configuración, seguridad, nhost
│       │   ├── auth/          # Autenticación y roles
│       │   ├── config/        # Configuraciones
│       │   └── security/      # Seguridad y permisos
│       ├── services/          # Lógica de negocio
│       ├── models.py          # Modelos Pydantic
│       └── main.py            # Entry point FastAPI
├── frontend/
│   ├── components/            # Componentes UI reutilizables
│   │   ├── common/           # Componentes compartidos
│   │   └── role-based/       # Componentes por rol
│   ├── screens/              # Pantallas por funcionalidad
│   │   ├── auth/            # Autenticación
│   │   ├── ceo/             # Pantallas CEO
│   │   ├── manager/         # Pantallas Gerente
│   │   ├── supervisor/      # Pantallas Supervisor
│   │   ├── hr/              # Pantallas RRHH
│   │   ├── support/         # Pantallas Atención al Cliente
│   │   └── agent/           # Pantallas Agente
│   ├── client/              # API y Nhost clients
│   ├── constants/           # Configuraciones
│   ├── utils/              # Utilidades
│   ├── hooks/              # Hooks personalizados
│   └── App.tsx             # Entry point de Expo
├── docker/
│   └── nginx/              # Configuración de Nginx
└── docker-compose.yml      # Orquestación de contenedores
```

---

## 👥 Roles y Permisos

### Estructura de Roles
- CEO
  - Acceso total al sistema
  - Gestión de roles y permisos
  - Reportes financieros globales
  - Configuración del sistema
  - Gestión de sucursales

- Gerente
  - Gestión de sucursal
  - Reportes de rendimiento
  - Gestión de supervisores
  - Aprobación de operaciones
  - Gestión de presupuestos

- Supervisor
  - Gestión de agentes
  - Reportes de equipo
  - Validación de operaciones
  - Gestión de cartera
  - Monitoreo de KPIs

- Recursos Humanos
  - Gestión de empleados
  - Nómina y beneficios
  - Capacitación
  - Evaluaciones
  - Documentación laboral

- Atención al Cliente
  - Gestión de tickets
  - Soporte a clientes
  - Resolución de incidencias
  - Seguimiento de casos
  - Feedback de clientes

- Agentes
  - Gestión de propiedades
  - Gestión de clientes
  - Proceso de ventas
  - Reportes de actividades
  - Seguimiento de leads

### Implementación de Roles

#### Backend
- Middleware de autenticación y autorización
- Validación de permisos por endpoint
- Logging de acciones por rol
- Auditoría de cambios
- Manejo de errores específicos por rol

#### Frontend
- Guardias de ruta por rol
- Componentes condicionales
- Navegación dinámica
- UI adaptativa
- Validación de acciones

#### Nhost
- Políticas RLS por rol
- Validaciones de permisos
- Webhooks específicos
- Auditoría de acciones
- Notificaciones por rol

---

## ⚙️ Reglas de Arquitectura

### Flujo de comunicación (obligatorio)

```
Frontend ⟶ Backend ⟶ Nhost
Nhost ⟶ Backend ⟶ Frontend
```

- ❌ El frontend **no debe escribir directamente en Nhost** (excepto para Realtime)
- ✅ Solo el backend gestiona la lógica, validaciones, almacenamiento y tokens

---

## 🧠 Backend – FastAPI

- ✅ Usar **Pydantic** para validaciones
- ✅ Cada módulo tiene su archivo en `api/routes/`
- ✅ Toda lógica de negocio va en `services/`
- ✅ `models.py` contiene estructuras de datos del dominio
- ✅ Configuración en `core/`, incluyendo seguridad y Nhost

---

## 📱 Frontend – Expo + NativeWind

- ✅ Usar **NativeWind** para todos los estilos
- ✅ Mantener cada pantalla en `screens/` organizada por rol
- ✅ Usar `components/` para UI reutilizable
- ✅ Hooks personalizados van en `hooks/`
- ✅ Archivos auxiliares en `utils/` y constantes globales en `constants/`
- ✅ Toda la lógica de API o Realtime debe vivir en `client/`

---

## 🐳 Docker y Despliegue

### Nginx
- ✅ Configuración como reverse proxy
- ✅ SSL con Let's Encrypt
- ✅ Headers de seguridad
- ✅ Rate limiting
- ✅ Caché y optimización

### Nhost
- ✅ PostgreSQL como base de datos
- ✅ Hasura para GraphQL
- ✅ Auth para autenticación
- ✅ Storage para archivos
- ✅ Funciones serverless

### VPS
- ✅ Docker Compose para orquestación
- ✅ Nginx como reverse proxy
- ✅ SSL con Let's Encrypt
- ✅ Backups automáticos
- ✅ Monitoreo con Prometheus/Grafana

---

## 🧼 Buenas Prácticas de Código

- ✅ Usar nombres descriptivos y en inglés
- ✅ Mantener separación clara entre UI, lógica y datos
- ✅ Evitar duplicar funciones o lógica entre capas
- ✅ Mantener un estilo modular y coherente
- ✅ Siempre documentar funciones públicas
- ✅ Seguir principios de Docker (capas, multi-stage builds)

---

## 🚫 Cosas que deben evitarse

- ❌ Consultas directas desde el frontend a Nhost (excepto suscripciones)
- ❌ Archivos grandes sin dividir en módulos
- ❌ Añadir nuevas carpetas sin justificación clara
- ❌ Credenciales hardcodeadas en Dockerfiles
- ❌ Exponer puertos innecesarios

---

## 📄 Extras

- `README.md`: visión general del proyecto
- `AI_PROJECT_RULES.md`: reglas para IA y equipo
- `.cursor-config.json`: configuración para el asistente de Cursor IDE
- `docker-compose.yml`: configuración de contenedores
- `nhost/config.yaml`: configuración de Nhost

---

## 🎨 Tema y Colores Corporativos

### Paleta de Colores
```typescript
const theme = {
  colors: {
    // Colores principales
    primary: {
      black: '#000000',    // Negro corporativo
      white: '#FFFFFF',    // Blanco
      gray: '#E5E5E5',     // Gris claro
    },
    // Colores de UI
    ui: {
      background: '#FFFFFF',
      surface: '#F5F5F5',
      text: {
        primary: '#000000',
        secondary: '#666666',
        light: '#999999',
      },
      border: '#E5E5E5',
    },
    // Estados
    status: {
      success: '#28A745',
      error: '#DC3545',
      warning: '#FFC107',
      info: '#17A2B8',
    }
  },
  // Tipografía
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Roboto, sans-serif',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
  },
  // Espaciado
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  // Bordes
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  // Sombras
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  }
}
```

### Implementación del Tema

#### Frontend
- ✅ Usar NativeWind con la paleta de colores definida
- ✅ Implementar modo oscuro usando negro como base
- ✅ Mantener consistencia en todos los componentes
- ✅ Usar sombras sutiles para profundidad
- ✅ Implementar transiciones suaves

#### Componentes
- ✅ Botones: Negro con texto blanco
- ✅ Tarjetas: Fondo blanco con bordes grises
- ✅ Headers: Negro con texto blanco
- ✅ Textos: Negro para títulos, gris para contenido
- ✅ Iconos: Negro o gris según contexto

---

