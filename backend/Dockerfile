FROM python:3.11-slim

# --------------------------
# Basic environment
# --------------------------
ENV PYTHONUNBUFFERED=1
WORKDIR /app/
ENV VENV_PATH=/app/.venv
ENV PATH="$VENV_PATH/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONPATH=/app

# --------------------------
# Install system dependencies
# --------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*

# --------------------------
# Install uv runtime
# --------------------------
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# --------------------------
# Create virtual environment
# --------------------------
RUN python -m venv $VENV_PATH

# --------------------------
# Install Python dependencies
# --------------------------
# Copy only lock & project files to leverage Docker caching
COPY pyproject.toml uv.lock /app/

RUN uv sync --frozen --no-install-project

# --------------------------
# Copy scripts, app, and tests
# --------------------------
COPY scripts /app/scripts
COPY app /app/app
COPY tests /app/tests
COPY alembic.ini /app/

# --------------------------
# Final sync
# --------------------------
RUN uv sync

# --------------------------
# Default command
# --------------------------
CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
