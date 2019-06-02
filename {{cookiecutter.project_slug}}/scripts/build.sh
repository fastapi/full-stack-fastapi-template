#! /usr/bin/env sh

# Exit in case of error
set -e

if [ -z ${TAG} ]; then
    echo "Variable TAG must be provided"
    exit 1
fi

TAG=${TAG} \
FRONTEND_ENV=${FRONTEND_ENV-production} \
docker-compose \
-f docker-compose.deploy.build.yml \
-f docker-compose.deploy.images.yml \
config > docker-stack.yml

docker-compose -f docker-stack.yml build
