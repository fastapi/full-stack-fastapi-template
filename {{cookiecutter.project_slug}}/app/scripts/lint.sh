#!/usr/bin/env bash

set -x

mypy app --exclude=alembic
black app --check --exclude=alembic
isort --check-only app --skip=alembic
flake8 --exclude=alembic --max-line-length=88 --exclude=.git,__pycache__,__init__.py,.mypy_cache,.pytest_cache
