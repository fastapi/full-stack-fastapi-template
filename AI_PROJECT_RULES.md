# 🤖 Reglas de Desarrollo para Cursor IDE – LM_Mobile

## 📦 Estructura del Proyecto

Este proyecto se divide en:

- `backend/app/api/routes`: contiene todos los endpoints REST organizados por dominio (chat, pagos, usuarios, etc.)
- `backend/app/services`: contiene la lógica de negocio para cada módulo
- `backend/app/models.py`: contiene modelos Pydantic (sin ORM)
- `backend/app/core`: configuraciones, seguridad, supabase, etc.
- `frontend/`: aplicación Expo + NativeWind
  - `components/`: UI modular (ej. CreateComponent, FeedItem, etc.)
  - `screens/`: todas las pantallas por funcionalidad
  - `services/`: lógica externa (API, supabase, livekit)
  - `lib/`, `constants/`, `hooks/`, `utils/`: organización clara y reutilizable

## 🧩 Reglas de Arquitectura

- 📡 Flujo de comunicación:
  ```
  Frontend → Backend → Supabase
  Supabase → Backend → Frontend
  ```
  No se permite que el frontend escriba directamente en Supabase excepto para Realtime.

- 🧠 Backend:
  - ✅ Usar solo Pydantic (sin ORM como SQLAlchemy o Tortoise)
  - ✅ Cada endpoint debe estar en su archivo correspondiente dentro de `api/routes`
  - ✅ Toda la lógica de negocio debe estar en `services/`
  - ✅ Los modelos deben vivir en `models.py`

- 📱 Frontend:
  - ✅ Usar Chackra-ui para estilos manteniendo el orden de los `theme/` & `theme.tsx`
  - ✅ Cada ruta o pages debe estar en `routes/`
  - ✅ La lógica para llamadas a API debe ir en `client o api/`
  - ✅ Componentes reutilizables en `components/`
  - ✅ Hooks reutilizables en `hooks/`

## 🧼 Buenas prácticas

- ✅ Escribir código limpio y modular
- ✅ Usar nombres de variables y funciones en inglés
- ✅ Mantener separación de responsabilidades clara
- ✅ No duplicar lógica entre frontend y backend
- ✅ No mezclar UI con lógica de negocio

## instalacion de dependencias en el backend
- User comando 'uv pip install ' - se usa gestor de dependencias uv
- para sincronizar cambios usar 'uv sync'
- activar entorno virtual usar '.venv\Scripts\activate '

## despliegue de servidor backend 
- usar 'uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'
- verifica siempre antes de ejecutar comando la ruta 'LM_Mobile/backend'

## 🚫 Cosas que deben evitarse

- ❌ Usar ORMs
- ❌ Acceder directamente a Supabase desde frontend (excepto suscripciones)
- ❌ Crear carpetas nuevas fuera del estándar sin razón