#! /usr/bin/env bash
set -e

hatch run production:python /app/app/tests_pre_start.py

bash ./scripts/test.sh "$@"
