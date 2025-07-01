# ==============================================================================
# DOCKERFILE UNIFICADO - GENIUS INDUSTRIES
# Backend (FastAPI) + Frontend (React) en un solo contenedor
# ==============================================================================

# ============== STAGE 1: Build Frontend ================
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Copiar package files
COPY frontend/package*.json ./
COPY frontend/biome.json ./
COPY frontend/tsconfig*.json ./
COPY frontend/vite.config.ts ./
COPY frontend/openapi-ts.config.ts ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html ./

# Build del frontend
RUN npm run build

# ============== STAGE 2: Python Environment with UV ================
FROM python:3.11-slim AS python-base

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Instalar dependencias del sistema y UV
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar UV
RUN pip install uv

# ============== STAGE 3: Backend Setup ================
FROM python-base AS backend-setup

WORKDIR /app

# Copiar archivos de configuración de UV
COPY backend/pyproject.toml ./
COPY backend/uv.lock ./

# Crear virtual environment y instalar dependencias con UV
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --frozen

# ============== STAGE 4: Final Production Image ================
FROM python-base AS production

WORKDIR /app

# Copiar virtual environment desde backend-setup
COPY --from=backend-setup /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Crear directorios necesarios
RUN mkdir -p /app/frontend /app/static

# Copiar frontend construido
COPY --from=frontend-build /app/frontend/dist /app/frontend

# Copiar backend
COPY backend/app ./app
COPY backend/alembic.ini ./
COPY backend/pyproject.toml ./

# Crear usuario no-root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Configurar variables de entorno
ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/utils/health || exit 1

# Comando de inicio
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"] 