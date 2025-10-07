SHELL := /bin/bash

.PHONY: dev
dev:
	uv sync
	uv run fastapi dev app/main.py --host 0.0.0.0 --reload
