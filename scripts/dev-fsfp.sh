#! /usr/bin/env bash

# Exit in case of error
set -e

if [ ! -d ./full-stack-fastapi-postgresql ] ; then
    echo "Run this script from outside the project, to generate a sibling dev-fsfp project with independent git"
    exit 1
fi

rm -rf ./dev-fsfp

cookiecutter --config-file ./full-stack-fastapi-postgresql/dev-fsfp-config.yml --no-input -f ./full-stack-fastapi-postgresql
