#!/usr/bin/env bash
set -e
bash scripts/prestart.sh
exec fastapi run --workers "${WEB_CONCURRENCY:-1}" --host 0.0.0.0 --port "$PORT" app/main.py
