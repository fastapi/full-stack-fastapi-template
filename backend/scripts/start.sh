#!/usr/bin/env bash
set -e
bash scripts/prestart.sh
exec fastapi run --workers 4 --host 0.0.0.0 --port "$PORT" app/main.py
