# Prerequisites

Before setting up the Full Stack FastAPI Template, ensure you have the following software installed on your development machine:

## Required Software

- **Docker and Docker Compose**: For containerized development and deployment
  - [Docker Installation Guide](https://docs.docker.com/get-docker/)
  - [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

- **Python 3.10+**: For local backend development
  - [Python Installation Guide](https://www.python.org/downloads/)
  
- **uv**: Modern Python package installer and environment manager (recommended over pip/venv)
  - Install with: `pip install uv`
  - [uv Documentation](https://github.com/astral-sh/uv)

- **Node.js 18+**: For local frontend development
  - [Node.js Installation Guide](https://nodejs.org/)
  - We recommend using a version manager like [fnm](https://github.com/Schniz/fnm) or [nvm](https://github.com/nvm-sh/nvm)

## Recommended Tools

- **VS Code**: With the following extensions for an optimal development experience:
  - Python extension (Microsoft)
  - ESLint
  - Prettier
  - Docker
  - REST Client

- **Git**: For version control
  - [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## System Requirements

- **Memory**: At least 4GB RAM for running the full stack (Docker containers)
- **Disk Space**: At least 2GB free space for the project and dependencies
- **Ports**: Ensure the following ports are available on your machine:
  - 5173: Frontend development server
  - 8000: Backend API
  - 5432: PostgreSQL
  - 8080: Adminer (database management)
  - 1025 & 8025: MailHog (email testing, if used)

Once you have all prerequisites installed, proceed to the [Setup and Run](02-setup-and-run.md) guide.