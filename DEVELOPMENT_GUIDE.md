# 🛠️ Development Guide – GENIUS INDUSTRIES

Esta guía está diseñada para mantener un estilo de desarrollo coherente y escalable dentro del proyecto `LM_Mobile`, que incluye un backend con FastAPI (sin ORM) y un frontend con Expo (React Native + TypeScript + NativeWind).

---

## 📦 Estructura del Proyecto

```
LM_Mobile/
├── backend/
│   └── app/
│       ├── api/routes/         # Endpoints por dominio (chat, pagos, auth, etc.)
│       ├── core/               # Configuración, seguridad, supabase
│       ├── services/           # Lógica de negocio
│       ├── models.py           # Modelos Pydantic (sin ORMs)
│       └── main.py             # Entry point FastAPI
├── frontend/
│   ├── components/             # Componentes UI reutilizables
│   ├── screens/                # Pantallas por funcionalidad (chat, perfil, etc.)
│   ├── client o api/               # API, Supabase y LiveKit clients
│   ├── constants/, utils/, hooks/  # Configs, helpers y lógica compartida
│   └── App.tsx                 # Entry point de Expo
```

---

## ⚙️ Reglas de Arquitectura

### Flujo de comunicación (obligatorio)

```
Frontend ⟶ Backend ⟶ Supabase
Supabase ⟶ Backend ⟶ Frontend
```

- ❌ El frontend **no debe escribir directamente en Supabase** (excepto para Realtime)
- ✅ Solo el backend gestiona la lógica, validaciones, almacenamiento y tokens

---

## 🧠 Backend – FastAPI (sin ORM)

- ✅ Solo se utiliza **Pydantic** para validaciones
- ❌ No usar ORMs como SQLAlchemy, Tortoise, etc.
- ✅ Cada módulo tiene su archivo en `api/routes/`
- ✅ Toda lógica de negocio va en `services/`
- ✅ `models.py` contiene estructuras de datos del dominio
- ✅ Configuración en `core/`, incluyendo seguridad y Supabase

---

## 📱 Frontend – Expo + NativeWind

- ✅ Usar **NativeWind** para todos los estilos
- ✅ Mantener cada pantalla en `screens/`
- ✅ Usar `components/` para UI reutilizable
- ✅ Hooks personalizados van en `hooks/`
- ✅ Archivos auxiliares en `utils/` y constantes globales en `constants/`
- ✅ Toda la lógica de API o Realtime debe vivir en `client/`

---

## 🧼 Buenas Prácticas de Código

- ✅ Usar nombres descriptivos y en inglés
- ✅ Mantener separación clara entre UI, lógica y datos
- ✅ Evitar duplicar funciones o lógica entre capas
- ✅ Mantener un estilo modular y coherente
- ✅ Siempre documentar funciones públicas

---

## 🚫 Cosas que deben evitarse

- ❌ ORMs
- ❌ Consultas directas desde el frontend a Supabase (excepto suscripciones)
- ❌ Archivos grandes sin dividir en módulos
- ❌ Añadir nuevas carpetas sin justificación clara

---

## 📄 Extras

- `README.md`: visión general del proyecto
- `AI_PROJECT_RULES.md`: reglas para IA y equipo
- `.cursor-config.json`: configuración para el asistente de Cursor IDE

---

## 📸 Componentes de Cámara

### CameraComponent
- ✅ Captura de fotos y videos
- ✅ Modo Reels con música y efectos
- ✅ Temporizador manos libres (0-60s)
- ✅ Control de flash
- ✅ Feedback táctil y sonoro
- ✅ Interfaz similar a Instagram

### Características de Audio
- ✅ Sonidos para diferentes eventos:
  - Shutter al tomar foto
  - Countdown para temporizador
  - Recording para inicio de grabación
- ✅ Control de mute
- ✅ Vibración táctil con patrones específicos

### Estructura de Archivos
```
frontend/
├── assets/
│   └── sounds/
│       ├── camera-shutter.mp3
│       ├── countdown.mp3
│       └── recording.mp3
└── components/
    ├── CameraComponent.tsx
    └── ReelsMode.tsx
```

### Dependencias Requeridas
- expo-camera
- expo-av
- expo-media-library
- expo-linear-gradient