#!/usr/bin/env bash

set -e
set -x

# app/tests
pytest -W ignore::DeprecationWarning $1
