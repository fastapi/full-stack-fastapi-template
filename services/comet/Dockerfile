# 3.12, not 3.14 like the other services. unbabel-comet pins numpy<2.0.0, and
# the last numpy 1.x (1.26.4) ships no wheel past cp312 -- on 3.13+ pip falls
# back to the sdist and the meson build dies looking for a C compiler.
# Revisit when unbabel-comet supports numpy 2.
FROM python:3.12-slim-trixie

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
# Kept in step with backend/Dockerfile.
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# --frozen: build from uv.lock exactly, never re-resolve.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --extra ${TORCH_VARIANT}

COPY ./app /app/app

EXPOSE 8000

# One worker: each is a full copy of the checkpoint. Scale with replicas.
CMD ["fastapi", "run", "--workers", "1", "--port", "8000", "app/main.py"]
