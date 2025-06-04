# Full Stack FastAPI Project

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test/badge.svg" alt="Test"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
    - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
    - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components.
    - 🤖 An automatically generated frontend client.
    - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.
    - 🦇 Dark mode support.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

### Dashboard Login

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Create User

[![API docs](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - User Settings

[![API docs](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## Getting Started / Local Development Setup

Docker Compose is the recommended way to run the project locally.
Use the command `docker compose watch` to start the services.

For more details on Docker Compose, including how to access services (frontend, backend, docs, etc.), please refer to `development.md`.

For faster development iteration, frontend and backend services can be run directly on the host machine.
Instructions for this can be found in `frontend/README.md` and `backend/README.md`.

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.

## Useful Scripts

Here's a list of scripts available in the project to help with common development tasks:

-   `scripts/build.sh`: Builds the Docker images for the project.
-   `scripts/test.sh`: Runs the complete test suite in a Dockerized environment. This typically includes backend tests and can be expanded to include frontend end-to-end tests.
-   `scripts/test-local.sh`: Runs backend tests directly on the host. It assumes the backend services (like the database) are already running (e.g., via `docker compose watch` or a similar local setup).
-   `scripts/generate-client.sh`: Generates or updates the frontend client based on the backend's OpenAPI schema. This usually involves fetching the schema and running a code generation tool.
-   `backend/scripts/format.sh`: Formats the backend Python code using Ruff to ensure consistent code style.
-   `backend/scripts/lint.sh`: Lints the backend Python code using MyPy for static type checking and Ruff for identifying potential errors and style issues.
-   `backend/scripts/test.sh`: Runs backend tests directly on the host (similar to `scripts/test-local.sh` but often focused only on backend unit/integration tests) and generates a test coverage report.

## Release Notes

Check the file [release-notes.md](./release-notes.md).
