#!/usr/bin/env bash

set -e
set -x
poetry run coverage run --source=app -m pytest
poetry run coverage report --show-missing
poetry run coverage html --title "${@-coverage}"
