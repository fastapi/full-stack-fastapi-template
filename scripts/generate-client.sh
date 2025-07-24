#! /usr/bin/env bash

set -e
set -x

cd backend
python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
cp openapi.json frontend/
cd frontend
npm run generate-client
npx biome format --write ./src/client

cd ..
mv openapi.json frontend-nextjs/
cd frontend-nextjs
npm run generate-client
npx biome format --write ./src/client
