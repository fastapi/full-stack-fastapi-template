FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# No apt packages: lingua ships prebuilt manylinux wheels and there is no torch
# here, so the triton/C-compiler problem that metricx hit does not apply.
COPY --from=ghcr.io/astral-sh/uv:0.7.5 /uv /uvx /bin/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

COPY ./app /app/app

EXPOSE 8000

# No weights and no GPU, so extra workers are cheap here — unlike the model
# services, where each worker is another full copy of the weights.
CMD ["fastapi", "run", "--workers", "1", "--port", "8000", "app/main.py"]
