---
title: "Deployment Environments"
doc-type: reference
status: published
last-updated: 2026-02-26
updated-by: "initialise skill"
related-code:
  - compose.yml
  - compose.override.yml
  - backend/Dockerfile
  - frontend/Dockerfile
  - .env
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
- **Database**: PostgreSQL 18 (local) or managed service (staging/production)
- **Proxy**: Traefik 3.6 for routing and HTTPS/TLS certificates via Let's Encrypt

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
| `ENVIRONMENT` | local | Development mode |
| `DOMAIN` | localhost | Base domain for Traefik |
| `FRONTEND_HOST` | http://localhost:5173 | Frontend URL for email links |
| `BACKEND_CORS_ORIGINS` | http://localhost,http://localhost:5173 | Allow frontend origin |
| `SECRET_KEY` | changethis | **Change for security** |
| `POSTGRES_SERVER` | db | Docker service name |
| `POSTGRES_PASSWORD` | changethis | **Change for security** |
| `FIRST_SUPERUSER` | admin@example.com | Admin email |
| `FIRST_SUPERUSER_PASSWORD` | changethis | **Change for security** |
| `SMTP_HOST` | mailcatcher | Automatic email testing |
| `SENTRY_DSN` | (empty) | No error tracking locally |

### Services

| Service | Type | Notes |
|---------|------|-------|
| PostgreSQL | Database | postgres:18 container |
| FastAPI | Backend | Python 3.10 with uvicorn |
| React | Frontend | Node 18 with Vite dev server |
| Traefik | Reverse Proxy | Routes traffic by domain |
| Mailcatcher | Email | Captures emails, UI at :1080 |
| Adminer | Database | Web UI for database management |

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
| `DOMAIN` | GitHub Secret | staging.example.com |
| `STACK_NAME` | GitHub Secret | staging-example-com |
| `FRONTEND_HOST` | GitHub Secret | https://dashboard.staging.example.com |
| `BACKEND_CORS_ORIGINS` | GitHub Secret | https://dashboard.staging.example.com |
| `SECRET_KEY` | GitHub Secret | [Secret manager] |
| `POSTGRES_SERVER` | GitHub Secret | db (internal) or managed-db.example.com |
| `POSTGRES_PASSWORD` | GitHub Secret | [Secret manager] |
| `FIRST_SUPERUSER` | GitHub Secret | admin@staging.example.com |
| `FIRST_SUPERUSER_PASSWORD` | GitHub Secret | [Secret manager] |
| `SMTP_HOST` | GitHub Secret | [Email service] |
| `SENTRY_DSN` | GitHub Secret | https://xxxx@sentry.io/yyyy |

### Services

| Service | Type | Config | Notes |
|---------|------|--------|-------|
| PostgreSQL 18 | Database | Managed or self-hosted | Backed up daily |
| FastAPI | Backend | 2-4 workers | Auto-restarts on failure |
| React | Frontend | Production build | Served by Nginx |
| Traefik | Reverse Proxy | Let's Encrypt SSL | Auto-renews certs |

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
| `DOMAIN` | GitHub Secret | example.com |
| `STACK_NAME` | GitHub Secret | example-com |
| `FRONTEND_HOST` | GitHub Secret | https://dashboard.example.com |
| `BACKEND_CORS_ORIGINS` | GitHub Secret | https://dashboard.example.com |
| `SECRET_KEY` | GitHub Secret | [Secret manager] |
| `POSTGRES_SERVER` | GitHub Secret | db (internal) or managed-db.example.com |
| `POSTGRES_PASSWORD` | GitHub Secret | [Secret manager] |
| `FIRST_SUPERUSER` | GitHub Secret | admin@example.com |
| `FIRST_SUPERUSER_PASSWORD` | GitHub Secret | [Secret manager] |
| `SMTP_HOST` | GitHub Secret | [Email service] |
| `SENTRY_DSN` | GitHub Secret | https://xxxx@sentry.io/yyyy |

### Services

| Service | Type | Config | Notes |
|---------|------|--------|-------|
| PostgreSQL 18 | Database | Managed or self-hosted | Daily backups, replication |
| FastAPI | Backend | 4+ workers | Auto-restart, health checks |
| React | Frontend | Production build | Cached, minified |
| Traefik | Reverse Proxy | Let's Encrypt SSL | Auto-renew, rate limiting |
| Sentry | Error Tracking | Enabled | Real-time alerts |

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
cp .env.example .env
# Edit .env with your values
```

### Staging & Production

Set via GitHub Secrets (encrypted, never logged):

**Required secrets:**
- `DOMAIN_STAGING`, `DOMAIN_PRODUCTION`
- `STACK_NAME_STAGING`, `STACK_NAME_PRODUCTION`
- `SECRET_KEY` (generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `POSTGRES_PASSWORD` (generate secure password)
- `FIRST_SUPERUSER_PASSWORD` (generate secure password)
- `EMAILS_FROM_EMAIL` (e.g., noreply@example.com)
- Other secrets as needed (SMTP, Sentry, etc.)

**How to set:**

1. Go to GitHub: Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each variable

**How to reference in workflow:**

```yaml
- name: Deploy
  env:
    DOMAIN: ${{ secrets.DOMAIN_STAGING }}
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

### Secret Rotation

For production:

```bash
# Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update GitHub Secret
# Redeploy application
git tag v1.2.4 && git push origin v1.2.4
```

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

### Database Connection Issues

- Verify `POSTGRES_SERVER` (localhost local, db in Docker, managed-db.example.com in cloud)
- Verify `POSTGRES_PASSWORD` matches
- Check networking: `docker compose logs db` (local) or SSH to server (prod)

### Traefik/HTTPS Issues

- Check Traefik logs: `docker compose logs proxy` (local) or `docker logs traefik` (prod)
- Verify domain DNS points to server IP
- Let's Encrypt rate limits (production only)

### Email Not Working

- **Local**: Mailcatcher at http://localhost:1080
- **Staging/Prod**: Check SMTP_HOST, SMTP_USER, SMTP_PASSWORD via Secrets
- Test: Send email via admin panel, check logs, verify Sentry

## Related

- [Setup Guide](../getting-started/setup.md)
- [Development Workflow](../getting-started/development.md)
- [Incidents Runbook](../runbooks/incidents.md)
- [CI/CD Pipeline](./ci-pipeline.md)
