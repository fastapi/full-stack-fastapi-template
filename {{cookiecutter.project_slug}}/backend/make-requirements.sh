#!/usr/bin/env bash

poetry export -f requirements.txt -o requirements.txt $(if [[ "$1" == "--dev" ]]; then echo "--dev"; fi)
