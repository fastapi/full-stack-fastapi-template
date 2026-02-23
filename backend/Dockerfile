FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

WORKDIR /app

# Copy kila-models to the path expected by uv.lock
# uv.lock resolves "../../kila-models" from /app/ to /kila-models
COPY kila-models/ /kila-models/

# Copy project manifests for dependency resolution
COPY kila/backend/pyproject.toml kila/backend/uv.lock ./

# Export all deps from lock file (excluding kila-models which we install from /kila-models),
# then install via pip. kila-models is installed separately.
RUN uv export --frozen --no-hashes --no-dev --no-emit-project | \
    grep -Ev "(kila.models|kila-models)" > /tmp/requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir /kila-models/

# Copy application source
COPY kila/backend/scripts ./scripts
COPY kila/backend/alembic.ini ./
COPY kila/backend/app ./app

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
