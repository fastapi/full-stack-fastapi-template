#!/bin/sh
# Install locked dependencies while outbound access is available, before services start.
set -eu
export UV_PROJECT_ENVIRONMENT=/workspace/venv
export UV_CACHE_DIR=/workspace/uv-cache
export BUN_INSTALL_CACHE_DIR=/workspace/bun-cache
uv sync --frozen --all-packages --all-groups
bun install --frozen-lockfile
cd frontend
# Use same-origin API requests; the private application URL is assigned later.
export VITE_API_URL=
bun run build
