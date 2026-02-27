---
title: "Deployment Environments"
doc-type: reference
status: published
last-updated: 2026-02-27
updated-by: "infra docs writer"
related-code:
  - backend/app/core/config.py
  - compose.yml
  - compose.override.yml
  - backend/Dockerfile
  - frontend/Dockerfile
  - .github/workflows/**
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
| `GIT_COMMIT` | GitHub Actions | SHA from commit |
| `BUILD_TIME` | GitHub Actions | Timestamp from build |
| `SENTRY_DSN` | GitHub Secret | https://xxxx@sentry.io/yyyy |
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

1. Push to `main` branch triggers GitHub Actions
2. Backend and frontend tests run in CI
3. On success, Docker images are built
4. Images pushed to registry
5. Remote runner pulls new images
6. `docker compose up -d` updates services
7. Traefik routes traffic to new containers

**How to Deploy:**

```bash
# Merge PR to main (GitHub automatically triggers deployment)
# Or push directly to main:
git push origin main
```

Monitor deployment: GitHub Actions → staging workflow

### Rollback

If staging breaks:

```bash
# On staging server (or via SSH)
cd /root/code/app/
git revert <commit-hash>
git push  # Triggers redeploy
# Or manually pull previous version and `docker compose up`
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
| `GIT_COMMIT` | GitHub Actions | SHA from release tag |
| `BUILD_TIME` | GitHub Actions | Timestamp from build |
| `SENTRY_DSN` | GitHub Secret | https://xxxx@sentry.io/yyyy |
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

1. Create Git tag: `git tag v1.2.3 && git push origin v1.2.3`
2. GitHub Actions detects tag
3. Tests run (same as staging)
4. Docker images built
5. Manual approval before prod deploy (optional in workflow)
6. Images pushed to registry
7. Remote runner pulls images
8. `docker compose up -d` updates services
9. Health checks verify deployment success

**How to Deploy:**

```bash
# Create and push a release tag
git tag v1.2.3
git push origin v1.2.3

# Or via GitHub UI: Create Release on main branch
```

Monitor deployment: GitHub Actions → production workflow

### Monitoring & Alerts

Production includes:
- **Sentry**: Error tracking and real-time alerts
- **Health checks**: Backend `/api/v1/utils/health-check/` returns 200 if healthy
- **Traefik**: Monitors container health automatically
- **Logs**: Stored on server and/or external logging service

### Security

`RequestPipelineMiddleware` automatically adds `Strict-Transport-Security: max-age=31536000; includeSubDomains` when `ENVIRONMENT=production`. Ensure DNS and subdomains are HTTPS-ready before setting this in production.

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

# 4. Redeploy application (triggers CI/CD):
git tag v1.2.4 && git push origin v1.2.4
```

**Monitoring secrets in logs:**
- Application uses `SecretStr` type for all sensitive values
- Logs will show masked secrets like `***` instead of actual values
- Check Sentry for any unmasked secrets and report immediately

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
