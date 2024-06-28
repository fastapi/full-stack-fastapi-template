#!/usr/bin/env bash

set -e
set -x

NO_COVERAGE=0

# Check for the --no-coverage flag
for arg in "$@"; do
    if [ "$arg" == "--no-coverage" ]; then
        NO_COVERAGE=1
        shift
        break
    fi
done

if [ $NO_COVERAGE -eq 0 ]; then
    coverage run --source=app -m pytest "$@"
    coverage report --show-missing
    coverage html --title "Coverage Report"
else
    pytest "$@"
fi