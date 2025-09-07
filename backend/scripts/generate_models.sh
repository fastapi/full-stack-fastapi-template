#! /usr/bin/env bash

# Simple SQLModel generation script
# Read database configuration from .env file

set -e
set -x

# Read .env file
source ../../.env

# Execute sqlacodegen
sqlacodegen --generator sqlmodels "$DATABASE_SOURCE_DSN" --outfile ../app/generated_sqlmodels.py

echo "SQLModel code generated successfully: ../app/generated_sqlmodels.py"
