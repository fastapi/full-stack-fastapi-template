#!/bin/bash
set -e

# Create the async database using createdb utility
createdb -U "$POSTGRES_USER" $POSTGRES_DB_ASYNC
# Create the test database
createdb -U "$POSTGRES_USER" $POSTGRES_TEST_DB
