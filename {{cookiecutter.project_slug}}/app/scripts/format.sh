#!/usr/bin/env bash

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py,alembic
black app --exclude=alembic
isort --skip=alembic app
