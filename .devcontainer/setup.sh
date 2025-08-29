#!/bin/bash
set -e

echo "Setting up development environment..."

# Install UV for Python package management
if ! command -v uv &> /dev/null; then
    echo "Installing UV for Python package management..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    # Add UV to PATH permanently
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
else
    echo "UV already installed"
fi

# Ensure UV is in PATH for this session
export PATH="$HOME/.local/bin:$PATH"

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
uv sync --dev
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm ci
cd ..

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
cd backend
uv run pre-commit install
cd ..

# Make scripts executable
chmod +x scripts/*.sh

# Create .gitpod directory if it doesn't exist
mkdir -p .gitpod

# Copy automations.yaml to .gitpod directory for Gitpod to find it
cp automations.yaml .gitpod/automations.yaml

# Open required ports for external access
echo "Opening required ports..."
gitpod environment port open 5173 --name "Frontend Preview" 2>/dev/null || echo "Port 5173 already open or not available"
gitpod environment port open 8000 --name "Backend API" 2>/dev/null || echo "Port 8000 already open or not available"
gitpod environment port open 8080 --name "Adminer DB Admin" 2>/dev/null || echo "Port 8080 already open or not available"

echo "Development environment setup complete!"
echo "All dependencies installed and configured."
echo "Use 'gitpod automations service start database' to start services"
