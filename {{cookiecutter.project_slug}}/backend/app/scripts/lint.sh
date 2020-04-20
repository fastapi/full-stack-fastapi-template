#!/usr/bin/env bash

set -e
set -x

mypy app
black app --check
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --check-only app
vulture app --min-confidence 70
flake8 --max-line-length 88 --exclude=__init__.py
