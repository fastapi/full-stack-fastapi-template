# 🏢 GENIUS INDUSTRIES - Backend Dockerfile
# FastAPI + Python 3.11 + uv + PostgreSQL support

FROM python:3.11-slim as builder

# Variables de entorno para construcción
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar uv para gestión de dependencias
RUN pip install uv

# Directorio de trabajo
WORKDIR /build

# Copiar archivos de configuración de dependencias
COPY pyproject.toml uv.lock ./

# Crear entorno virtual y instalar dependencias
RUN uv sync --frozen --no-dev

# =============================================================================
# Imagen de producción
# =============================================================================
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Directorio de trabajo
WORKDIR /app

# Copiar entorno virtual desde builder
COPY --from=builder --chown=appuser:appuser /build/.venv /app/.venv

# Copiar código fuente de la aplicación
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser alembic.ini ./

# Crear directorio para logs
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
