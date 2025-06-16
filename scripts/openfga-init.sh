#!/bin/bash

set -e

# Wait for dependencies to be ready
sleep 20

echo "Creating FGA store..."
sleep 1
echo '.'
sleep 1
echo '.'
sleep 1
echo '.'
sleep 1
echo '.'
STORE_ID=$(curl -v -s -X POST http://openfga:8085/stores -H 'Content-Type: application/json' -d '{"name": "my-app"}' | jq -r '.id')
if [ -z "$STORE_ID" ]; then
  echo "Error: Failed to create FGA store. Exiting."
  exit 1
fi
echo "FGA Store ID: $STORE_ID"

echo "Creating authorization model from /my-app_openfga/model.json..."
if [ ! -f /Scripts/fga/model.json ]; then
  echo "Error: Authorization model file not found at /my-app_openfga/model.json. Exiting."
  exit 1
fi
AUTH_MODEL_ID=$(curl -s -X POST http://openfga:8085/stores/$STORE_ID/authorization-models -H 'Content-Type: application/json' -d @/Scripts/fga/model.json | jq -r '.authorization_model_id')
if [ -z "$AUTH_MODEL_ID" ]; then
  echo "Error: Failed to create authorization model. Exiting."
  exit 1
fi
echo "Authorization Model ID: $AUTH_MODEL_ID"

# Save variables to a file
printf "{\n  \"storeId\": \"%s\",\n  \"authModelId\": \"%s\"\n}" "$STORE_ID" "$AUTH_MODEL_ID" > /home/fga_variables.json

echo "Initialization complete. Keeping the container running..."
wait 