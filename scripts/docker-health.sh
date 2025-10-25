#!/bin/bash
# Docker Health Check Script
# Quick health check for all services

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "FastAPI Full Stack Template - Health Check"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Check if docker-compose.yml exists
if [ ! -f docker-compose.yml ]; then
    echo -e "${RED}✗ docker-compose.yml not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ docker-compose.yml found${NC}"

# Check services
echo
echo "Service Status:"
echo "---------------"

services=("db" "backend" "frontend")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps "$service" | grep -q "Up"; then
        echo -e "${GREEN}✓ $service: Running${NC}"
    else
        echo -e "${RED}✗ $service: Not running${NC}"
        all_healthy=false
    fi
done

# Health checks
echo
echo "Health Checks:"
echo "--------------"

# Database
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database: Ready${NC}"
else
    echo -e "${RED}✗ Database: Not ready${NC}"
    all_healthy=false
fi

# Backend API
if curl -s http://localhost:8000/api/v1/utils/health-check/ > /dev/null; then
    echo -e "${GREEN}✓ Backend API: Healthy${NC}"
else
    echo -e "${RED}✗ Backend API: Unhealthy${NC}"
    all_healthy=false
fi

# Frontend
if curl -s -I http://localhost:5173 > /dev/null; then
    echo -e "${GREEN}✓ Frontend: Accessible${NC}"
else
    echo -e "${RED}✗ Frontend: Not accessible${NC}"
    all_healthy=false
fi

echo
if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}🎉 All services are healthy!${NC}"
    echo
    echo "Access your application:"
    echo "• Frontend: http://localhost:5173"
    echo "• Backend API: http://localhost:8000"
    echo "• API Docs: http://localhost:8000/docs"
    echo "• Database Admin: http://localhost:8080"
else
    echo -e "${RED}⚠️  Some services have issues${NC}"
    echo
    echo "Try running: ./scripts/docker-dev.sh status"
    echo "Or check logs: ./scripts/docker-dev.sh logs"
fi