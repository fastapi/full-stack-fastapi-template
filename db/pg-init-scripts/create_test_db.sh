#!/bin/bash
# source: https://dev.to/bgord/multiple-postgres-databases-in-a-single-docker-container-417l

set -e
set -u

function create_database() {
	local database=$1
	echo "  Creating db '$database' for user '$POSTGRES_USER'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
		    CREATE DATABASE $database;
	EOSQL
}

if [ -n "$POSTGRES_TEST_DB" ]; then
	create_database $POSTGRES_TEST_DB
fi
