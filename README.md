# Vantage

A social movie club platform with an Art Deco-inspired design. Discover movies, build watchlists, rate films, and connect with friends through shared cinema experiences.

## Overview

Vantage is a full-stack web application that enables teams and friend groups to:

- **Discover Movies** - Search and explore films via OMDB API integration with local caching
- **Personal Watchlists** - Track movies you want to watch and mark ones you've seen
- **Rate & Review** - Rate movies on a 5-star scale with your personal collection
- **Movie Clubs** (Coming Soon) - Create clubs with shared watchlists and voting
- **Watch Parties** (Coming Soon) - Schedule events and coordinate viewing sessions
- **Discussions** (Coming Soon) - Threaded forums for movie discussions

Built on the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) with modern React frontend.

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | Python web framework with async support |
| PostgreSQL | Primary database |
| SQLModel | ORM combining SQLAlchemy + Pydantic |
| Alembic | Database migrations |
| JWT | Authentication tokens |
| httpx | Async HTTP client for OMDB API |
| Sentry | Error tracking (optional) |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 19 | UI framework |
| TypeScript | Type safety |
| Vite | Build tool and dev server |
| TanStack Router | Type-safe routing |
| TanStack Query | Server state management |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Component library (Radix UI + Tailwind) |
| Playwright | End-to-end testing |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker Compose | Container orchestration |
| Traefik | Reverse proxy with automatic HTTPS |
| Adminer | Database administration UI |
| Mailcatcher | Email testing in development |

## Installation

### Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Python 3.10+** (for local backend development)
- **Bun** or **Node.js 18+** (for frontend development)
- **uv** (Python package manager)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vantage
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set required values:
   ```env
   # Generate a secure key
   SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(32))">

   # Admin account
   FIRST_SUPERUSER=admin@example.com
   FIRST_SUPERUSER_PASSWORD=<your-password>

   # Database
   POSTGRES_PASSWORD=<your-password>

   # OMDB API (get free key at http://www.omdbapi.com/apikey.aspx)
   OMDB_API_KEY=<your-api-key>
   ```

3. **Start the application**
   ```bash
   docker compose watch
   ```

4. **Access the services**
   | Service | URL |
   |---------|-----|
   | Frontend | http://localhost:5173 |
   | Backend API | http://localhost:8000 |
   | API Documentation | http://localhost:8000/docs |
   | Database Admin | http://localhost:8080 |
   | Email Inbox | http://localhost:1080 |
   | Traefik Dashboard | http://localhost:8090 |

### Local Development Setup

#### Backend
```bash
cd backend
uv sync                          # Install dependencies
source .venv/bin/activate        # Activate virtual environment
fastapi dev app/main.py          # Start dev server (port 8000)
```

#### Frontend
```bash
cd frontend
bun install                      # Install dependencies
bun run dev                      # Start dev server (port 5173)
```

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | Application name | Vantage |
| `ENVIRONMENT` | Environment mode | local |
| `DOMAIN` | Primary domain | localhost |
| `SECRET_KEY` | JWT signing key | (required) |
| `POSTGRES_SERVER` | Database host | db |
| `POSTGRES_PORT` | Database port | 5432 |
| `POSTGRES_DB` | Database name | app |
| `POSTGRES_USER` | Database user | postgres |
| `POSTGRES_PASSWORD` | Database password | (required) |
| `OMDB_API_KEY` | OMDB API key | (required) |
| `OMDB_CACHE_TTL_DAYS` | Movie cache duration | 30 |
| `SMTP_HOST` | Mail server host | mailcatcher |
| `SMTP_PORT` | Mail server port | 1025 |
| `BACKEND_CORS_ORIGINS` | Allowed origins (JSON array) | ["http://localhost:5173"] |

## Project Structure

```
vantage/
├── backend/                      # FastAPI backend application
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── models.py            # SQLModel database models
│   │   ├── crud.py              # Database operations
│   │   ├── api/
│   │   │   ├── main.py          # API router configuration
│   │   │   ├── deps.py          # Dependency injection
│   │   │   └── routes/          # API endpoint handlers
│   │   │       ├── login.py     # Authentication
│   │   │       ├── users.py     # User management
│   │   │       ├── movies.py    # Movie search & details
│   │   │       ├── ratings.py   # Movie ratings
│   │   │       └── watchlist.py # Personal watchlist
│   │   ├── core/
│   │   │   ├── config.py        # Settings with Pydantic
│   │   │   ├── security.py      # Password hashing & JWT
│   │   │   └── db.py            # Database connection
│   │   ├── services/
│   │   │   └── omdb.py          # OMDB API client
│   │   └── alembic/             # Database migrations
│   ├── tests/                    # Backend test suite
│   └── pyproject.toml           # Python dependencies
│
├── frontend/                     # React frontend application
│   ├── src/
│   │   ├── main.tsx             # Application entry point
│   │   ├── routes/              # TanStack Router pages
│   │   │   ├── __root.tsx       # Root layout
│   │   │   ├── _layout.tsx      # Authenticated layout
│   │   │   └── _layout/
│   │   │       ├── index.tsx    # Dashboard
│   │   │       ├── movies.tsx   # Movie search
│   │   │       ├── movies.$imdbId.tsx  # Movie details
│   │   │       ├── watchlist.tsx       # Personal watchlist
│   │   │       ├── ratings.tsx  # Rating history
│   │   │       └── settings.tsx # User settings
│   │   ├── components/
│   │   │   ├── Movies/          # Movie components
│   │   │   ├── Ratings/         # Rating components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   └── Sidebar/         # Navigation
│   │   ├── client/              # Auto-generated API client
│   │   └── hooks/               # Custom React hooks
│   ├── package.json             # Node dependencies
│   └── playwright.config.ts     # E2E test configuration
│
├── scripts/                      # Utility scripts
│   └── generate-client.sh       # Generate TypeScript API client
│
├── compose.yml                   # Docker Compose configuration
├── compose.override.yml          # Development overrides
├── .env.example                  # Environment template
├── development.md                # Development guide
├── deployment.md                 # Deployment guide
└── SPEC.md                       # Product specification
```

