#! /usr/bin/env bash

#! /usr/bin/env bash

# Exit in case of error
set -e

# Stop and remove any existing containers, volumes, and orphaned containers
# This ensures a clean environment before starting the tests
docker-compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error

# On Linux systems, remove __pycache__ directories.
# Note: Using sudo here might indicate a permissions issue if these files are not owned by the current user.
# __pycache__ directories are created by Python and generally should not require sudo for removal.
if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

# Build the Docker images for all services
docker-compose build
# Start all services in detached mode (in the background)
docker-compose up -d
# Execute the backend test script (scripts/tests-start.sh) inside the 'backend' container
# -T disables pseudo-TTY allocation, suitable for non-interactive scripts
# "$@" forwards all arguments passed to this script to the tests-start.sh script
docker-compose exec -T backend bash scripts/tests-start.sh "$@"

# Note: Unlike test.sh, this script does not run `docker-compose down` at the end.
# This means the services will remain running after the tests complete,
# potentially for inspection or further local development.
