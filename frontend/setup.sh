#!/bin/bash

echo "🚀 Starting SaaS Front-end Setup..."

# 1. Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it from https://nodejs.org/"
    exit 1
fi

# 2. Ensure pnpm is installed (The fast, isolated package manager)
if ! command -v pnpm &> /dev/null; then
    echo "📦 pnpm not found. Installing globally..."
    npm install -g pnpm
fi

# 3. Install dependencies (The 'venv' equivalent)
echo "📥 Installing project dependencies..."
pnpm install

# 4. Generate GraphQL types from your FastAPI backend
echo "🧬 Generating TypeScript types from GraphQL schema..."
# Note: Your FastAPI server must be running for this to work
npm run generate || echo "⚠️ Warning: Could not connect to backend to generate types."

echo "✅ Setup complete! Run 'pnpm dev' to start the application."