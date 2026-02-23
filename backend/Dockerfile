FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Copy kila-models (shared local package) and install
COPY kila-models/ /kila-models/
RUN pip install --no-cache-dir /kila-models/

# Install backend dependencies from pre-generated requirements file
# (generated locally via: uv export --frozen --no-hashes --no-dev --no-emit-project --no-emit-package kila-models)
COPY kila/backend/requirements.prod.txt ./
RUN pip install --no-cache-dir -r requirements.prod.txt

# Copy application source
COPY kila/backend/scripts ./scripts
COPY kila/backend/alembic.ini ./
COPY kila/backend/app ./app

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
