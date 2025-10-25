#!/bin/bash
# Docker Development Helper Script
# Provides common Docker operations for the FastAPI Full Stack Template

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        log_error ".env file not found!"
        log_info "Creating .env from template..."
        if [ -f .env.example ]; then
            cp .env.example .env
            log_success ".env file created from .env.example"
        else
            log_error "No .env.example found. Please create .env manually."
            exit 1
        fi
    fi
}

# Generate secret keys
generate_secrets() {
    log_info "Generating new secret keys..."
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    POSTGRES_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
    
    # Update .env file
    sed -i.bak "s/SECRET_KEY=changethis/SECRET_KEY=${SECRET_KEY}/" .env
    sed -i.bak "s/POSTGRES_PASSWORD=changethis/POSTGRES_PASSWORD=${POSTGRES_PASSWORD}/" .env
    
    log_success "Secret keys generated and updated in .env"
}

# Reset everything
reset() {
    log_warning "This will remove all containers, volumes, and data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Stopping all services..."
        docker-compose down -v --remove-orphans
        
        log_info "Removing unused Docker resources..."
        docker system prune -f
        
        log_info "Starting fresh..."
        docker-compose up -d --build
        
        log_success "Reset complete!"
    else
        log_info "Reset cancelled."
    fi
}

# Quick status check
status() {
    log_info "Checking service status..."
    docker-compose ps
    
    echo
    log_info "Service health checks:"
    
    # Check backend
    if curl -s http://localhost:8000/api/v1/utils/health-check/ > /dev/null; then
        log_success "Backend API: ✓ Healthy"
    else
        log_error "Backend API: ✗ Unhealthy"
    fi
    
    # Check frontend
    if curl -s -I http://localhost:5173 > /dev/null; then
        log_success "Frontend: ✓ Accessible"
    else
        log_error "Frontend: ✗ Not accessible"
    fi
    
    # Check database
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        log_success "Database: ✓ Ready"
    else
        log_error "Database: ✗ Not ready"
    fi
}

# View logs
logs() {
    SERVICE=${1:-""}
    if [ -z "$SERVICE" ]; then
        log_info "Showing logs for all services..."
        docker-compose logs --tail=50 -f
    else
        log_info "Showing logs for $SERVICE..."
        docker-compose logs --tail=50 -f "$SERVICE"
    fi
}

# Restart specific service
restart() {
    SERVICE=${1:-""}
    if [ -z "$SERVICE" ]; then
        log_error "Please specify a service to restart"
        log_info "Available services: backend, frontend, db, adminer"
        exit 1
    fi
    
    log_info "Restarting $SERVICE..."
    docker-compose restart "$SERVICE"
    log_success "$SERVICE restarted"
}

# Rebuild specific service
rebuild() {
    SERVICE=${1:-""}
    if [ -z "$SERVICE" ]; then
        log_error "Please specify a service to rebuild"
        log_info "Available services: backend, frontend"
        exit 1
    fi
    
    log_info "Rebuilding $SERVICE..."
    docker-compose up -d --build "$SERVICE"
    log_success "$SERVICE rebuilt"
}

# Database operations
db_reset() {
    log_warning "This will reset the database and lose all data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Stopping database..."
        docker-compose stop db
        
        log_info "Removing database volume..."
        docker volume rm full-stack-fastapi-template_app-db-data 2>/dev/null || true
        
        log_info "Starting database..."
        docker-compose up -d db
        
        log_info "Waiting for database to be ready..."
        sleep 10
        
        log_info "Running migrations..."
        docker-compose exec backend alembic upgrade head
        
        log_success "Database reset complete!"
    fi
}

# Show help
show_help() {
    echo "Docker Development Helper for FastAPI Full Stack Template"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  setup           Initial setup (check .env, generate secrets)"
    echo "  start           Start all services"
    echo "  stop            Stop all services"
    echo "  restart [svc]   Restart specific service or all services"
    echo "  rebuild [svc]   Rebuild specific service"
    echo "  reset           Complete reset (removes all data)"
    echo "  status          Check service status and health"
    echo "  logs [svc]      View logs (all services or specific service)"
    echo "  db-reset        Reset database (removes all data)"
    echo "  shell [svc]     Open shell in service container"
    echo "  help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0 setup                 # Initial setup"
    echo "  $0 start                 # Start all services"
    echo "  $0 logs backend          # View backend logs"
    echo "  $0 restart frontend      # Restart frontend service"
    echo "  $0 shell backend         # Open shell in backend container"
}

# Open shell in container
shell() {
    SERVICE=${1:-"backend"}
    log_info "Opening shell in $SERVICE container..."
    
    case $SERVICE in
        backend)
            docker-compose exec backend bash
            ;;
        frontend)
            docker-compose exec frontend sh
            ;;
        db)
            docker-compose exec db psql -U postgres -d app
            ;;
        *)
            log_error "Unknown service: $SERVICE"
            log_info "Available services: backend, frontend, db"
            exit 1
            ;;
    esac
}

# Main command handling
case "${1:-help}" in
    setup)
        check_env
        generate_secrets
        log_info "Starting services..."
        docker-compose up -d --build
        log_success "Setup complete! Services are starting..."
        ;;
    start)
        check_env
        docker-compose up -d
        log_success "Services started"
        ;;
    stop)
        docker-compose down
        log_success "Services stopped"
        ;;
    restart)
        restart "$2"
        ;;
    rebuild)
        rebuild "$2"
        ;;
    reset)
        reset
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    db-reset)
        db_reset
        ;;
    shell)
        shell "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac