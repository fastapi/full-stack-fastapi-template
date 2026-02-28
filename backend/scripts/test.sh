#!/usr/bin/env bash

set -e
set -x

coverage run -m pytest tests/unit/ tests/integration/
coverage report
coverage html --title "${@-coverage}"
