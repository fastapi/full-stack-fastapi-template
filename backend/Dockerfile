FROM python:3.10 as dev

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY ./pyproject.toml ./alembic.ini /app/

# Install pip and build tools
RUN pip install --no-cache-dir pip setuptools wheel hatchling

# Copy application code
COPY ./app /app/app
COPY ./scripts /app/scripts

# Install the package and its dependencies
RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app

# Make scripts executable
RUN chmod +x /app/scripts/prestart.sh

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
