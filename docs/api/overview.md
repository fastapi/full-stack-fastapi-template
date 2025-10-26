# API Documentation

**CurriculumExtractor REST API**

## API Overview

RESTful API built with FastAPI for K-12 worksheet extraction platform.

- **Framework**: FastAPI 0.115+
- **Database**: Supabase PostgreSQL 17 (Session Mode)
- **Auth**: JWT tokens with 8-day expiry
- **Task Queue**: Celery 5.5 with Redis
- **Documentation**: Auto-generated from OpenAPI 3.1

## Base URL

- **Development**: `http://localhost:8000`
- **API Prefix**: `/api/v1`
- **Supabase Project**: wijzypbstiigssjuiuvh (ap-south-1)

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs (Try it out!)
- **ReDoc**: http://localhost:8000/redoc (Alternative view)
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

**Quick Start**: Open http://localhost:8000/docs and use the "Authorize" button with your JWT token.

## Authentication

All protected endpoints require JWT authentication.

### Obtaining Token

```bash
POST /api/v1/login/access-token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "token_type": "bearer"
}
```

### Using Token

Include in Authorization header:
```
Authorization: Bearer eyJ0eXAiOiJKV1...
```

## Core Endpoints

### Authentication
- `POST /api/v1/login/access-token` - Login
- `POST /api/v1/login/test-token` - Verify token
- `POST /api/v1/password-recovery/{email}` - Request password reset
- `POST /api/v1/reset-password/` - Reset password with token

### Users
- `GET /api/v1/users/me` - Current user profile
- `PATCH /api/v1/users/me` - Update profile
- `PATCH /api/v1/users/me/password` - Change password
- `POST /api/v1/users/signup` - Register new user
- `GET /api/v1/users/` - List users (admin only)
- `POST /api/v1/users/` - Create user (admin only)
- `GET /api/v1/users/{user_id}` - Get user (admin only)
- `PATCH /api/v1/users/{user_id}` - Update user (admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Tasks (Celery)
- `POST /api/v1/tasks/health-check` - Trigger health check task
- `POST /api/v1/tasks/test?duration=5` - Trigger test task (with duration)
- `GET /api/v1/tasks/status/{task_id}` - Get task status and result
- `GET /api/v1/tasks/inspect/stats` - Get Celery worker statistics

### Utilities
- `GET /api/v1/utils/health-check/` - Backend health check

### Ingestions (Document Upload) ✅ Implemented
- `POST /api/v1/ingestions/` - Upload PDF worksheet (multipart/form-data)

---

## CurriculumExtractor Endpoints (To Be Implemented)

### Extractions
- `GET /api/v1/extractions/` - List user's extractions
- `GET /api/v1/extractions/{id}` - Get extraction details
- `PATCH /api/v1/extractions/{id}` - Update extraction
- `DELETE /api/v1/extractions/{id}` - Delete extraction
- `POST /api/v1/extractions/{id}/process` - Trigger OCR extraction pipeline

### Questions
- `GET /api/v1/questions/` - List questions (with filters)
- `GET /api/v1/questions/{id}` - Get question details
- `PATCH /api/v1/questions/{id}` - Update question
- `DELETE /api/v1/questions/{id}` - Delete question
- `POST /api/v1/questions/{id}/approve` - Approve for question bank
- `POST /api/v1/questions/{id}/reject` - Reject question

## Common Patterns

### Pagination

Query parameters:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 100)

Example:
```bash
GET /api/v1/items/?skip=10&limit=5
```

### Error Responses

Standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error

Error format:
```json
{
  "detail": "Error message"
}
```

## Request/Response Examples

### Trigger Celery Task

```bash
# Trigger health check
curl -X POST http://localhost:8000/api/v1/tasks/health-check

# Response
{
  "task_id": "8f3db2b2-0959-4410-9865-1632a8eed59b",
  "status": "queued",
  "message": "Health check task queued successfully"
}

# Check status
curl http://localhost:8000/api/v1/tasks/status/8f3db2b2-0959-4410-9865-1632a8eed59b

# Response
{
  "task_id": "8f3db2b2-0959-4410-9865-1632a8eed59b",
  "status": "SUCCESS",
  "ready": true,
  "result": {
    "status": "healthy",
    "message": "Celery worker is operational"
  }
}
```

### Authentication Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@curriculumextractor.com&password=your-password"

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}

# 2. Use token for authenticated requests
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Upload PDF for Extraction

```bash
# Upload PDF ✅ Implemented
curl -X POST http://localhost:8000/api/v1/ingestions/ \
  -H "Authorization: Bearer {token}" \
  -F "file=@worksheet.pdf"

# Response
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "filename": "worksheet.pdf",
  "file_size": 5242880,
  "page_count": 10,
  "mime_type": "application/pdf",
  "status": "UPLOADED",
  "presigned_url": "https://wijzypbstiigssjuiuvh.supabase.co/storage/v1/object/sign/worksheets/...",
  "uploaded_at": "2025-10-25T14:30:00Z",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## API Architecture

### Tech Stack
- **Framework**: FastAPI 0.115+ (async)
- **ORM**: SQLModel 0.0.24 (Pydantic + SQLAlchemy)
- **Database**: Supabase PostgreSQL 17
- **Task Queue**: Celery 5.5 + Redis 7
- **Auth**: JWT (pyjwt 2.8)
- **Validation**: Pydantic 2.12

### Connection Details
- **Mode**: Session Pooler (port 5432)
- **Region**: ap-south-1 (Mumbai, India)
- **Pool Size**: 10 base + 20 overflow = 30 max
- **Driver**: psycopg3 (postgresql+psycopg://)

---

## Rate Limiting

Currently no rate limiting (development phase).

**Production considerations**:
- Implement rate limiting per user/IP
- Use Redis for distributed rate limiting
- Configure via FastAPI middleware

---

## Async Task Processing

### Celery Integration

All long-running operations (OCR, PDF processing) run asynchronously via Celery:

```python
# Queue a task
POST /api/v1/extractions/{id}/process

# Returns immediately with task_id
{
  "task_id": "abc123..."
}

# Poll for status
GET /api/v1/tasks/status/{task_id}

# Get result when complete
{
  "status": "SUCCESS",
  "result": {...}
}
```

**Celery Worker**:
- 4 concurrent processes
- 10-minute max task time
- Redis message broker
- Real-time progress logging

---

For complete interactive API documentation, visit: **http://localhost:8000/docs**

For detailed endpoint documentation, see [endpoints/](./endpoints/) (to be created)
