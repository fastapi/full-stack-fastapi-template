# Aygentic Starter Template

A production-ready full-stack microservice template: **FastAPI** backend, **React** frontend, **Supabase** database, and **Clerk** authentication — containerised with Docker and deployed via GitHub Actions to GitHub Container Registry (GHCR).

## Technology Stack

| Category | Technology |
|----------|-----------|
| Backend | Python >=3.10, FastAPI >=0.114.2 |
| ORM | SQLModel >=0.0.21 (SQLAlchemy) |
| Database | Supabase (managed PostgreSQL) |
| Frontend | TypeScript 5.9, React 19.1, Vite 7.3 (SWC) |
| Routing | TanStack Router 1.157+ (file-based) |
| Server State | TanStack Query 5.90+ |
| Styling | Tailwind CSS 4.2, shadcn/ui (new-york) |
| Auth | Clerk (managed JWT verification) |
| Logging | structlog (structured JSON) |
| Container Registry | GitHub Container Registry (GHCR) |
| CI/CD | GitHub Actions |

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/your-repo.git
cd your-repo

# 2. Copy environment template and fill in credentials
cp .env.example .env
# Edit .env: set SUPABASE_URL, SUPABASE_SERVICE_KEY, CLERK_SECRET_KEY

# 3. Start the full stack with live reload
docker compose watch
```

The stack will be available at:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Database Admin | http://localhost:8080 |

See [docs/getting-started/setup.md](docs/getting-started/setup.md) for full installation details.

## Development

```bash
# Full stack (recommended)
docker compose watch

# Backend only
cd backend && uv sync && fastapi dev app/main.py

# Frontend only
cd frontend && bun install && bun run dev

# Regenerate TypeScript API client after backend changes
bash scripts/generate-client.sh
```

See [docs/getting-started/development.md](docs/getting-started/development.md) for the complete development workflow.

## Testing

```bash
# Backend: all tests with coverage (requires >=90%)
bash ./scripts/test.sh

# Backend: specific test file
cd backend && uv run pytest tests/unit/test_entities.py -v

# Frontend: E2E tests (requires full stack running)
bunx playwright test

# Frontend: E2E with interactive UI
bunx playwright test --ui
```

See [docs/testing/strategy.md](docs/testing/strategy.md) for coverage requirements and mocking patterns.

---

## Deployment

### Environment Model

| Environment | Trigger | URL Pattern | Purpose |
|-------------|---------|-------------|---------|
| **Local** | `docker compose watch` | localhost | Development with hot-reload |
| **Staging** | Push to `main` branch | staging.example.com | Pre-production validation |
| **Production** | GitHub release published | example.com | Live traffic |

### Container Registry (GHCR)

Docker images are stored in GitHub Container Registry at:

```
ghcr.io/{github-org}/{github-repo}/backend:{tag}
```

**Tagging strategy:**

| Environment | Tags Applied |
|-------------|-------------|
| Staging | `:{git-sha}` and `:staging` |
| Production | `:{semver-version}` and `:latest` |

The SHA tag is the stable, immutable reference. The `staging` and `latest` tags are mutable pointers that always reference the most recently deployed image. Using the SHA tag for production promotion guarantees that the exact image validated on staging reaches production — with no rebuild.

**Packages are public by default** when the repository is public. For private registries, set the package visibility in your GitHub organization settings.

### Staging Deployment

Staging deploys automatically on every push to the `main` branch.

**Workflow file:** `.github/workflows/deploy-staging.yml`

```
Push to main
    │
    ├── Checkout code
    ├── Log in to GHCR (GITHUB_TOKEN)
    ├── Build Docker image (backend/Dockerfile)
    │     Build args: GIT_COMMIT={sha}, BUILD_TIME={timestamp}
    ├── Push ghcr.io/{repo}/backend:{sha}
    ├── Push ghcr.io/{repo}/backend:staging
    └── [Platform deploy step — uncomment one block]
```

The staging workflow uses `concurrency: cancel-in-progress: true`, so rapid pushes to `main` will cancel the in-flight staging deploy in favour of the newest commit.

### Production Promotion

Production deploys when a **GitHub Release is published**. It does not rebuild the image — it promotes the exact staging image by re-tagging it.

**Workflow file:** `.github/workflows/deploy-production.yml`

```
GitHub Release published (tag: v1.2.3)
    │
    ├── Checkout code
    ├── Log in to GHCR (GITHUB_TOKEN)
    ├── docker pull ghcr.io/{repo}/backend:{release-sha}
    ├── docker tag → ghcr.io/{repo}/backend:v1.2.3
    ├── docker tag → ghcr.io/{repo}/backend:latest
    ├── docker push :v1.2.3 and :latest
    └── [Platform deploy step — uncomment one block]
