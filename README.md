# 🚀 GENIUS INDUSTRIES

## 📱 Plataforma Empresarial Multiplataforma

Genius Industries es una plataforma empresarial moderna que combina un backend unificado con múltiples frontends, diseñada para proporcionar una experiencia de usuario excepcional y un rendimiento óptimo en todas las plataformas.

## 🛠️ Stack Tecnológico

### Backend Unificado
- **FastAPI** - Framework Python para APIs
- **Pydantic** - Validación de datos
- **Nhost** - Backend as a Service
  - PostgreSQL - Base de datos
  - Hasura - GraphQL API
  - Auth - Autenticación
  - Storage - Almacenamiento de archivos
  - Funciones serverless

### Frontend Web
- **React** - Framework UI
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos
- **React Query** - Gestión de estado
- **React Router** - Navegación
- **Chakra UI** - Componentes UI

### Frontend Móvil
- **Expo SDK 50+** - Framework móvil
- **React Native** - UI nativa
- **TypeScript** - Tipado estático
- **NativeWind** - Estilos con Tailwind
- **React Query** - Gestión de estado
- **React Navigation** - Navegación
- **Expo Router** - Enrutamiento basado en archivos

### Infraestructura
- **VPS** - Servidor de producción con Ubuntu 22.04 LTS
- **Nginx** - Reverse proxy con SSL
- **Let's Encrypt** - Certificados SSL automáticos
- **Docker** - Contenedorización para servicios

## 🚀 Características Principales

### Backend
- 🔐 Autenticación unificada con Nhost Auth
- 📊 API GraphQL con Hasura
- 🔄 Webhooks y eventos en tiempo real
- 📤 Gestión de archivos con CDN
- 🔍 Búsqueda avanzada
- 📊 Analytics y métricas

### Frontend Web
- 🌐 PWA con soporte offline
- 🎨 UI moderna y responsive
- 🔄 Sincronización en tiempo real
- 📱 Diseño adaptativo
- 🌙 Modo oscuro/claro
- 🔍 Búsqueda avanzada

### Frontend Móvil
- 📱 Aplicación nativa iOS/Android
- 🔄 Sincronización offline
- 📤 Carga de archivos con progreso
- 🔔 Notificaciones push
- 🎨 UI nativa optimizada
- 🌐 Internacionalización

## 🏗️ Estructura del Proyecto

```
Genius-Industries/
├── backend/                  # Backend unificado
│   ├── app/
│   │   ├── api/             # Endpoints REST
│   │   ├── core/            # Configuración
│   │   ├── services/        # Lógica de negocio
│   │   └── models.py        # Modelos Pydantic
│   ├── scripts/             # Scripts de utilidad
│   ├── tests/               # Tests unitarios
│   ├── pyproject.toml       # Dependencias Python
│   └── alembic.ini          # Configuración de migraciones
├── frontend/                # Aplicación web
│   ├── src/
│   │   ├── client/         # Clientes API y Nhost
│   │   ├── components/     # Componentes UI reutilizables
│   │   ├── routes/         # Rutas y páginas
│   │   ├── hooks/          # Hooks personalizados
│   │   ├── theme/          # Configuración de temas
│   │   └── utils/          # Utilidades
│   ├── public/             # Assets estáticos
│   ├── tests/              # Tests de integración
│   ├── vite.config.ts      # Configuración de Vite
│   └── package.json        # Dependencias Node
├── docker/                 # Configuración Docker
│   └── nginx/             # Configuración Nginx
├── scripts/               # Scripts globales
├── docs/                  # Documentación
│   ├── DEVELOPMENT_GUIDE.md
│   ├── AI_PROJECT_RULES.md
│   ├── CHECKLIST_PROJECT.md
│   └── SECURITY.md
└── .github/              # Configuración GitHub
```

## 🚀 Inicio Rápido

1. **Requisitos Previos**
   - Node.js 18+
   - Python 3.8+
   - Expo CLI (`npm install -g expo-cli`)
   - Nhost CLI (`npm install -g nhost`)
   - Git
   - Docker

2. **Instalación Backend**
```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # o .venv\Scripts\activate en Windows
   pip install -r requirements.txt
```

3. **Instalación Frontend Web**
```bash
   cd frontend-web
   npm install
   ```

4. **Instalación Frontend Móvil**
```bash
   cd frontend-mobile
   npm install
   ```

5. **Desarrollo**
```bash
   # Backend
   cd backend
   uvicorn app.main:app --reload

   # Frontend Web
   cd frontend-web
   npm run dev

   # Frontend Móvil
   cd frontend-mobile
   npm start
   ```

6. **Despliegue**
   - Ver `DEVELOPMENT_GUIDE.md` para instrucciones detalladas
   - El proceso incluye configuración de Nhost, despliegue de apps y Nginx

## 📚 Documentación

- [Guía de Desarrollo](DEVELOPMENT_GUIDE.md) - Guía completa
- [Reglas de IA](AI_PROJECT_RULES.md) - Reglas para desarrollo con IA
- [Checklist del Proyecto](CHECKLIST_PROJECT.md) - Lista de verificación
- [Seguridad](SECURITY.md) - Guía de seguridad

## 🤝 Contribución

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de Contribución
- Sigue las convenciones de código en `DEVELOPMENT_GUIDE.md`
- Asegúrate de que todos los tests pasen
- Actualiza la documentación según sea necesario
- Incluye ejemplos de uso para nuevas características

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

Genius Industries - [@geniusindustries](https://twitter.com/geniusindustries)

Link del Proyecto: [https://github.com/your-org/Genius-Industries](https://github.com/your-org/Genius-Industries)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com)
- [Nhost](https://nhost.io)
- [React](https://reactjs.org)
- [Expo](https://expo.dev)
- [Chakra UI](https://chakra-ui.com)
- [NativeWind](https://www.nativewind.dev)
