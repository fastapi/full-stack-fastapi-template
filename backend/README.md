# Political Social Media Analysis Platform - Backend

This is the backend for the Political Social Media Analysis Platform, built with FastAPI, SQLModel, MongoDB, Redis, and Celery.

## Project Structure

```
backend/
├── app/
│   ├── api/                  # API routes
│   │   ├── api_v1/           # API v1 routes
│   │   │   ├── endpoints/    # API endpoints
│   │   │   └── api.py        # API router
│   │   ├── deps.py           # Dependency injection
│   │   └── main.py           # API router configuration
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Application configuration
│   │   ├── security.py       # Authentication and security
│   │   └── errors.py         # Error handling
│   ├── db/                   # Database models and connections
│   │   ├── models/           # SQLModel models for PostgreSQL
│   │   │   ├── user.py
│   │   │   └── item.py
│   │   ├── schemas/          # MongoDB schemas
│   │   │   ├── social_post.py
│   │   │   └── political_entity.py
│   │   ├── session.py        # Database session management
│   │   └── init_db.py        # Database initialization
│   ├── schemas/              # API schemas
│   │   ├── user.py
│   │   ├── item.py
│   │   └── common.py
│   ├── services/             # Business logic
│   │   ├── user.py
│   │   └── analysis.py
│   ├── tasks/                # Celery tasks
│   │   ├── celery_app.py     # Celery configuration
│   │   └── worker.py         # Background tasks
│   └── main.py               # FastAPI application entry point
├── tests/                    # Tests
├── Dockerfile                # Docker configuration
├── pyproject.toml            # Python project configuration
└── README.md                 # This file
```

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL databases in Python, designed for simplicity, compatibility, and robustness
- **MongoDB**: NoSQL database for storing social media data
- **Redis**: In-memory data structure store for caching and message broker
- **Celery**: Distributed task queue for background processing
- **JWT Authentication**: Secure authentication with JWT tokens
- **Dependency Injection**: Clean, modular code with FastAPI's dependency injection
- **Environment Variables**: Configuration via environment variables
- **Docker**: Containerized development and deployment

## Database Structure

The application uses two databases:

1. **PostgreSQL** (with SQLModel ORM)
   - User accounts and authentication
   - Application data

2. **MongoDB**
   - Social media posts
   - Political entities
   - Analytics data

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone the repository
2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
3. Start the development environment:
   ```bash
   docker-compose up -d
   ```

### API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Background Tasks

The application uses Celery for background tasks:

- Social media scraping
- Data analysis
- Report generation

You can monitor Celery tasks using Flower at http://localhost:5555

## Development

### Adding New Models

1. Create a new model in `app/db/models/` for SQL models or `app/db/schemas/` for MongoDB schemas
2. Create corresponding API schemas in `app/schemas/`
3. Create service functions in `app/services/`
4. Create API endpoints in `app/api/api_v1/endpoints/`

### Running Tests

```bash
docker-compose exec backend pytest
```

### Code Formatting and Linting

```bash
docker-compose exec backend ruff check .
docker-compose exec backend black .
docker-compose exec backend mypy .
```
