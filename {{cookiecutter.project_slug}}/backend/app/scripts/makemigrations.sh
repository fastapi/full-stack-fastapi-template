#!/bin/sh -e
set -x

alembic revision --autogenerate -m "$*"