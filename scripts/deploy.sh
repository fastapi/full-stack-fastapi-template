#!/usr/bin/env sh

# Exit in case of error
set -e

# Define variables
HELM_CHART_DIR="./kubernetes/charts/sdp"
RELEASE_NAME="sdp"
BACKEND_PORT=8000
FRONTEND_PORT=5173
ADMINER_PORT=8080
TIMEOUT=300  # 5 minute timeout

# Main deployment
echo "Deploying Helm chart..."
helm upgrade --install $RELEASE_NAME $HELM_CHART_DIR
