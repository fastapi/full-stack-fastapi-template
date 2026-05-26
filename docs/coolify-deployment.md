# Well Apps — Coolify Deployment Guide

Deploy Well Apps to a VPS using [Coolify](https://coolify.io), an open-source self-hosted PaaS.

## Architecture

```
Internet (HTTPS)
    |
Coolify Traefik (auto-SSL via Let's Encrypt)
    |
    ├── dashboard.yourdomain.com  →  frontend (Nginx, port 80)
    ├── api.yourdomain.com        →  backend  (FastAPI, port 8000)
    └── (internal only)           →  db       (PostgreSQL 18)
```

Coolify manages Traefik, SSL certificates, and domain routing. The app uses
`compose.coolify.yml` — a simplified compose file without Traefik labels.

---

## Prerequisites

- A VPS with 2+ vCPUs, 4+ GB RAM, 40+ GB disk (Ubuntu 24.04 LTS recommended)
- A domain with DNS pointed to your VPS IP
- A wildcard DNS record: `*.yourdomain.com → VPS_IP`
- A GitHub account with access to `the-ai-buildr/well-apps`

---

## 1. Install Coolify on Your VPS

SSH into your server and run:

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

After installation, access the Coolify dashboard at `http://YOUR_VPS_IP:8000`.

Create your admin account and complete the initial setup wizard.

---

## 2. Connect GitHub to Coolify

### Create a GitHub App (recommended over deploy keys)

1. In Coolify: **Settings → Git Sources → Add**
2. Select **GitHub App**
3. Follow the OAuth flow — Coolify will create a GitHub App in your account
4. Grant access to the `the-ai-buildr/well-apps` repository

This gives Coolify push/webhook access for auto-deploy.

---

## 3. Configure GitHub Repository Secrets

Even though Coolify handles deployment, GitHub Actions still runs CI (tests,
linting). Set these secrets so CI continues to work.

### Using the `gh` CLI

```bash
# Authenticate (if not already)
gh auth login

# Navigate to your repo
cd well-apps

# --- CI secrets (repository-level) ---
gh secret set POSTGRES_PASSWORD --body "ci-test-password"
gh secret set POSTGRES_USER --body "postgres"
gh secret set POSTGRES_DB --body "app"
gh secret set SECRET_KEY --body "$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
gh secret set FIRST_SUPERUSER --body "admin@wellbeing.app"
gh secret set FIRST_SUPERUSER_PASSWORD --body "$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"

# --- Staging environment secrets ---
gh secret set DOMAIN_STAGING --env staging --body "staging.yourdomain.com"
gh secret set STACK_NAME_STAGING --env staging --body "well-apps-staging"

# --- Production environment secrets ---
gh secret set DOMAIN_PRODUCTION --env production --body "yourdomain.com"
gh secret set STACK_NAME_PRODUCTION --env production --body "well-apps-production"

# --- Shared across environments ---
for env in staging production; do
  gh secret set SECRET_KEY --env "$env" \
    --body "$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  gh secret set FIRST_SUPERUSER --env "$env" --body "admin@wellbeing.app"
  gh secret set FIRST_SUPERUSER_PASSWORD --env "$env" \
    --body "$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"
  gh secret set POSTGRES_PASSWORD --env "$env" \
    --body "$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  gh secret set EMAILS_FROM_EMAIL --env "$env" --body "noreply@yourdomain.com"
  gh secret set SMTP_HOST --env "$env" --body ""
  gh secret set SMTP_USER --env "$env" --body ""
  gh secret set SMTP_PASSWORD --env "$env" --body ""
done
```

### Create GitHub Environments

```bash
# Create staging and production environments
gh api repos/:owner/:repo/environments/staging -X PUT
gh api repos/:owner/:repo/environments/production -X PUT
```

For production, add a **required reviewers** protection rule in the GitHub UI:
**Settings → Environments → production → Required reviewers**.

---

## 4. Create the Coolify Project

### 4a. Create the Project

1. In Coolify dashboard: **Projects → Add**
2. Name: `Well Apps`
3. Create two environments: `staging` and `production`

### 4b. Add the Application (per environment)

For each environment (staging, production):

1. **Add New Resource → Docker Compose**
2. **Git Repository**: select `the-ai-buildr/well-apps`
3. **Branch**: `master` (production) or `develop` (staging)
4. **Docker Compose File**: `compose.coolify.yml`
5. **Build Pack**: Docker Compose

### 4c. Configure Domains

In the resource settings, configure the service domains:

| Service | Domain |
|---------|--------|
| `frontend` (port 80) | `dashboard.yourdomain.com` |
| `backend` (port 8000) | `api.yourdomain.com` |

For staging, use:

| Service | Domain |
|---------|--------|
| `frontend` (port 80) | `dashboard.staging.yourdomain.com` |
| `backend` (port 8000) | `api.staging.yourdomain.com` |

Coolify will automatically provision Let's Encrypt SSL certificates.

---

## 5. Set Environment Variables in Coolify

In the Coolify resource settings, go to **Environment Variables** and add:

### Required

| Variable | Example Value | Notes |
|----------|---------------|-------|
| `DOMAIN` | `yourdomain.com` | Your root domain |
| `ENVIRONMENT` | `production` | `staging` or `production` |
| `FRONTEND_HOST` | `https://dashboard.yourdomain.com` | Full URL to the frontend |
| `SECRET_KEY` | *(generate)* | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `FIRST_SUPERUSER` | `admin@wellbeing.app` | Admin email |
| `FIRST_SUPERUSER_PASSWORD` | *(generate)* | Strong password |
| `POSTGRES_USER` | `postgres` | |
| `POSTGRES_PASSWORD` | *(generate)* | Strong password |
| `POSTGRES_DB` | `well_apps` | |
| `POSTGRES_PORT` | `5432` | |
| `BACKEND_CORS_ORIGINS` | `https://dashboard.yourdomain.com` | Comma-separated allowed origins |
| `PROJECT_NAME` | `Well Apps` | Shown in API docs and emails |

### Optional

| Variable | Example Value | Notes |
|----------|---------------|-------|
| `SMTP_HOST` | `smtp.mailgun.org` | For email sending |
| `SMTP_USER` | `postmaster@yourdomain.com` | |
| `SMTP_PASSWORD` | *(your smtp password)* | |
| `SMTP_PORT` | `587` | |
| `SMTP_TLS` | `True` | |
| `EMAILS_FROM_EMAIL` | `noreply@yourdomain.com` | |
| `SENTRY_DSN` | `https://...@sentry.io/...` | Error tracking |
| `DOCKER_IMAGE_BACKEND` | `well-apps-backend` | |
| `DOCKER_IMAGE_FRONTEND` | `well-apps-frontend` | |

---

## 6. Deploy

### First deploy

Click **Deploy** in the Coolify dashboard. Coolify will:

1. Clone the repo
2. Build the backend and frontend Docker images
3. Start PostgreSQL and wait for it to be healthy
4. Run the prestart migration script
5. Start the backend and frontend services
6. Configure Traefik routing and SSL

### Auto-deploy on push

In the resource settings, enable **Auto Deploy** and select the branch.
Coolify installs a GitHub webhook that triggers a build on every push.

### Manual deploy via Coolify API

```bash
# Get your Coolify API token from Settings → API Tokens
COOLIFY_TOKEN="your-api-token"
COOLIFY_URL="https://coolify.yourdomain.com"

# Trigger a deployment
curl -X POST "$COOLIFY_URL/api/v1/deploy" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"uuid": "your-resource-uuid"}'
```

---

## 7. Post-Deploy Verification

```bash
# Health check
curl -f https://api.yourdomain.com/api/v1/utils/health-check/

# API docs
open https://api.yourdomain.com/docs

# Frontend
open https://dashboard.yourdomain.com
```

---

## 8. Backups

Configure automated PostgreSQL backups in Coolify:

1. Go to your resource → **Backups**
2. Select the `db` service
3. Set schedule (e.g., daily at 2 AM)
4. Choose backup destination:
   - **Local**: stored on the VPS (configure offsite sync separately)
   - **S3-compatible**: direct upload to S3, Backblaze B2, R2, etc.

### Manual backup

```bash
# SSH into your VPS
docker exec well-apps-db-1 pg_dump -U postgres well_apps > backup_$(date +%Y%m%d).sql
```

---

## 9. Monitoring

Coolify provides basic container monitoring (CPU, memory, disk). For
production, consider adding:

- **Sentry** — set `SENTRY_DSN` env var for error tracking
- **Uptime Kuma** — deploy as a separate Coolify service for uptime monitoring
- **Dozzle** — deploy for centralized container log viewing

---

## Compose Files Reference

| File | Use |
|------|-----|
| `compose.coolify.yml` | Coolify deployment (no Traefik labels) |
| `compose.yml` | Self-hosted production with external Traefik |
| `compose.override.yml` | Local development (hot-reload, mailcatcher) |
| `compose.traefik.yml` | Standalone Traefik proxy (not needed with Coolify) |

---

## Migrating from Self-Hosted Runner Deployment

If you previously deployed using the GitHub Actions self-hosted runner
workflow (`deploy-staging.yml` / `deploy-production.yml`), those workflows
are no longer needed for Coolify deployments. Coolify handles builds and
deploys directly via its GitHub webhook integration.

The CI workflows (`test-backend.yml`, `playwright.yml`, etc.) continue to
run as before — they validate code on push/PR and are independent of the
deployment method.

---

## Troubleshooting

**Build fails: "Variable not set"**
Check that all required environment variables are configured in the Coolify
resource settings. The `compose.coolify.yml` file uses `${VAR}` syntax
without the `?Variable not set` assertions, so missing vars will be empty
strings rather than hard errors — check Coolify logs for runtime issues.

**Database connection refused**
The prestart service waits for the database health check. If it still fails,
check that `POSTGRES_SERVER=db` is set (Coolify's shared network lets
services reach each other by service name).

**SSL certificate not provisioning**
Verify your DNS A record points to the VPS IP and the wildcard `*.domain`
is configured. Coolify's Traefik needs ports 80 and 443 open on the VPS
firewall.

**Frontend shows "Network Error"**
Check `VITE_API_URL` build arg in `compose.coolify.yml` — it must match
your API domain (`https://api.yourdomain.com`). This is baked into the
frontend at build time, so a redeploy is needed after changing the domain.
