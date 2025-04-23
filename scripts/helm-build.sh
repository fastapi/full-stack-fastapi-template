#!/usr/bin/env sh

# Exit in case of error
set -e

# Define variables
HELM_CHART_DIR="./helm"

# Package the Helm chart
echo "Packaging Helm chart from $HELM_CHART_DIR..."
helm package $HELM_CHART_DIR

echo "Helm chart packaged successfully!"
