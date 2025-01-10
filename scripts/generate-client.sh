#! /usr/bin/env bash

set -e
set -x

cd backend
python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
mv openapi.json frontend/
cd frontend
pnpm run generate-client
pnpm exec biome format --write ./src/client
