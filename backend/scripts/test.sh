#!/usr/bin/env bash

set -e
set -x

NO_COVERAGE=0
MESSAGE="Coverage Report"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-coverage)
            NO_COVERAGE=1
            ;;
        --message=*)
            MESSAGE="${1#*=}"
            ;;
        *)
            TEST_PATH="$1"
            ;;
    esac
    shift
done

if [ $NO_COVERAGE -eq 0 ]; then
    coverage run --source=app -m pytest ${TEST_PATH}
    coverage report --show-missing
    coverage html --title "$MESSAGE"
else
    pytest ${TEST_PATH}
fi
