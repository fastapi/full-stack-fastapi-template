#! /usr/bin/env bash

set -e
set -x

cd backend
python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
cp openapi.json next/
mv openapi.json frontend/

# Generate React client
cd frontend
npm run generate-client
npx biome format --write ./src/client


# Generate NextJS client
cd ../next
npm run generate-client
npx biome format --write ./src/client
