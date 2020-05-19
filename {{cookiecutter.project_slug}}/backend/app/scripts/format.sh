#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --ignore-init-module-imports
black app
isort --recursive --apply app
