#! /usr/bin/env bash

set -e
set -x

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

python app/tests_pre_start.py

bash scripts/test.sh "$@"
