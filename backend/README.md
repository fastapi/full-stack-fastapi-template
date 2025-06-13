# Kondition Backend - FastAPI Documentation

## Overview

This is the FastAPI backend for the Kondition fitness motivator application. It provides a robust API for user management, authentication, and data storage to support the mobile frontend.

## Tech Stack

- **FastAPI**: High-performance Python web framework
- **SQLModel**: SQL database ORM combining SQLAlchemy and Pydantic
- **PostgreSQL**: Relational database
- **Alembic**: Database migration tool
- **JWT**: JSON Web Tokens for authentication
- **Docker**: Containerization for deployment
- **Sentry**: Error tracking and monitoring

## Project Structure

```
backend/
├── app/                      # Main application package
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── crud.py               # CRUD operations
│   ├── models.py             # Data models
│   ├── utils.py              # Utility functions
│   ├── alembic/              # Database migrations
│   ├── api/                  # API endpoints
│   │   ├── routes/           # Route definitions
│   │   │   ├── login.py      # Authentication endpoints
│   │   │   ├── users.py      # User management endpoints
│   │   │   ├── items.py      # Item endpoints
│   │   │   └── ...           # Other endpoint modules
│   │   ├── deps.py           # Dependency injection
│   │   └── main.py           # API router configuration
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Application configuration
│   │   ├── security.py       # Security utilities
│   │   └── db.py             # Database connection
│   └── tests/                # Test suite
├── Dockerfile                # Docker configuration
├── pyproject.toml            # Python project metadata
└── alembic.ini               # Alembic configuration
```

## API Endpoints

### Authentication

#### Login

```
POST /api/v1/login/access-token
```

Authenticates a user and returns a JWT access token.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Test Token

```
POST /api/v1/login/test-token
```

Tests if the current token is valid and returns the user information.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "John Doe"
}
```

#### Password Recovery

```
POST /api/v1/password-recovery/{email}
```

Initiates the password recovery process for a user.

**Response:**
```json
{
  "message": "Password recovery email sent"
}
```

#### Reset Password

```
POST /api/v1/reset-password/
```

Resets a user's password using a token.

**Request Body:**
```json
{
  "token": "recovery-token",
  "new_password": "new-password123"
}
```

**Response:**
```json
{
  "message": "Password updated successfully"
}
```

### User Management

#### Create User (Admin)

```
POST /api/v1/users/
```

Creates a new user (admin only).

**Request Body:**
```json
{
  "email": "new-user@example.com",
  "password": "password123",
  "full_name": "New User",
  "is_superuser": false
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "new-user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "New User"
}
```

#### Get Current User

```
GET /api/v1/users/me
```

Returns the current user's information.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "John Doe"
}
```

#### Update Current User

```
PATCH /api/v1/users/me
```

Updates the current user's information.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "email": "updated-email@example.com"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "updated-email@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Updated Name"
}
```

#### Update Password

```
PATCH /api/v1/users/me/password
```

Updates the current user's password.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "current_password": "current-password",
  "new_password": "new-password123"
}
```

**Response:**
```json
{
  "message": "Password updated successfully"
}
```

#### Delete Current User

```
DELETE /api/v1/users/me
```

Deletes the current user's account.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

#### User Registration

```
POST /api/v1/users/signup
```

Registers a new user without admin privileges.

**Request Body:**
```json
{
  "email": "new-user@example.com",
  "password": "password123",
  "full_name": "New User"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "new-user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "New User"
}
```

### Additional Endpoints

The API includes additional endpoints for item management and other features that will be implemented in future sprints.

## Data Models

### User

```python
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    items: list["Item"] = Relationship(back_populates="owner")
```

### Item

```python
class Item(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: str | None = None
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="items")
```

## Authentication Flow

1. **User Registration**: Users register with email and password
2. **Password Hashing**: Passwords are securely hashed before storage
3. **Login**: Users authenticate with credentials to receive JWT token
4. **Token Usage**: JWT token is included in API requests for authorization
5. **Token Validation**: Backend validates token for protected endpoints
6. **Password Recovery**: Email-based password reset flow

## Security Features

- **Password Hashing**: Secure password storage using bcrypt
- **JWT Authentication**: Stateless authentication with expiring tokens
- **Role-Based Access Control**: Superuser and regular user permissions
- **CORS Protection**: Configurable CORS settings
- **Rate Limiting**: Protection against brute force attacks (to be implemented)
- **Input Validation**: Request validation using Pydantic models

## Development Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker and Docker Compose (optional)

### Local Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd PROJECT/KonditionFastAPI
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
cd backend
pip install -e .
```

4. **Set up environment variables**

Create a `.env` file in the backend directory:

```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=kondition
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin
```

5. **Run database migrations**

```bash
alembic upgrade head
```

6. **Start the development server**

```bash
uvicorn app.main:app --reload
```

### Docker Setup

1. **Build and start the containers**

```bash
docker-compose up -d
```

2. **Run migrations in the container**

```bash
docker-compose exec backend alembic upgrade head
```

3. **Create initial data**

```bash
docker-compose exec backend python -m app.initial_data
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app
```

### Test Structure

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database interactions
- **Fixtures**: Reusable test components

## Database Migrations

### Creating a Migration

```bash
# Generate a migration script
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Revert migrations
alembic downgrade -1
```

## Deployment

### Production Deployment

1. **Configure environment variables for production**

2. **Build and deploy with Docker Compose**

```bash
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d
```

3. **Set up a reverse proxy (Traefik, Nginx, etc.)**

4. **Configure SSL certificates**

### Monitoring

- **Sentry Integration**: Error tracking and performance monitoring
- **Logging**: Structured logs for debugging and auditing
- **Health Checks**: Endpoint for monitoring service health

## Future Implementations

### Planned Features

1. **Workout Data Models**
   - Workout sessions
   - Exercise types
   - User progress tracking

2. **Scheduling System**
   - Workout scheduling
   - Reminder notifications

3. **Social Features**
   - Friend connections
   - Activity sharing
   - Leaderboards

4. **Analytics**
   - Progress visualization
   - Achievement tracking
   - Performance metrics

## Best Practices

### Code Style

- Follow PEP 8 guidelines
- Use type hints for better IDE support
- Document functions and classes with docstrings
- Use meaningful variable and function names

### API Design

- Follow RESTful principles
- Use appropriate HTTP methods and status codes
- Implement proper error handling
- Version the API for backward compatibility

### Security

- Keep dependencies updated
- Implement proper input validation
- Use secure password hashing
- Protect against common vulnerabilities (CSRF, XSS, etc.)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [JWT Documentation](https://jwt.io/)
