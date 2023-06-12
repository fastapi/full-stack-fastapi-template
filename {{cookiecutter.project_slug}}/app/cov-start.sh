#! /usr/bin/env bash
set -e

python /app/app/tests_pre_start.py

bash ./scripts/cov.sh "$@"
