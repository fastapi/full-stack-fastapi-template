#!/usr/bin/env bash

# Exit in case of error
set -e
# Print commands and their arguments as they are executed
set -x

# Run Mypy for static type checking on the 'app' directory.
mypy app
# Run Ruff to check for linting errors in the 'app' directory.
# This command only reports errors, it does not fix them.
ruff check app
# Run Ruff formatter in check mode on the 'app' directory.
# This command reports files that need formatting without actually modifying them.
# It's useful for CI to verify that code is correctly formatted.
ruff format app --check
