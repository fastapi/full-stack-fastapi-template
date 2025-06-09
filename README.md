# 🏠 Genius Industries Real Estate Platform

Plataforma inmobiliaria completa que ofrece servicios de compra, venta, corretaje, administración, asesorías, avalúos y créditos inmobiliarios.

## 🌟 Características Principales

- 📱 Aplicación móvil y web responsive
- 🔐 Autenticación segura con Supabase
- 🏢 Gestión completa de propiedades
- 💰 Sistema de créditos inmobiliarios
- 📊 Administración de propiedades
- 📝 Avalúos y tasaciones
- 👥 Asesoría inmobiliaria personalizada

## 🛠️ Tecnologías

### Backend
- FastAPI (Python)
- Supabase (Base de datos y autenticación)
- Pydantic (Validación de datos)

### Frontend
- React Native con Expo
- NativeWind (Estilos)
- Supabase Client

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- Node.js 16+
- Expo CLI
- Supabase CLI

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
expo start
```

## 📁 Estructura del Proyecto

```
LM_Mobile/
├── backend/
│   └── app/
│       ├── api/routes/         # Endpoints REST
│       ├── core/              # Configuración
│       ├── services/          # Lógica de negocio
│       └── models.py          # Modelos Pydantic
└── frontend/
    ├── components/            # Componentes UI
    ├── screens/              # Pantallas
    ├── services/             # Clientes API
    └── utils/                # Utilidades
```

## 🔐 Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Backend
SECRET_KEY=your_secret_key
BACKEND_CORS_ORIGINS=["*"]

# Email
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

## 📱 Características de la Aplicación

### Gestión de Propiedades
- Listado y búsqueda avanzada
- Filtros por tipo, precio, ubicación
- Galería de imágenes
- Detalles completos
- Ubicación en mapa

### Sistema de Créditos
- Simulador de créditos
- Solicitud online
- Seguimiento de estado
- Documentación digital

### Administración
- Dashboard de propiedades
- Gestión de inquilinos
- Control de pagos
- Reportes y estadísticas

### Avalúos
- Solicitud de avalúos
- Historial de tasaciones
- Reportes detallados
- Comparativas de mercado

### Asesoría
- Consultas personalizadas
- Asesoría legal
- Análisis de inversión
- Recomendaciones

## 🤝 Contribución

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

Genius Industries - [@geniusindustries](https://twitter.com/geniusindustries)

Link del Proyecto: [https://github.com/geniusindustries/real-estate-platform](https://github.com/geniusindustries/real-estate-platform)