```

The production workflow uses `concurrency: cancel-in-progress: false`, so a production deploy is never cancelled mid-flight.

**To trigger a production deploy:**

1. Verify staging is healthy (health checks, smoke tests)
2. Run `supabase db push` against the production database (see [Supabase Migration Coordination](#supabase-migration-coordination))
3. Create a GitHub Release via the UI or CLI:

```bash
# Via GitHub CLI
gh release create v1.2.3 --title "v1.2.3" --notes "Changelog here"
```

### Platform-Specific Deployment

Both workflow files contain five pluggable deploy blocks. Uncomment exactly one block per workflow to activate deployment to your chosen platform.

#### Railway

**Secrets required:** `RAILWAY_TOKEN`, `RAILWAY_SERVICE_ID_STAGING`, `RAILWAY_SERVICE_ID_PRODUCTION`

```yaml
# Uncomment in deploy-staging.yml:
# - name: Deploy to Railway
#   run: railway up --service ${{ secrets.RAILWAY_SERVICE_ID_STAGING }}
#   env:
#     RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

Railway automatically pulls the image from GHCR and redeploys the service. Ensure your Railway service is configured to pull from `ghcr.io/{repo}/backend`.

#### Alibaba Cloud (ACR + ECS)

**Secrets required:** `ALIBABA_ACCESS_KEY`, `ALIBABA_SECRET_KEY`

The block re-tags the GHCR image to your Alibaba Cloud Container Registry namespace and pushes it, then triggers an ECS rolling update. Fill in `{region}` and `{namespace}` placeholders with your ACR details before uncommenting.

#### Google Cloud Run

**Secrets required:** `GCP_SA_KEY` (service account JSON), `GCP_SERVICE_NAME`

```yaml
# Uncomment in deploy-staging.yml:
# - name: Deploy to Cloud Run
#   uses: google-github-actions/deploy-cloudrun@v2
#   with:
#     service: ${{ secrets.GCP_SERVICE_NAME }}
#     image: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
```

Cloud Run pulls the image directly from GHCR. Grant the Cloud Run service account `roles/artifactregistry.reader` or configure GHCR package access for your service account.

#### Fly.io

**Secrets required:** `FLY_API_TOKEN`

```yaml
# Uncomment in deploy-staging.yml:
# - name: Deploy to Fly.io
#   uses: superfly/flyctl-actions/setup-flyctl@main
# - run: flyctl deploy --image ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
#   env:
#     FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Ensure your `fly.toml` references the correct app name and that the Fly app has GHCR pull access configured.

#### Self-hosted (Docker Compose via SSH)

**Secrets required:** `DEPLOY_HOST` (user@host format)

```yaml
# Uncomment in deploy-staging.yml:
# - name: Deploy via SSH
#   run: |
#     ssh ${{ secrets.DEPLOY_HOST }} \
#       "docker pull ghcr.io/${{ github.repository }}/backend:${{ github.sha }} \
#        && docker compose up -d"
```

The self-hosted runner SSH key must be pre-authorized on the target server. The server must have Docker and Docker Compose installed.

### Required GitHub Actions Secrets

Configure these in: **GitHub repository → Settings → Secrets and variables → Actions**

| Secret | Description | Required By |
|--------|-------------|-------------|
| `GITHUB_TOKEN` | Automatic — grants `write:packages` for GHCR push | Both deploy workflows |
| `RAILWAY_TOKEN` | Railway deploy token | Railway only |
| `RAILWAY_SERVICE_ID_STAGING` | Railway staging service ID | Railway staging |
| `RAILWAY_SERVICE_ID_PRODUCTION` | Railway production service ID | Railway production |
| `GCP_SA_KEY` | Google Cloud service account key (JSON) | Cloud Run only |
| `GCP_SERVICE_NAME` | Google Cloud Run service name | Cloud Run only |
| `FLY_API_TOKEN` | Fly.io API token | Fly.io only |
| `DEPLOY_HOST` | SSH target host (`user@host`) | Self-hosted only |

Application runtime secrets (passed to the container at deploy time):

| Secret | Description |
|--------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `CLERK_SECRET_KEY` | Clerk backend secret key |
| `SENTRY_DSN` | Sentry error tracking DSN (optional) |

### Rollback Procedure

To roll back to a previous release, redeploy an earlier image tag from GHCR.

**Option 1 — Redeploy a previous GitHub Release:**

Create a new release pointing at the previous tag. The production workflow will re-tag and deploy that image.

**Option 2 — Direct image rollback (emergency):**

```bash
# Identify the previous stable SHA or version tag
# Example: rolling back to v1.2.2

