# ============================================================
# Stage 1: Builder
# Install dependencies and compile bytecode in an isolated env.
# ============================================================
FROM python:3.10-slim AS builder

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Compile bytecode for faster startup
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# Use copy link mode for uv cache compatibility
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

WORKDIR /app/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies only (no workspace packages yet) for better layer caching
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace --package app

COPY ./backend/scripts /app/backend/scripts
COPY ./backend/pyproject.toml /app/backend/
COPY ./backend/app /app/backend/app

# Final sync — installs the workspace package itself into the venv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --package app

# ============================================================
# Stage 2: Runtime
# Minimal image — only the venv and app source, no build tools.
# ============================================================
FROM python:3.10-slim AS runtime

# OCI standard metadata for GHCR
LABEL org.opencontainers.image.source="https://github.com/Aygentic/Aygentic-starter-template"
LABEL org.opencontainers.image.description="Aygentic microservice backend"

# Dynamic labels populated by CI build args
ARG GIT_COMMIT=unknown
ARG BUILD_TIME=unknown
LABEL org.opencontainers.image.version="${BUILD_TIME}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"

# Propagate build metadata into the container environment
ENV GIT_COMMIT=${GIT_COMMIT}
ENV BUILD_TIME=${BUILD_TIME}
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security hardening
RUN useradd --create-home appuser

WORKDIR /app/backend/

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source and scripts from the builder stage
COPY --from=builder /app/backend/app /app/backend/app
COPY --from=builder /app/backend/scripts /app/backend/scripts

# Place venv executables on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Drop privileges — run as non-root user
USER appuser

EXPOSE 8000

# Health check using Python + httpx (no curl required in slim image)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import httpx; httpx.get('http://localhost:8000/healthz').raise_for_status()"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
