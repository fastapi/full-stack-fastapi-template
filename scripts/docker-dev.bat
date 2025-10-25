@echo off
REM Docker Development Helper Script for Windows
REM Provides common Docker operations for the FastAPI Full Stack Template

setlocal enabledelayedexpansion

REM Check if .env file exists
:check_env
if not exist .env (
    echo [ERROR] .env file not found!
    if exist .env.example (
        echo [INFO] Creating .env from template...
        copy .env.example .env >nul
        echo [SUCCESS] .env file created from .env.example
    ) else (
        echo [ERROR] No .env.example found. Please create .env manually.
        exit /b 1
    )
)
goto :eof

REM Generate secret keys
:generate_secrets
echo [INFO] Generating new secret keys...
for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set SECRET_KEY=%%i
for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(16))"') do set POSTGRES_PASSWORD=%%i

REM Update .env file (basic replacement)
powershell -Command "(gc .env) -replace 'SECRET_KEY=changethis', 'SECRET_KEY=!SECRET_KEY!' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'POSTGRES_PASSWORD=changethis', 'POSTGRES_PASSWORD=!POSTGRES_PASSWORD!' | Out-File -encoding ASCII .env"

echo [SUCCESS] Secret keys generated and updated in .env
goto :eof

REM Reset everything
:reset
echo [WARNING] This will remove all containers, volumes, and data!
set /p confirm="Are you sure? (y/N): "
if /i "!confirm!"=="y" (
    echo [INFO] Stopping all services...
    docker-compose down -v --remove-orphans
    
    echo [INFO] Removing unused Docker resources...
    docker system prune -f
    
    echo [INFO] Starting fresh...
    docker-compose up -d --build
    
    echo [SUCCESS] Reset complete!
) else (
    echo [INFO] Reset cancelled.
)
goto :eof

REM Quick status check
:status
echo [INFO] Checking service status...
docker-compose ps

echo.
echo [INFO] Service health checks:

REM Check backend
curl -s http://localhost:8000/api/v1/utils/health-check/ >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Backend API: ✓ Healthy
) else (
    echo [ERROR] Backend API: ✗ Unhealthy
)

REM Check frontend
curl -s -I http://localhost:5173 >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Frontend: ✓ Accessible
) else (
    echo [ERROR] Frontend: ✗ Not accessible
)

REM Check database
docker-compose exec -T db pg_isready -U postgres >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Database: ✓ Ready
) else (
    echo [ERROR] Database: ✗ Not ready
)
goto :eof

REM View logs
:logs
if "%~2"=="" (
    echo [INFO] Showing logs for all services...
    docker-compose logs --tail=50 -f
) else (
    echo [INFO] Showing logs for %~2...
    docker-compose logs --tail=50 -f %~2
)
goto :eof

REM Restart specific service
:restart_service
if "%~2"=="" (
    echo [ERROR] Please specify a service to restart
    echo [INFO] Available services: backend, frontend, db, adminer
    exit /b 1
)

echo [INFO] Restarting %~2...
docker-compose restart %~2
echo [SUCCESS] %~2 restarted
goto :eof

REM Rebuild specific service
:rebuild
if "%~2"=="" (
    echo [ERROR] Please specify a service to rebuild
    echo [INFO] Available services: backend, frontend
    exit /b 1
)

echo [INFO] Rebuilding %~2...
docker-compose up -d --build %~2
echo [SUCCESS] %~2 rebuilt
goto :eof

REM Database reset
:db_reset
echo [WARNING] This will reset the database and lose all data!
set /p confirm="Are you sure? (y/N): "
if /i "!confirm!"=="y" (
    echo [INFO] Stopping database...
    docker-compose stop db
    
    echo [INFO] Removing database volume...
    docker volume rm full-stack-fastapi-template_app-db-data 2>nul
    
    echo [INFO] Starting database...
    docker-compose up -d db
    
    echo [INFO] Waiting for database to be ready...
    timeout /t 10 /nobreak >nul
    
    echo [INFO] Running migrations...
    docker-compose exec backend alembic upgrade head
    
    echo [SUCCESS] Database reset complete!
)
goto :eof

REM Open shell in container
:shell
set service=%~2
if "!service!"=="" set service=backend

echo [INFO] Opening shell in !service! container...

if "!service!"=="backend" (
    docker-compose exec backend bash
) else if "!service!"=="frontend" (
    docker-compose exec frontend sh
) else if "!service!"=="db" (
    docker-compose exec db psql -U postgres -d app
) else (
    echo [ERROR] Unknown service: !service!
    echo [INFO] Available services: backend, frontend, db
    exit /b 1
)
goto :eof

REM Show help
:show_help
echo Docker Development Helper for FastAPI Full Stack Template
echo.
echo Usage: %~nx0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo   setup           Initial setup (check .env, generate secrets)
echo   start           Start all services
echo   stop            Stop all services
echo   restart [svc]   Restart specific service or all services
echo   rebuild [svc]   Rebuild specific service
echo   reset           Complete reset (removes all data)
echo   status          Check service status and health
echo   logs [svc]      View logs (all services or specific service)
echo   db-reset        Reset database (removes all data)
echo   shell [svc]     Open shell in service container
echo   help            Show this help message
echo.
echo Examples:
echo   %~nx0 setup                 # Initial setup
echo   %~nx0 start                 # Start all services
echo   %~nx0 logs backend          # View backend logs
echo   %~nx0 restart frontend      # Restart frontend service
echo   %~nx0 shell backend         # Open shell in backend container
goto :eof

REM Main command handling
if "%~1"=="" goto show_help
if "%~1"=="help" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="-h" goto show_help

if "%~1"=="setup" (
    call :check_env
    call :generate_secrets
    echo [INFO] Starting services...
    docker-compose up -d --build
    echo [SUCCESS] Setup complete! Services are starting...
) else if "%~1"=="start" (
    call :check_env
    docker-compose up -d
    echo [SUCCESS] Services started
) else if "%~1"=="stop" (
    docker-compose down
    echo [SUCCESS] Services stopped
) else if "%~1"=="restart" (
    call :restart_service %*
) else if "%~1"=="rebuild" (
    call :rebuild %*
) else if "%~1"=="reset" (
    call :reset
) else if "%~1"=="status" (
    call :status
) else if "%~1"=="logs" (
    call :logs %*
) else if "%~1"=="db-reset" (
    call :db_reset
) else if "%~1"=="shell" (
    call :shell %*
) else (
    echo [ERROR] Unknown command: %~1
    call :show_help
    exit /b 1
)