# Pull and retag the previous image as latest
docker pull ghcr.io/{org}/{repo}/backend:v1.2.2
docker tag ghcr.io/{org}/{repo}/backend:v1.2.2 \
  ghcr.io/{org}/{repo}/backend:latest
docker push ghcr.io/{org}/{repo}/backend:latest

# On the production host (or via your platform CLI):
docker pull ghcr.io/{org}/{repo}/backend:v1.2.2
docker compose up -d
```

**Option 3 — Platform-specific rollback:**

- **Railway:** Go to Railway dashboard → Deployments → click "Rollback" on a previous deployment
- **Cloud Run:** `gcloud run services update-traffic SERVICE_NAME --to-revisions=REVISION=100`
- **Fly.io:** `flyctl releases list` then `flyctl deploy --image ghcr.io/{repo}/backend:v1.2.2`

### Pre-Production Checklist

Before publishing a GitHub Release to trigger production deployment:

- [ ] All CI checks pass (lint, types, tests, coverage >=90%)
- [ ] Docker image built and pushed to GHCR (`:staging` tag exists)
- [ ] Image is deployed and running on staging
- [ ] Staging liveness check passes: `GET /healthz` returns 200
- [ ] Staging readiness check passes: `GET /readyz` returns 200
- [ ] Staging `GET /version` shows the expected commit SHA and build time
- [ ] Manual or automated smoke tests pass on staging
- [ ] Supabase migrations applied to production (`supabase db push` — see below)
- [ ] GitHub Release created with changelog
- [ ] Production health checks verified post-deploy

### Supabase Migration Coordination

Database migrations must be applied **before** the new container is deployed. The application will fail to start if the schema does not match expectations.

```bash
# 1. Confirm supabase/config.toml points to your production project
#    [project]
#    id = "your-production-project-ref"

# 2. Apply all pending migrations to production Supabase project
supabase db push

# 3. Verify no migration errors in Supabase dashboard
#    Dashboard → Database → Migrations

# 4. Then publish the GitHub Release to trigger production deploy
```

This project uses two migration tools:

| Tool | Files | Purpose |
|------|-------|---------|
| Supabase CLI | `supabase/migrations/` | Entity tables with row-level security |
| Alembic | `backend/alembic/versions/` | SQLModel-managed tables |

Run `alembic upgrade head` for Alembic migrations and `supabase db push` for Supabase CLI migrations. Both must be applied before releasing.

---

## Environment Variables

Configuration is loaded from `.env` (development) or passed as container environment variables (staging/production). Copy `.env.example` to `.env` to get started.

**Required — no defaults:**

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL (e.g. `https://xxx.supabase.co`) |
| `SUPABASE_SERVICE_KEY` | Service role key — bypasses row-level security |
| `CLERK_SECRET_KEY` | Clerk backend secret for JWT verification |

**Key optional variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Runtime environment: `local`, `staging`, `production` |
| `SERVICE_NAME` | `my-service` | Application identifier used in logs |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | `json` | `json` (production) or `console` (development) |
| `BACKEND_CORS_ORIGINS` | `[]` | Comma-separated allowed CORS origins |
| `SENTRY_DSN` | — | Sentry DSN for error reporting (optional) |
| `GIT_COMMIT` | `unknown` | Set automatically by CI from `github.sha` |
| `BUILD_TIME` | `unknown` | Set automatically by CI from commit timestamp |

See `.env.example` for the full variable reference including CI/CD platform secrets.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/getting-started/setup.md](docs/getting-started/setup.md) | Prerequisites, installation, local services |
| [docs/getting-started/development.md](docs/getting-started/development.md) | Daily commands, database migrations, API client |
| [docs/getting-started/contributing.md](docs/getting-started/contributing.md) | Code standards, PR process, commit format |
| [docs/architecture/overview.md](docs/architecture/overview.md) | System design, component interactions |
| [docs/api/overview.md](docs/api/overview.md) | API conventions, authentication, error handling |
| [docs/data/models.md](docs/data/models.md) | Data models and database schema |
| [docs/testing/strategy.md](docs/testing/strategy.md) | Testing approach and coverage requirements |
| [docs/deployment/environments.md](docs/deployment/environments.md) | Environment configs, variables, migration guide |
| [docs/deployment/ci-pipeline.md](docs/deployment/ci-pipeline.md) | All GitHub Actions workflows in detail |
| [docs/runbooks/incidents.md](docs/runbooks/incidents.md) | Incident response and escalation procedures |

---

## License

MIT
