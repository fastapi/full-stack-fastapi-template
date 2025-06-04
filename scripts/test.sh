#! /usr/bin/env sh

# Exit in case of error
set -e
# Print commands and their arguments as they are executed
set -x

# Build the Docker images for all services
docker compose build

# Stop and remove any existing containers, volumes, and orphaned containers
# This ensures a clean environment before starting the tests
docker compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error

# Start all services in detached mode (in the background)
docker compose up -d

# Execute the backend test script (scripts/tests-start.sh) inside the 'backend' container
# -T disables pseudo-TTY allocation, suitable for non-interactive scripts
# "$@" forwards all arguments passed to this script to the tests-start.sh script
docker compose exec -T backend bash scripts/tests-start.sh "$@"

# Stop and remove all containers, volumes, and orphaned containers after tests are done
docker compose down -v --remove-orphans
