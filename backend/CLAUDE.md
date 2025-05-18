# Backend - CLAUDE.md

This file provides guidance for Claude Code when working with the backend of this FastAPI project.

## Architecture Overview

- **FastAPI Framework**: Modern Python web framework with automatic API documentation
- **SQLModel**: Data modeling with SQLAlchemy core + Pydantic validation
- **PostgreSQL**: Database backend accessed through SQLModel
- **JWT Authentication**: Token-based authentication system
- **Alembic**: Database migration management
- **Pydantic**: Data validation and settings management
- **Email Integration**: User registration and password recovery

## Key Components

### Models (`app/models.py`)

- `User`: User account data with relationships
- `Item`: Example model with owner relationship
- Supporting Pydantic models for API validation

### Database (`app/core/db.py`)

- SQLModel configuration 
- Database connection management
- Session handling

### Config (`app/core/config.py`)

- Environment variable configuration
- Pydantic Settings class
- Secrets and connection strings
- Email configuration

### API Routes (`app/api/routes/`)

- `users.py`: User management endpoints
- `login.py`: Authentication endpoints
- `items.py`: Example CRUD resource
- `private.py`: Private test endpoint
- `utils.py`: Utility endpoints

### CRUD Operations (`app/crud.py`)

- Database access functions for all models
- Abstraction layer between API routes and database

### Core Utilities (`app/core/`)

- `security.py`: Password hashing, JWT token generation/verification

### Email Templates (`app/email-templates/`)

- MJML source templates
- HTML build output

### Tests (`app/tests/`)

- API route tests
- CRUD function tests
- Utility tests
- Initialization script tests

## Development Workflow

### Local Development

```bash
# Setup virtual environment
cd backend
uv sync
source .venv/bin/activate

# Run the application with live reload
fastapi run --reload app/main.py

# Or use Docker Compose for the full stack
docker compose watch
```

### Running Tests

```bash
# Run all tests
bash ./scripts/test.sh

# Run tests with Docker Compose
docker compose exec backend bash scripts/tests-start.sh

# Run specific tests or with options
docker compose exec backend bash scripts/tests-start.sh -xvs
```

### Database Migrations

```bash
# Create a new migration
docker compose exec backend bash -c "alembic revision --autogenerate -m 'Description of changes'"

# Apply migrations
docker compose exec backend bash -c "alembic upgrade head"
```

### Code Formatting and Linting

```bash
# Format code
bash ./scripts/format.sh

# Run linter
bash ./scripts/lint.sh
```

## API Authentication

- JWT tokens used for authentication
- Request User available through dependencies in `app/api/deps.py`
- Superuser routes protected with `current_active_superuser` dependency

## Common Files to Modify

- `app/models.py`: Add/edit data models
- `app/crud.py`: Add/edit database operations
- `app/api/routes/`: Add/edit API endpoints
- `app/core/config.py`: Update configuration settings

## Testing Guidelines

- All new features should include tests
- Test fixtures available in `app/tests/conftest.py`
- Utility functions for testing in `app/tests/utils/`
- Coverage report generated in `htmlcov/index.html`

## Deployment

- Uses Docker containers
- Multiple environment configurations via .env file
- Migrations run automatically on startup
- Initial superuser created on first run