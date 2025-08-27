# AGENTS.MD - Instructions for AI Agents

This document provides guidance for AI agents working on this project. It outlines the project structure, development workflow, and other important information to help you contribute effectively.

## Project Overview

This is a full-stack web application built with the following technologies:

*   **Backend:**
    *   [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance) web framework for building APIs with Python.
    *   [SQLModel](https://sqlmodel.tiangolo.com/): A library for interacting with SQL databases from Python code, with Python objects.
    *   [PostgreSQL](https://www.postgresql.org/): A powerful, open-source object-relational database system.
    *   [Alembic](https://alembic.sqlalchemy.org/): A lightweight database migration tool for SQLAlchemy.
*   **Frontend:**
    *   [React](https://react.dev/): A JavaScript library for building user interfaces.
    *   [TypeScript](https://www.typescriptlang.org/): A typed superset of JavaScript that compiles to plain JavaScript.
    *   [Vite](https://vitejs.dev/): A fast frontend build tool.
    *   [Chakra UI](https://chakra-ui.com/): A simple, modular and accessible component library for React.
*   **DevOps & Tooling:**
    *   [Docker](https://www.docker.com/): For containerizing the application for consistent development and deployment.
    *   [Traefik](https://traefik.io/): A modern reverse proxy and load balancer.
    *   [uv](https://docs.astral.sh/uv/): For Python package and environment management.
    *   [pre-commit](https://pre-commit.com/): For running pre-commit hooks to maintain code quality.

## Getting Started

### Backend Setup

1.  Navigate to the `backend` directory: `cd backend`
2.  Install the Python dependencies using `uv`:
    ```bash
    uv sync
    ```
3.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

### Frontend Setup

1.  Navigate to the `frontend` directory: `cd frontend`
2.  Ensure you have `nvm` or `fnm` installed. Then, install and use the correct Node.js version:
    ```bash
    # Using fnm
    fnm install
    fnm use

    # Or using nvm
    nvm install
    nvm use
    ```
3.  Install the NPM dependencies:
    ```bash
    npm install
    ```

## Development Workflow

The primary way to run the application for development is using Docker Compose.

1.  From the project root, start the entire stack:
    ```bash
    docker compose watch
    ```
2.  This will make the following services available:
    *   **Frontend:** `http://localhost:5173`
    *   **Backend API:** `http://localhost:8000`
    *   **API Docs (Swagger):** `http://localhost:8000/docs`
    *   **Database Admin (Adminer):** `http://localhost:8080`
    *   **Email Catcher (MailCatcher):** `http://localhost:1080`

For a faster development loop, you can run the frontend or backend services locally outside of Docker. See `development.md` for more details.

## Testing

### Backend Tests

1.  Navigate to the `backend` directory.
2.  Run the tests using the provided script:
    ```bash
    bash ./scripts/test.sh
    ```
    This script uses `pytest` to run the test suite.

### Frontend End-to-End Tests

1.  Make sure the Docker stack is running: `docker compose up -d --wait backend`
2.  Navigate to the `frontend` directory.
3.  Run the Playwright tests:
    ```bash
    npx playwright test
    ```

## Code Generation

The frontend has a generated API client based on the backend's OpenAPI schema. If you make changes to the backend API, you must regenerate the client.

1.  Ensure the backend virtual environment is activated.
2.  From the project root, run the generation script:
    ```bash
    ./scripts/generate-client.sh
    ```
3.  Commit the updated client files in `frontend/src/client/`.

## Code Style & Linting

This project uses `pre-commit` to enforce code style and linting. The hooks are defined in `.pre-commit-config.yaml`.

*   **Installation:** Run `pre-commit install` once to set up the git hooks.
*   **Usage:** The hooks will run automatically before each commit. If a hook modifies a file, you will need to stage the changes and commit again.
*   **Manual Run:** You can run the hooks on all files at any time with `pre-commit run --all-files`.

## Deployment

The application is designed to be deployed using Docker. A CI/CD pipeline using GitHub Actions is configured for `staging` and `production` environments. For detailed deployment instructions, please refer to the `deployment.md` file.

## Key Files & Directories

*   `AGENTS.MD`: (This file) Instructions for AI agents.
*   `README.md`: General project information.
*   `development.md`: Detailed local development guide.
*   `deployment.md`: Detailed deployment guide.
*   `.env`: Configuration file for environment variables (passwords, keys, etc.).
*   `docker-compose.yml`: Main Docker Compose configuration.
*   `docker-compose.override.yml`: Docker Compose overrides for local development.
*   `backend/`: Contains the FastAPI backend application.
    *   `backend/app/main.py`: Main application entry point.
    *   `backend/app/models.py`: SQLModel data models.
    *   `backend/app/api/`: API endpoint definitions.
    *   `backend/app/crud.py`: CRUD operations.
    *   `backend/app/tests/`: Backend tests.
*   `frontend/`: Contains the React frontend application.
    *   `frontend/src/main.tsx`: Main application entry point.
    *   `frontend/src/routes/`: Application routes and pages.
    *   `frontend/src/components/`: Reusable React components.
    *   `frontend/src/client/`: Generated API client.
    *   `frontend/tests/`: Playwright E2E tests.
*   `.github/workflows/`: GitHub Actions CI/CD workflows.