## System Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      Traefik Proxy                              │
│                   (Routing & HTTPS)                             │
└──────────┬─────────────────────────────────────┬────────────────┘
           │                                     │
┌──────────▼──────────┐              ┌───────────▼───────────────┐
│   Frontend (Vite)   │              │   Backend (FastAPI)       │
│   React + TS        │◄────────────►│   Python 3.10+            │
│   Port 5173         │   REST API   │   Port 8000               │
└─────────────────────┘              └───────────┬───────────────┘
                                                 │
                         ┌───────────────────────┼───────────────┐
                         │                       │               │
              ┌──────────▼──────────┐ ┌─────────▼─────────┐     │
              │   PostgreSQL        │ │   OMDB API        │     │
              │   Database          │ │   (External)      │     │
              │   Port 5432         │ └───────────────────┘     │
              └─────────────────────┘                           │
                                      ┌─────────────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │   Mailcatcher       │
                           │   (Dev SMTP)        │
                           │   Port 1025/1080    │
                           └─────────────────────┘
```

### Data Flow

1. **Authentication**: JWT-based with access tokens stored client-side
2. **API Communication**: RESTful endpoints with auto-generated TypeScript client from OpenAPI schema
3. **Movie Data**: OMDB API integration with 30-day local cache in PostgreSQL
4. **State Management**: TanStack Query for server state with automatic caching and revalidation

### Database Schema

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    User      │       │  UserWatchlist   │       │    Movie     │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id           │──┐    │ id               │    ┌──│ id           │
│ email        │  │    │ user_id       ───┼────┤  │ imdb_id      │
│ hashed_pass  │  └────┼─ user_id         │    │  │ title        │
│ full_name    │       │ movie_id      ───┼────┘  │ year         │
│ is_active    │       │ status           │       │ poster       │
│ is_superuser │       │ added_at         │       │ plot         │
│ created_at   │       └──────────────────┘       │ actors       │
└──────────────┘                                  │ director     │
       │           ┌──────────────────┐           │ imdb_rating  │
       │           │     Rating       │           │ cached_at    │
       │           ├──────────────────┤           └──────────────┘
       │           │ id               │                  │
       └───────────┼─ user_id         │                  │
                   │ movie_id      ───┼──────────────────┘
                   │ score (1-5)      │
                   │ created_at       │
                   └──────────────────┘
```

### API Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/login/access-token` | Login and get JWT token |
| POST | `/api/v1/signup` | Register new user |
| POST | `/api/v1/password-recovery/{email}` | Request password reset |
| POST | `/api/v1/reset-password/` | Reset password with token |

#### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PATCH | `/api/v1/users/me` | Update current user |
| GET | `/api/v1/users/` | List users (admin) |
| DELETE | `/api/v1/users/{id}` | Delete user (admin) |

#### Movies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/movies/search` | Search movies (query, year, type) |
| GET | `/api/v1/movies/{imdb_id}` | Get movie details |

#### Watchlist
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me/watchlist` | Get personal watchlist |
| POST | `/api/v1/users/me/watchlist` | Add movie to watchlist |
| PATCH | `/api/v1/users/me/watchlist/{id}` | Update watchlist item |
| DELETE | `/api/v1/users/me/watchlist/{id}` | Remove from watchlist |

#### Ratings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ratings/me` | Get user's ratings |
| POST | `/api/v1/ratings/` | Create/update rating |
| DELETE | `/api/v1/ratings/{id}` | Delete rating |

## Development

### Database Migrations

```bash
# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### Regenerate API Client

After modifying backend endpoints, regenerate the TypeScript client:

```bash
./scripts/generate-client.sh
# Or from frontend directory:
bun run generate-client
```

### Running Tests

**Backend (pytest)**
```bash
docker compose exec backend pytest
# With coverage
docker compose exec backend pytest --cov=app
```

**Frontend (Playwright E2E)**
```bash
cd frontend
bun run test        # Headless mode
bun run test:ui     # Interactive mode
```

### Code Quality

Pre-commit hooks are configured for:
- **Backend**: Ruff (linting/formatting), mypy (type checking)
- **Frontend**: Biome (linting/formatting)

```bash
# Run all hooks manually
uv run prek run --all-files

# Install hooks
uv run prek install -f
```

## Deployment

See [deployment.md](deployment.md) for production deployment instructions covering:

- Docker Compose production configuration
- Traefik setup with automatic HTTPS
- Environment variables for production
- GitHub Actions CI/CD

### Quick Production Setup

1. Configure production `.env` with secure secrets
2. Set up DNS records for your domain
3. Create Traefik proxy network:
   ```bash
   docker network create traefik-public
   ```
4. Deploy:
   ```bash
   docker compose -f compose.yml up -d
   ```

## Roadmap

- [x] **Phase 1**: OMDB integration, movie search, personal watchlist
- [x] **Phase 2**: Movie ratings, user profiles
- [ ] **Phase 3**: Movie clubs with shared watchlists and voting
- [ ] **Phase 4**: Written reviews and discussion forums
- [ ] **Phase 5**: Watch party scheduling and events
- [ ] **Phase 6**: Notifications, activity feeds, achievements

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Opening issues and discussions
- Submitting pull requests
- Code style and testing requirements

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Vantage** - Bringing friends together through cinema.
