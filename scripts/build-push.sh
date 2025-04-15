#!/bin/bash

# Set your Docker Hub username
DOCKER_USERNAME="dperezsa"
VERSION="1.0.0"

# Build backend image
echo "Building backend image..."
docker build -t ${DOCKER_USERNAME}/sdp-backend:${VERSION} -f backend/Dockerfile backend/

# Build frontend image
echo "Building frontend image..."
docker build -t ${DOCKER_USERNAME}/sdp-frontend:${VERSION} -f frontend/Dockerfile frontend/

# Push images to Docker Hub
echo "Pushing images to Docker Hub..."
docker push ${DOCKER_USERNAME}/sdp-backend:${VERSION}
docker push ${DOCKER_USERNAME}/sdp-frontend:${VERSION}

echo "Done!" 