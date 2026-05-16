#!/usr/bin/env bash

set -e
set -x

mypy app
ty check app
ruff check app
ruff format app --check
