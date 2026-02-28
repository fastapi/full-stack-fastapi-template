---
title: "Deployment Environments"
doc-type: reference
status: published
last-updated: 2026-03-01
updated-by: "infra docs writer (AYG-73)"
related-code:
  - backend/app/core/config.py
  - compose.yml
  - compose.override.yml
  - backend/Dockerfile
  - frontend/Dockerfile
  - .github/workflows/deploy-staging.yml
  - .github/workflows/deploy-production.yml
  - supabase/config.toml
  - supabase/migrations/**
related-docs:
  - docs/getting-started/setup.md
  - docs/runbooks/incidents.md
  - docs/deployment/ci-pipeline.md
tags: [deployment, infrastructure, environments]
---

# Deployment Environments

## Environment Overview

This project uses three deployment environments with progressively stricter configurations:

| Environment | Branch | Auto-Deploy | URL Pattern | Purpose |
|-------------|--------|-------------|-------------|---------|
| **Local** | N/A | N/A | localhost | Active development on your machine |
| **Staging** | main | Yes (push) | staging.example.com | Pre-production validation |
| **Production** | main (tagged) | No (manual) | example.com | Live customer-facing |

## Architecture

All environments use:
- **Frontend**: React 19 + TypeScript, served by Nginx, managed by Traefik
- **Backend**: FastAPI + Python 3.10, run by uvicorn, managed by Traefik
- **Database**: PostgreSQL 18 (local) or Supabase managed service (staging/production)
- **Authentication**: Clerk for user authentication and JWT verification
- **Proxy**: Traefik 3.6 for routing and HTTPS/TLS certificates via Let's Encrypt

Configuration is managed via environment variables with the following characteristics:
- **Settings are frozen**: All configuration is immutable after application initialization
- **Secrets are protected**: Uses Pydantic `SecretStr` type to prevent accidental logging
- **Production validation**: Enforces security rules (no default secrets, no wildcard CORS)
- **Local development**: Same validation with relaxed error handling for convenience

Domains are managed by:
- **Local**: localhost with optional localhost.tiangolo.com
- **Staging/Production**: Traefik with subdomains (api.*, dashboard.*, etc.)

---

## Local Development

**Access:**
- Runs on your machine via `docker compose watch`
- Services available on localhost with different ports

### URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Database Admin (Adminer) | http://localhost:8080 |
| Email Testing (Mailcatcher) | http://localhost:1080 |
| Proxy Dashboard (Traefik) | http://localhost:8090 |

### Environment Variables (Local)

| Variable | Value | Notes |
|----------|-------|-------|
| `ENVIRONMENT` | local | Development mode (relaxed validation) |
| `SUPABASE_URL` | [Vault/Config/Secret manager] | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | [Vault/Config/Secret manager] | Service role key (secret value) |
| `CLERK_SECRET_KEY` | [Vault/Config/Secret manager] | Clerk authentication secret |
| `LOG_LEVEL` | INFO | Standard information logging |
| `LOG_FORMAT` | json | Structured JSON logging |
| `BACKEND_CORS_ORIGINS` | http://localhost,http://localhost:5173 | Allow frontend origin |
| `WITH_UI` | false | UI endpoints disabled |
| `HTTP_CLIENT_TIMEOUT` | 30 | Request timeout in seconds |
| `SENTRY_DSN` | (empty) | No error tracking locally |

### Services

| Service | Type | Notes |
|---------|------|-------|
| PostgreSQL 18 | Database | Local postgres:18 container |
| FastAPI | Backend | Python 3.10 with uvicorn |
| React | Frontend | Node 18 with Vite dev server |
| Traefik | Reverse Proxy | Routes traffic by domain |
| Mailcatcher | Email | Captures emails, UI at :1080 |
| Adminer | Database | Web UI for database management |
| Clerk | Authentication | External managed service |
| Supabase | Storage | External managed service |

### Running Locally

```bash
docker compose watch
```

### Accessing Components

```bash
# View logs
docker compose logs -f backend

# Stop a service
docker compose stop frontend

# Restart everything
docker compose down && docker compose watch
```

See [Setup Guide](../getting-started/setup.md) for detailed instructions.

---

## Staging

**Purpose:** Validate release candidates before production
**Deployment:** Automatic on push to `main` branch via GitHub Actions
**Infrastructure:** Remote server with Docker, Traefik proxy

### Access

| Resource | Method |
|----------|--------|
| Application | https://dashboard.staging.example.com |
| API | https://api.staging.example.com |
| API Docs | https://api.staging.example.com/docs |
| Database | SSH tunnel + psql (contact DevOps) |
| Logs | GitHub Actions or server logs |
| Monitoring | [Sentry project](https://sentry.io) (if configured) |

### Environment Variables

| Variable | Source | Example |
|----------|--------|---------|
| `ENVIRONMENT` | Hardcoded | staging |
| `SERVICE_NAME` | GitHub Secret | my-service |
| `SUPABASE_URL` | GitHub Secret | https://your-project.supabase.co |
| `SUPABASE_SERVICE_KEY` | GitHub Secret | [Secret manager] |
| `CLERK_SECRET_KEY` | GitHub Secret | [Secret manager] |
| `LOG_LEVEL` | GitHub Secret | INFO |
| `LOG_FORMAT` | GitHub Secret | json |
| `BACKEND_CORS_ORIGINS` | GitHub Secret | https://dashboard.staging.example.com |
| `CLERK_AUTHORIZED_PARTIES` | Default | [] |
| `GIT_COMMIT` | GitHub Actions | SHA from commit |
| `BUILD_TIME` | GitHub Actions | Timestamp from build |
| `SENTRY_DSN` | GitHub Secret | https://xxxx@sentry.io/yyyy (optional) |
| `HTTP_CLIENT_TIMEOUT` | Default | 30 |
| `HTTP_CLIENT_MAX_RETRIES` | Default | 3 |

### Services

| Service | Type | Config | Notes |
|---------|------|--------|-------|
| Supabase PostgreSQL | Database | Managed service | Daily backups, auto-scaling |
| FastAPI | Backend | 2-4 workers | Auto-restarts on failure |
| React | Frontend | Production build | Served by Nginx, cached |
| Traefik | Reverse Proxy | Let's Encrypt SSL | Auto-renews certs, rate limiting |
| Clerk | Authentication | Managed service | JWT verification, user management |
| Sentry | Error Tracking | Enabled | Real-time alerts |

### Deployment Process

1. Push to `main` branch triggers `deploy-staging.yml` in GitHub Actions
2. CI workflows (Test Backend, Playwright, pre-commit) run in parallel
3. Backend Docker image is built with build args: `GIT_COMMIT={sha}` and `BUILD_TIME={timestamp}`
4. Image pushed to GHCR with two tags: `ghcr.io/{repo}/backend:{sha}` and `ghcr.io/{repo}/backend:staging`
5. Pluggable deploy step (configured in workflow) deploys the new image to the staging environment
6. Health checks verify deployment: `/healthz`, `/readyz`, `/version`

**How to Deploy:**

```bash
# Merge PR to main (GitHub automatically triggers deployment)
# Or push directly to main:
git push origin main
```

Monitor deployment: GitHub Actions → Deploy to Staging workflow

### Rollback

If staging breaks, re-deploy a previous GHCR image by SHA:

```bash
# Find the last known-good commit SHA from GitHub Actions run history
# Then re-tag that image as staging and redeploy via your chosen platform

# Example: re-tag a previous SHA as staging
docker pull ghcr.io/{repo}/backend:{previous-sha}
docker tag ghcr.io/{repo}/backend:{previous-sha} ghcr.io/{repo}/backend:staging
docker push ghcr.io/{repo}/backend:staging
# Then trigger your platform's deploy for the staging tag
```

Alternatively, revert the commit on `main` to trigger a fresh build:

```bash
git revert <commit-hash>
git push origin main  # Triggers a new staging deploy
```

---

## Production

**Purpose:** Live customer-facing application
**Deployment:** Manual on release tag, via GitHub Actions
**Infrastructure:** Remote server with Docker, Traefik proxy, monitoring

### Access

| Resource | Method |
|----------|--------|
| Application | https://dashboard.example.com |
| API | https://api.example.com |
| API Docs | https://api.example.com/docs |
| Database | SSH tunnel + psql (contact DevOps) |
| Logs | Sentry or server logs |
| Monitoring | Sentry dashboard + uptime monitoring |

### Environment Variables

| Variable | Source | Example |
|----------|--------|---------|
| `ENVIRONMENT` | Hardcoded | production |
| `SERVICE_NAME` | GitHub Secret | my-service |
| `SUPABASE_URL` | GitHub Secret | https://your-project.supabase.co |
| `SUPABASE_SERVICE_KEY` | GitHub Secret | [Secret manager] |
| `CLERK_SECRET_KEY` | GitHub Secret | [Secret manager] |
| `LOG_LEVEL` | GitHub Secret | WARNING |
| `LOG_FORMAT` | GitHub Secret | json |
| `BACKEND_CORS_ORIGINS` | GitHub Secret | https://dashboard.example.com |
| `CLERK_AUTHORIZED_PARTIES` | Default | [] |
| `GIT_COMMIT` | GitHub Actions | SHA from release tag |
| `BUILD_TIME` | GitHub Actions | Timestamp from build |
| `SENTRY_DSN` | GitHub Secret | https://xxxx@sentry.io/yyyy (optional) |
| `HTTP_CLIENT_TIMEOUT` | Default | 30 |
| `HTTP_CLIENT_MAX_RETRIES` | Default | 3 |

### Services

| Service | Type | Config | Notes |
|---------|------|--------|-------|
| Supabase PostgreSQL | Database | Managed service | Daily backups, point-in-time recovery, replication |
| FastAPI | Backend | 4+ workers | Auto-restart, health checks |
| React | Frontend | Production build | Cached, minified, CDN-ready |
| Traefik | Reverse Proxy | Let's Encrypt SSL | Auto-renew, rate limiting, health checks |
| Clerk | Authentication | Managed service | JWT verification, OAuth providers |
| Sentry | Error Tracking | Enabled | Real-time alerts, performance monitoring |

### Logging & Monitoring

Structured JSON log output from structlog (fields: `timestamp`, `level`, `event`, `service`, `version`, `environment`, `request_id`, `correlation_id`, `method`, `path`, `status_code`, `duration_ms`). Recommended: `LOG_FORMAT=json`, `LOG_LEVEL=WARNING` for production.

### Deployment Process

1. Create a GitHub Release (UI or CLI) with a semver tag (e.g. `v1.2.3`)
2. Publishing the release triggers `deploy-production.yml` in GitHub Actions
3. The staging image tagged with the release commit SHA is pulled from GHCR — no new build occurs
4. Image is re-tagged as `ghcr.io/{repo}/backend:v1.2.3` and `ghcr.io/{repo}/backend:latest`
5. Both new tags are pushed to GHCR
6. Pluggable deploy step (configured in workflow) deploys the promoted image to production
7. Health checks verify post-deploy: `/healthz`, `/readyz`, `/version`

**The production image is the same binary validated on staging.** No code is recompiled at release time.

**How to Deploy:**

```bash
# Via GitHub CLI
gh release create v1.2.3 --title "v1.2.3" --notes "Release notes here"

# Or via GitHub UI:
# Repository → Releases → Draft a new release → Publish release
```

Monitor deployment: GitHub Actions → Deploy to Production workflow

### Monitoring & Alerts

Production includes:
- **Sentry**: Error tracking and real-time alerts
- **Health checks**: Backend `/healthz` (liveness) and `/readyz` (readiness) return 200 if healthy
- **Traefik**: Monitors container health automatically
- **Logs**: Stored on server and/or external logging service

### Security

`RequestPipelineMiddleware` automatically adds `Strict-Transport-Security: max-age=31536000; includeSubDomains` header when `ENVIRONMENT=production`. Ensure DNS and subdomains are HTTPS-ready before setting this in production.

**Production-specific validations:**
- Wildcard CORS (`*`) is rejected — must specify exact origins
- Secret values cannot be `"changethis"` — must be valid credentials
- Settings are frozen and immutable after initialization

### Disaster Recovery

See [Incidents Runbook](../runbooks/incidents.md) for:
- P1 incident response
- Rollback procedures
- Data recovery steps
- Communication protocols

---

## Environment Variable Management

### Local Development

Set in `.env` file (git-ignored, never commit secrets):

```bash
# Create .env file with required secrets
cat > .env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
CLERK_SECRET_KEY=sk_test_...
EOF
```

The `.env` file is listed in `.gitignore` and will never be committed. All other optional variables use defaults defined in `backend/app/core/config.py`.

### Staging & Production

Set via GitHub Secrets (encrypted, never logged):

**Required GitHub Secrets:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key
- `CLERK_SECRET_KEY` - Clerk backend secret

**GHCR authentication:** `GITHUB_TOKEN` is provided automatically — no configuration required.

**Platform-specific deploy secrets (configure one set matching your chosen deploy target):**

| Secret | Platform |
|--------|----------|
| `RAILWAY_TOKEN` + `RAILWAY_SERVICE_ID_STAGING` / `RAILWAY_SERVICE_ID_PRODUCTION` | Railway |
| `ALIBABA_ACCESS_KEY` + `ALIBABA_SECRET_KEY` | Alibaba Cloud (ACR + ECS) |
| `GCP_SA_KEY` + `GCP_SERVICE_NAME` | Google Cloud Run |
| `FLY_API_TOKEN` | Fly.io |
| `DEPLOY_HOST` | Self-hosted via SSH |

**Optional GitHub Secrets:**
- `SENTRY_DSN` - Sentry error tracking (optional)
- `LOG_LEVEL` - Override default INFO level
- `HTTP_CLIENT_TIMEOUT` - Override default 30 seconds
- Other variables as needed for your deployment

**How to set:**

1. Go to GitHub: Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter secret name and value

**How to reference in workflow:**

```yaml
- name: Deploy
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
    CLERK_SECRET_KEY: ${{ secrets.CLERK_SECRET_KEY }}
```

### Security & Secret Management

**Secret types used:**
- `SUPABASE_SERVICE_KEY`: Supabase service role key (never shared with frontend)
- `CLERK_SECRET_KEY`: Clerk backend secret for token verification
- All secrets use Pydantic `SecretStr` type to prevent accidental logging

**Security behavior:**
- Settings are frozen after initialization (immutable configuration)
- Secret values never appear in logs or error messages
- In production, startup fails if secrets contain `"changethis"`
- In production, wildcard CORS (`*`) is rejected for security

**Secret Rotation for Production:**

When rotating secrets:

```bash
# 1. Generate new Clerk Secret Key from Clerk dashboard
# 2. Generate new Supabase Service Key from Supabase dashboard

# 3. Update GitHub Secrets:
#    - Go to Settings → Secrets and variables → Actions
#    - Update CLERK_SECRET_KEY and SUPABASE_SERVICE_KEY

# 4. Redeploy to pick up the new secrets by publishing a new GitHub Release:
#    - Repository → Releases → Draft a new release → Publish release
#    - Or via CLI: gh release create v1.2.4 --title "v1.2.4 (secret rotation)"
#
#    Note: The deploy workflow pulls the existing GHCR image (no rebuild needed).
#    The new secrets are injected at deploy time by the pluggable deploy step.
```

**Monitoring secrets in logs:**
- Application uses `SecretStr` type for all sensitive values
- Logs will show masked secrets like `***` instead of actual values
- Check Sentry for any unmasked secrets and report immediately

---

## Supabase Migrations

This project uses two complementary migration systems:

### Migration Systems

| System | Tool | Location | Use Case | When to Run |
|--------|------|----------|----------|------------|
| **Alembic** | SQLAlchemy | `backend/alembic/versions/` | Legacy SQLModel tables | On backend model changes |
| **Supabase CLI** | Supabase | `supabase/migrations/` | Entity tables with RLS | On entity model changes |

**Why both?** During the transition to Supabase, Alembic manages existing SQLModel-based tables while Supabase CLI manages new entity tables with row-level security policies.

### Supabase CLI Migrations

Entity migrations are stored in `supabase/migrations/` and applied via the Supabase CLI.

#### Configuration

Before running CLI commands, configure your Supabase project:

```bash
# Edit supabase/config.toml
[project]
id = "your-supabase-project-ref"  # e.g., "abcdefghijklmnop"
```

Get your project ref from Supabase dashboard → Settings → General → Project Ref.

#### Applying Migrations

Run migrations on initial setup and after pulling new migration files:

```bash
# From repository root
supabase db push

# This applies all pending migrations from supabase/migrations/ to your Supabase project
```

Migrations run in timestamp order. Each migration file is idempotent — running them multiple times is safe.

#### Example Migration

`supabase/migrations/20260227000000_create_entities.sql`:
- Creates `entities` table with UUID primary key
- Adds owner-scoped index for performance
- Configures Row-Level Security (RLS) policies
- Users can only access their own entities via `owner_id = current_user_id`
- Service role key (backend only) bypasses RLS for admin operations

#### Required Environment Variables

For local development and CI/CD pipelines:

| Variable | Source | Purpose |
|----------|--------|---------|
| `SUPABASE_URL` | Supabase Settings | Project URL for database connection |
| `SUPABASE_SERVICE_KEY` | Supabase Settings → API | Service role key for backend (bypasses RLS) |
| `SUPABASE_DB_PASSWORD` | Supabase Settings | Database password (if using psql directly) |

All Supabase secrets are managed via:
- **Local**: `.env` file (git-ignored)
- **Staging/Production**: GitHub Secrets

#### When to Use Supabase CLI

Use Supabase CLI for:
- New entity tables requiring row-level security
- Migrations with PostgreSQL-specific features (triggers, functions, extensions)
- Data that requires user isolation

Use Alembic for:
- Changes to existing FastAPI/SQLModel tables
- Python ORM-based schema management
- Tables without RLS requirements

---

## Troubleshooting

### Local Not Starting

```bash
# Clear everything and start fresh
docker compose down -v --remove-orphans
docker compose watch

# Check logs
docker compose logs -f
```

### Staging/Production Deployment Fails

See [Incidents Runbook](../runbooks/incidents.md) → Investigation steps

### Supabase Connection Issues

- Verify `SUPABASE_URL` is correct (check Supabase dashboard → Settings)
- Verify `SUPABASE_SERVICE_KEY` matches the service role key (not anon key)
- Check application startup logs for authentication errors
- Verify network connectivity to Supabase endpoint

### Clerk Authentication Issues

- Verify `CLERK_SECRET_KEY` is correct (check Clerk dashboard → API Keys)
- Verify `CLERK_JWKS_URL` matches your Clerk instance (auto-detected if not set)
- Check application logs for JWT verification errors
- Verify user exists in Clerk dashboard

### Application Startup Failures

- **Secret validation error**: Verify secrets are not `"changethis"` in non-local environments
- **CORS validation error**: Verify `BACKEND_CORS_ORIGINS` doesn't contain wildcard `*` in production
- **Settings frozen error**: Configuration cannot change after startup; restart application to reload env vars

### Traefik/HTTPS Issues

- Check Traefik logs: `docker compose logs proxy` (local) or `docker logs traefik` (prod)
- Verify domain DNS points to server IP
- Let's Encrypt rate limits (production only)

## Related

- [Setup Guide](../getting-started/setup.md)
- [Development Workflow](../getting-started/development.md)
- [Incidents Runbook](../runbooks/incidents.md)
- [CI/CD Pipeline](./ci-pipeline.md)
