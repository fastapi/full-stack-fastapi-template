# Development Scripts

This directory contains helper scripts to streamline Docker development workflow.

## Docker Development Scripts

### `docker-dev.sh` / `docker-dev.bat`
Comprehensive Docker development helper with common operations.

**Linux/Mac:**
```bash
./scripts/docker-dev.sh [command]
```

**Windows:**
```cmd
scripts\docker-dev.bat [command]
```

**Available commands:**
- `setup` - Initial setup (check .env, generate secrets)
- `start` - Start all services
- `stop` - Stop all services  
- `restart [service]` - Restart specific service
- `rebuild [service]` - Rebuild specific service
- `reset` - Complete reset (removes all data)
- `status` - Check service status and health
- `logs [service]` - View logs
- `db-reset` - Reset database
- `shell [service]` - Open shell in container

### `docker-health.sh`
Quick health check for all services.

```bash
./scripts/docker-health.sh
```

## Quick Start

1. **Initial setup:**
   ```bash
   ./scripts/docker-dev.sh setup
   ```

2. **Check everything is working:**
   ```bash
   ./scripts/docker-health.sh
   ```

3. **View logs if issues:**
   ```bash
   ./scripts/docker-dev.sh logs
   ```

## Troubleshooting

If you encounter issues, see [DOCKER_TROUBLESHOOTING.md](../DOCKER_TROUBLESHOOTING.md) for detailed solutions.