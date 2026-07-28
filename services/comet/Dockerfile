FROM python:3.11-slim-bookworm

# "cuda" pulls the default PyPI torch (CUDA bundled).
# "cpu" pulls from the pytorch-cpu index — use this for CPU-only Container Apps.
ARG TORCH_VARIANT=cuda

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Weights are mounted, never baked in.
    HF_HOME=/data/aimodels \
    HF_HUB_OFFLINE=1

WORKDIR /app

# Needs >=0.5.16 for [tool.uv] conflicts, which the cpu/cuda extras rely on.
COPY --from=ghcr.io/astral-sh/uv:0.7.5 /uv /uvx /bin/

# --frozen: build from uv.lock exactly, never re-resolve.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --extra ${TORCH_VARIANT}

COPY ./app /app/app

EXPOSE 8000

# One worker: each is a full copy of the checkpoint. Scale with replicas.
CMD ["fastapi", "run", "--workers", "1", "--port", "8000", "app/main.py"]
