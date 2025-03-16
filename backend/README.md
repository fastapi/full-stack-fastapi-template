# FastAPI Backend Template

This is a modern backend template built with FastAPI, SQLModel, PostgreSQL, and JWT authentication.

## Project Structure

```
backend/
├── app/
│   ├── api/                  # API routes
│   │   ├── api_v1/           # API v1 routes
│   │   │   ├── endpoints/    # API endpoints
│   │   │   └── api.py        # API router
│   │   └── deps.py           # Dependency injection
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Application configuration
│   │   ├── security.py       # Authentication and security
│   │   └── errors.py         # Error handling
│   ├── db/                   # Database models and connections
│   │   ├── models/           # SQLModel models
│   │   │   ├── user.py
│   │   │   └── item.py
│   │   └── session.py        # Database session management
│   ├── schemas/              # API schemas (Pydantic models)
│   │   ├── user.py
│   │   ├── item.py
│   │   └── common.py         # Shared schema definitions
│   ├── services/             # Business logic services
│   │   └── user.py           # User service
│   └── main.py               # FastAPI application entry point
├── tests/                    # Tests
├── Dockerfile                # Docker configuration
├── pyproject.toml            # Python project configuration
└── README.md                 # This file
```

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL databases in Python, designed for simplicity, compatibility, and robustness
- **JWT Authentication**: Secure authentication with JWT tokens
- **Dependency Injection**: Clean, modular code with FastAPI's dependency injection
- **Environment Variables**: Configuration via environment variables
- **Docker**: Containerized development and deployment
- **UUID Primary Keys**: All database models use UUIDs as primary keys

## Database Structure

The application uses **PostgreSQL** with SQLModel ORM for:
- User accounts and authentication
- Application data storage
- Relationship management

### UUID Migration Notes

As of July 2024, the project has migrated from using integer IDs to UUIDs for all database models. This change improves:
- Security (IDs are not sequential or predictable)
- Distributed system compatibility
- Data privacy

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- uv (for dependency management)

### Development Setup

1. Clone the repository
2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
3. Install dependencies using uv:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip sync
   ```
4. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running with Docker

```bash
docker-compose up -d
```

### API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Adding New Models

1. Create a new model in `app/db/models/`
2. Create corresponding API schemas in `app/schemas/`
3. Create service functions in `app/services/`
4. Create API endpoints in `app/api/api_v1/endpoints/`

### Running Tests

```bash
pytest
```

### Code Formatting and Linting

```bash
ruff check .
ruff format .
mypy .
```

## Dependency Management with uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

- `uv venv` - Create a virtual environment
- `uv pip sync` - Install dependencies from uv.lock
- `uv pip add <package>` - Add a new dependency
