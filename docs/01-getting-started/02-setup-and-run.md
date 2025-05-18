# Setup and Run

This guide covers the initial setup and running of the Full Stack FastAPI Template.

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/full-stack-fastapi-template.git
cd full-stack-fastapi-template
```

### 2. Environment Configuration

Create a `.env` file in the project root based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file to set up the following important variables:

```
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis  # Choose a secure password
POSTGRES_DB=app

# Backend
SECRET_KEY=changethis  # Generate a secure key for JWT
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis  # Choose a secure password
SMTP_HOST=localhost
SMTP_PORT=1025
```

To generate a secure random key for `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Running with Docker Compose

For a complete development environment with hot-reload capability:

```bash
# Start all services
docker compose watch
```

This will start:
- PostgreSQL database
- FastAPI backend
- React frontend
- Adminer (database management tool)

If you prefer to run services individually:

```bash
# Start only the database
docker compose up -d db

# Start backend with development server
cd backend
uv sync
source .venv/bin/activate
fastapi dev app/main.py

# Start frontend with development server
cd frontend
fnm use  # or nvm use
npm install
npm run dev
```

## First-Time Setup

After starting the services, run the initial setup scripts:

```bash
# Run database migrations
docker compose exec backend bash -c "alembic upgrade head"

# Initialize first user and sample data (if needed)
docker compose exec backend python app/initial_data.py
```

## Accessing the Services

Once everything is running, you can access:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Adminer** (Database UI): http://localhost:8080
  - System: PostgreSQL
  - Server: db
  - Username: postgres
  - Password: (as set in `.env`)
  - Database: app

## Development Mode

For the best development experience:

1. The Docker Compose configuration includes `watch` mode, which will automatically reload both the backend and frontend when files change.

2. For backend-only development:
   ```bash
   cd backend
   uv sync
   source .venv/bin/activate
   fastapi dev app/main.py
   ```

3. For frontend-only development:
   ```bash
   cd frontend
   npm run dev
   ```

## Troubleshooting

- If containers fail to start, check Docker logs:
  ```bash
  docker compose logs
  ```

- If the backend fails to connect to the database, ensure PostgreSQL is running:
  ```bash
  docker compose ps db
  ```

- For permission issues with volume mounts, check file ownership in the `./data` directory.

Next steps: Learn about the [Architecture Overview](../02-architecture/01-overview.md).