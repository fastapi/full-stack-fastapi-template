FROM python:3.14-slim-trixie

# "cuda" pulls the default PyPI torch (CUDA bundled, ~5.5 GB image).
# "cpu" pulls from the pytorch-cpu index — use this for CPU-only Container Apps.
ARG TORCH_VARIANT=cuda

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Weights are mounted, never baked in. Keep the hub out of the request path
    # so a cold start can't turn into a surprise download.
    HF_HOME=/data/aimodels \
    HF_HUB_OFFLINE=1

WORKDIR /app

# Needs >=0.5.16 for [tool.uv] conflicts, which the cpu/cuda extras rely on.
# Kept in step with backend/Dockerfile; 0.7.5 predates Python 3.14 and does not
# resolve cp314 wheels.
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Dependencies in their own layer so app edits don't re-resolve torch.
# --frozen: build from uv.lock exactly, never re-resolve. Regenerate with
# `uv lock` when a dependency changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --extra ${TORCH_VARIANT}

COPY ./app /app/app

EXPOSE 8000

# One worker, deliberately. Each worker is a full copy of the weights, so
# scaling here means more replicas, not more processes.
CMD ["fastapi", "run", "--workers", "1", "--port", "8000", "app/main.py"]
