#!/bin/bash

# CurriculumExtractor Development Environment Check
# This script verifies your development environment setup

set -e

echo "🔍 Checking CurriculumExtractor Development Environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 installed: $(command -v $1)"
        if [ ! -z "$3" ]; then
            echo "  Version: $($1 $3 2>&1 | head -1)"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $2 not found"
        return 1
    fi
}

# Check prerequisites
echo "📋 Prerequisites:"
echo ""

check_command "docker" "Docker" "--version" || MISSING=1
check_command "docker" "Docker Compose" "compose version" || MISSING=1
check_command "node" "Node.js" "--version" || MISSING=1
check_command "npm" "npm" "--version" || MISSING=1
check_command "uv" "uv (Python package manager)" "--version" || MISSING=1
check_command "python3" "Python 3" "--version" || MISSING=1

echo ""
echo "🔐 Environment Configuration:"
echo ""

# Check .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check for placeholders
    if grep -q "YOUR-PROJECT-REF" .env; then
        echo -e "${YELLOW}⚠${NC}  Supabase credentials not configured (still has placeholders)"
        echo "   → Run: open https://app.supabase.com"
        echo "   → Update DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY in .env"
        NEEDS_SUPABASE=1
    else
        echo -e "${GREEN}✓${NC} Supabase credentials configured"
    fi
    
    # Check SECRET_KEY
    if grep -q "SECRET_KEY=changethis" .env; then
        echo -e "${RED}✗${NC} SECRET_KEY still using default 'changethis'"
        MISSING=1
    else
        echo -e "${GREEN}✓${NC} SECRET_KEY configured"
    fi
    
    # Check FIRST_SUPERUSER_PASSWORD
    if grep -q "FIRST_SUPERUSER_PASSWORD=changethis" .env; then
        echo -e "${YELLOW}⚠${NC}  FIRST_SUPERUSER_PASSWORD still using default 'changethis'"
        echo "   → Change this to a strong password before deploying"
    else
        echo -e "${GREEN}✓${NC} FIRST_SUPERUSER_PASSWORD configured"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "   → Copy from template or create one"
    MISSING=1
fi

echo ""
echo "📦 Dependencies:"
echo ""

# Check frontend dependencies
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC}  Frontend dependencies not installed"
    echo "   → Run: cd frontend && npm install"
    MISSING_DEPS=1
fi

# Check backend dependencies (if using local Python)
if [ -d "backend/.venv" ]; then
    echo -e "${GREEN}✓${NC} Backend virtual environment exists"
else
    echo -e "${YELLOW}⚠${NC}  Backend virtual environment not found (OK if using Docker)"
    echo "   → For local development: cd backend && uv sync"
fi

echo ""
echo "🐳 Docker Status:"
echo ""

# Check if Docker is running
if docker info &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker daemon is running"
else
    echo -e "${RED}✗${NC} Docker daemon is not running"
    echo "   → Start Docker Desktop"
    MISSING=1
fi

echo ""
echo "📝 Summary:"
echo ""

if [ ! -z "$MISSING" ]; then
    echo -e "${RED}✗ Setup incomplete${NC} - Please install missing prerequisites"
    exit 1
elif [ ! -z "$NEEDS_SUPABASE" ]; then
    echo -e "${YELLOW}⚠ Setup incomplete${NC} - Supabase credentials needed"
    echo ""
    echo "Next steps:"
    echo "1. Create Supabase project: https://app.supabase.com"
    echo "2. Get your credentials from project settings"
    echo "3. Update .env file with your Supabase credentials"
    echo "4. Run: docker compose watch"
    echo ""
    echo "See SETUP_STATUS.md for detailed instructions"
    exit 1
elif [ ! -z "$MISSING_DEPS" ]; then
    echo -e "${YELLOW}⚠ Dependencies incomplete${NC}"
    echo "   → Run: cd frontend && npm install"
    exit 1
else
    echo -e "${GREEN}✓ Environment setup complete!${NC}"
    echo ""
    echo "🚀 Ready to start development:"
    echo "   → Run: docker compose watch"
    echo "   → Open: http://localhost:5173"
    echo ""
    exit 0
fi

