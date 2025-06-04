#! /usr/bin/env bash

# Exit in case of error
set -e
# Print commands and their arguments as they are executed
set -x

# Navigate to the backend directory
cd backend
# Generate the OpenAPI schema from the FastAPI application
# This command executes a Python one-liner:
# - Imports the main FastAPI application (app.main)
# - Imports the json library
# - Accesses the app's OpenAPI schema (app.main.app.openapi())
# - Dumps the schema to a JSON string
# - Redirects the output to openapi.json in the parent (project root) directory
# Note: This step assumes that the necessary Python environment is active
# or that the FastAPI application and its dependencies can be imported.
python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
# Navigate back to the project root directory
cd ..
# Move the generated openapi.json to the frontend directory
mv openapi.json frontend/
# Navigate to the frontend directory
cd frontend
# Run the npm script to generate the API client code using the openapi.json
npm run generate-client
# Format the generated client code using Biome
npx biome format --write ./src/client
