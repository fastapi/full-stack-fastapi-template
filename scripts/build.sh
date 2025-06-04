#! /usr/bin/env sh

# Exit in case of error
set -e

# Set the TAG for Docker images, and exit if not provided
# TAG is typically the version or a git commit hash
TAG=${TAG?Variable not set} \
# Set the FRONTEND_ENV to 'production' if not already set
# This ensures the frontend is built with production optimizations
FRONTEND_ENV=${FRONTEND_ENV-production} \
# Build the Docker images using docker-compose
# The -f flag specifies the docker-compose file to use
docker-compose \
-f docker-compose.yml \
build
