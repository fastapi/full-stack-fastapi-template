#! /usr/bin/env bash
set -e
set -x

# Use the same pre-start script as the main application
python app/backend_pre_start.py

bash scripts/test.sh "$@"
