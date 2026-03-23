# Kila Platform — Operations SOP

**Audience:** Operations team, SRE, on-call engineers
**Scope:** End-to-end coverage — production server, Docker containers, database, daily pipeline, Stripe billing, data backfill
**Server:** Hetzner `89.167.87.10` — all production workloads run here

---

## Table of Contents

1. [Server Access & Orientation](#1-server-access--orientation)
2. [Container Health & Management](#2-container-health--management)
3. [Database Operations](#3-database-operations)
4. [Daily Pipeline — Monitoring & Troubleshooting](#4-daily-pipeline--monitoring--troubleshooting)
5. [Ofelia Job Scheduler Issues](#5-ofelia-job-scheduler-issues)
6. [Nginx / TLS Issues](#6-nginx--tls-issues)
7. [Backend API Issues](#7-backend-api-issues)
8. [Frontend Issues](#8-frontend-issues)
9. [Stripe & Billing Issues](#9-stripe--billing-issues)
10. [Subscription State Issues](#10-subscription-state-issues)
11. [Deployment Procedures](#11-deployment-procedures)
12. [Data Backfill Procedures](#12-data-backfill-procedures)
13. [Log Access Guide](#13-log-access-guide)
14. [Emergency Runbook](#14-emergency-runbook)

---

## 1. Server Access & Orientation

### SSH Access

```bash
# Admin access (for operations, investigation, container management)
ssh -i ~/.ssh/id_ed25519_hetzner spekila_admin@89.167.87.10

# Deployer access (used by GitHub Actions CI/CD — limited sudo)
ssh -i ~/.ssh/id_ed25519_hetzner deployer@89.167.87.10
```

### Directory Layout

```
/opt/geo/
├── kila/                         # Main web app (frontend + backend)
│   ├── docker-compose.prod.yml   # Single compose file for ALL containers
│   ├── nginx.prod.conf           # Nginx reverse proxy config
│   ├── certs/                    # Cloudflare Origin CA certs (origin.crt, origin.key)
│   ├── backend/                  # Python FastAPI backend
│   └── frontend/                 # React TypeScript SPA
├── kila-scraper/                 # Standalone scraper service + job runner
│   ├── app/jobs/                 # All pipeline jobs
│   └── .env.prod                 # Scraper environment config
└── data/                         # Local JSON backups from scraper
    └── brand/
        └── YYYY-MM-DD/           # Daily result files
```

### Running Containers

All 5 containers are managed by a single compose file:

```bash
# From /opt/geo — always use this path
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml ps
```

| Container | Role | Port |
|-----------|------|------|
| `kila-nginx-1` | Reverse proxy, TLS termination | 80, 443 |
| `kila-frontend-1` | React SPA (nginx inside) | internal:80 |
| `kila-backend-1` | FastAPI API | internal:8000 |
| `kila-scraper-1` | Scraper + pipeline job host | internal |
| `kila-ofelia-1` | Cron job scheduler | internal |

### Database

PostgreSQL 17 running directly on the host machine (not in Docker).

- **Host (from containers):** `host.docker.internal` (resolves to host gateway)
- **Port:** 5432
- **Database:** `kila_intelligence`
- **Connection (from server host):** `psql -U <db_user> -d kila_intelligence`

---

## 2. Container Health & Management

### Issue: One or more containers are down

**Verify:**

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml ps
# Look for containers not in "running" state
```

**Fix — Restart a specific container:**

```bash
docker compose -f kila/docker-compose.prod.yml restart backend
docker compose -f kila/docker-compose.prod.yml restart frontend
docker compose -f kila/docker-compose.prod.yml restart scraper
docker compose -f kila/docker-compose.prod.yml restart nginx
docker compose -f kila/docker-compose.prod.yml restart ofelia
```

**Fix — Restart all containers:**

```bash
docker compose -f kila/docker-compose.prod.yml up -d
```

**Fix — Container keeps crashing (exit loop):**

```bash
# Check the last 100 lines of logs for crash reason
docker compose -f kila/docker-compose.prod.yml logs --tail=100 backend
docker compose -f kila/docker-compose.prod.yml logs --tail=100 scraper

# If backend fails on startup it's likely a DB migration issue or config error
# See Section 3 for DB issues, Section 7 for backend issues
```

### Issue: Container is running but unhealthy / not serving

**Verify backend:**

```bash
# From the server, bypass nginx and hit backend directly
curl -s http://localhost:8000/api/v1/health   # if health endpoint exists
# Or use docker exec
docker exec kila-backend-1 curl -s http://localhost:8000/docs | head -5
```

**Verify frontend:**

```bash
docker exec kila-frontend-1 curl -s http://localhost:80 | head -5
```

**Verify nginx is proxying correctly:**

```bash
curl -sk https://www.spekila.com/api/v1/    # Should return JSON (not 502)
curl -sk https://www.spekila.com/           # Should return HTML
```

### Issue: Out of disk space

**Verify:**

```bash
df -h /
du -sh /opt/geo/data/brand/*/     # Check data directory growth
docker system df                   # Docker image/volume space usage
```

**Fix — Clean up old Docker images:**

```bash
docker image prune -f              # Remove dangling images only (safe)
docker system prune -f             # Remove stopped containers, dangling images, unused networks
# WARNING: do NOT use --volumes flag — that would delete data volumes
```

**Fix — Remove old data backups (keep last 30 days):**

```bash
# List what's there first
ls -la /opt/geo/data/brand/

# Remove directories older than 30 days
find /opt/geo/data/brand/ -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

---

## 3. Database Operations

### Issue: Backend/scraper cannot connect to database

**Verify connection from host:**

```bash
psql -U <db_user> -d kila_intelligence -c "SELECT 1;"
```

**Verify connection from inside a container:**

```bash
docker exec kila-backend-1 python -c "
import asyncio, asyncpg
async def test():
    conn = await asyncpg.connect('postgresql://<user>:<pass>@host.docker.internal:5432/kila_intelligence')
    print(await conn.fetchval('SELECT version()'))
    await conn.close()
asyncio.run(test())
"
```

**If PostgreSQL is not running:**

```bash
# Check PostgreSQL service status
sudo systemctl status postgresql

# Start if stopped
sudo systemctl start postgresql

# Check PostgreSQL logs
sudo journalctl -u postgresql -n 50
```

**If containers cannot reach host.docker.internal:**

```bash
# Verify the extra_hosts mapping is in place
docker inspect kila-backend-1 | grep -A5 "ExtraHosts"
# Should show "host.docker.internal:host-gateway"
# If missing, check docker-compose.prod.yml and redeploy
```

### Issue: Database migrations are missing / schema out of sync

**Symptoms:** Backend crashes on startup with `relation does not exist` errors, or API returns 500 on certain endpoints.

**Verify — Check applied migrations:**

```bash
docker exec kila-backend-1 alembic current
docker exec kila-backend-1 alembic history --verbose
```

**Verify — Check what's pending:**

```bash
docker exec kila-backend-1 alembic heads
```

**Fix — Apply pending migrations:**

```bash
# Migrations run automatically on backend startup via prestart.sh
# But you can also run manually:
docker exec kila-backend-1 alembic upgrade head

# If the backend is not running, run it as a one-off:
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml run --rm backend alembic upgrade head
```

**Fix — Roll back one migration:**

```bash
docker exec kila-backend-1 alembic downgrade -1
```

**Known migration history (in order):**

| Description |
|-------------|
| `e2412789c190` — Initialize models |
| `f1a2b3c4d5e6` — Add external_user_id to users |
| `d98dd8ec85a3` — Replace integer IDs with UUIDs |
| `9c0a54914c78` — Add max length for string/varchar |
| `f1fa28918ba4` — Create user_subscriptions table |
| `1a31ce608336` — Add cascade delete relationships |
| `a3c72f81b9d0` — Add is_super_user to user_subscriptions |
| `b4d91e2f7c3a` — Add trailing window metrics |
| `c5e82d93f0b1` — Add brand_user table and brand columns |
| `95d44b33e6b4` — Add past_due subscription status |
| `b3f1cc820a11` — Add cancel_at_period_end and current_period_end |
| `c9e4f7a2b8d3` — Change awareness_daily_performance PK |
| `d1e2f3a4b5c6` — Add pipeline_run tables |
| `e3a1b2c4d5f6` — Multi-model support |

### Issue: Inspect database state

```bash
# Connect to DB from the server
psql -U <db_user> -d kila_intelligence

# Key queries:

-- Active users and their subscription tiers
SELECT u.email, s.tier, s.status, s.trial_expires_at, s.is_super_user
FROM users u
JOIN user_subscriptions s ON u.user_id = s.user_id
ORDER BY u.created_at DESC;

-- Pipeline run history (last 7)
SELECT run_id, pipeline_name, status, started_at, completed_at
FROM pipeline_run
ORDER BY started_at DESC
LIMIT 7;

-- Per-job status for a specific run
SELECT job_name, status, attempts, started_at, completed_at, error_message
FROM pipeline_job_run
WHERE run_id = '<run_id>'
ORDER BY started_at;

-- Active brand prompts
SELECT b.brand_name, bp.prompt_text, bp.is_active, bp.ai_model
FROM brand_prompts bp
JOIN brands b ON bp.brand_id = b.brand_id
WHERE bp.is_active = true
ORDER BY b.brand_name;

-- Latest brand search results
SELECT b.brand_name, bsr.search_date, bsr.rank, bsr.visibility_score
FROM brand_search_results bsr
JOIN brands b ON bsr.brand_id = b.brand_id
ORDER BY bsr.search_date DESC, b.brand_name
LIMIT 50;
```

---

## 4. Daily Pipeline — Monitoring & Troubleshooting

### Pipeline Overview

The daily pipeline runs at **02:00 AM UTC** every day inside the `kila-scraper-1` container.

**Stages:**

| Stage | Jobs | Parallelism | Retries |
|-------|------|-------------|---------|
| Stage 0 | subscription_eligibility_job | sequential | 2 |
| Stage 1 | brand_search_response_job | sequential | 1 |
| Stage 2 | brand_search_basic_metrics_job, brand_search_competitors_basic_metrics_job | parallel | 2 each |
| Stage 3 | brand_awareness_performance_job, brand_competitors_awareness_performance_job | parallel | 2 each |
| Stage 4 | 9 signal jobs (competitive_dominance, competitive_erosion, competitor_breakthrough, growth_deceleration, weak_structural_position, rank_displacement, fragile_leadership, volatility_spike, new_entrant) | parallel | 2 each |

**Pipeline stops immediately if any stage fails.** Stages 2–4 only run if Stage 1 completes successfully.

### Issue: Daily pipeline did not run at all

**Verify — Check Ofelia logs:**

```bash
docker compose -f kila/docker-compose.prod.yml logs --tail=100 ofelia
# Look for lines like:
# "Starting job" brand-search-daily
# Or absence of any such line around 02:00 UTC
```

**Verify — Check what schedule Ofelia has loaded:**

```bash
docker logs kila-ofelia-1 2>&1 | grep -i "brand-search"
# Expected:
# "python -m app.jobs.daily_pipeline" - "0 0 2 * * *"
```

**Verify — Check scraper container labels:**

```bash
docker inspect kila-scraper-1 | grep -A5 "ofelia"
# Should show:
# "ofelia.enabled": "true"
# "ofelia.job-exec.brand-search-daily.schedule": "0 0 2 * * *"
# "ofelia.job-exec.brand-search-daily.command": "python -m app.jobs.daily_pipeline"
```

**Root cause:** Ofelia reads container labels ONLY at its own startup. If the scraper was redeployed after Ofelia started, Ofelia still runs the old command with the old schedule.

**Fix:**

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml restart ofelia
# Wait 5-10 seconds, then verify:
docker logs kila-ofelia-1 2>&1 | tail -20
# Should show Ofelia re-reading labels and registering the job
```

### Issue: Pipeline ran but stopped mid-way / some stages missing

**Verify — Find last pipeline run ID:**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT run_id, status, started_at, completed_at
FROM pipeline_run
ORDER BY started_at DESC
LIMIT 5;
"
```

**Verify — Check which jobs failed:**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT job_name, status, attempts, error_message
FROM pipeline_job_run
WHERE run_id = '<run_id>'
ORDER BY started_at;
"
```

**Verify — Read scraper logs from when it ran:**

```bash
docker compose -f kila/docker-compose.prod.yml logs --since="2026-03-22T02:00:00" scraper
```

**Fix — Resume a failed pipeline run (skip already-succeeded jobs):**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.daily_pipeline --resume-run-id <run_id>
```

**Fix — Manually trigger the full pipeline:**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.daily_pipeline
```

**Fix — Dry run to verify what would run:**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.daily_pipeline --dry-run
```

### Issue: Stage 1 (brand_search_response_job) fails

Stage 1 queries Gemini AI for each active brand prompt. It fails if:

1. **Gemini API key is invalid or quota exceeded**

```bash
# Check the .env.prod file
docker exec kila-scraper-1 env | grep GEMINI
# Or check the scraper logs for specific Gemini error messages
docker compose -f kila/docker-compose.prod.yml logs scraper | grep -i "gemini\|quota\|api key"
```

2. **No active brand prompts**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT COUNT(*) FROM brand_prompts WHERE is_active = true;
"
# If 0, check subscription_eligibility_job deactivated all prompts — see Section 10
```

3. **Database write failure**

```bash
docker compose -f kila/docker-compose.prod.yml logs scraper | grep -i "error\|exception" | tail -30
```

**Fix — Run Stage 1 in isolation:**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.brand_search_jobs.brand_search_response_job \
  --mode daily --full-run
```

### Issue: Stage 2 (basic metrics) or Stage 3 (awareness performance) fails

These jobs compute metrics from data produced by Stage 1. They fail if:

1. Stage 1 produced no data (empty tables)
2. Database query errors

**Fix — Run a specific job in isolation:**

```bash
# Stage 2 jobs
docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_search_basic_metrics_job

docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_search_competitors_basic_metrics_job

# Stage 3 jobs (requires --type, --start, --end)
docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_awareness_performance_job \
  --type daily --start 2026-03-22 --end 2026-03-22

docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_competitors_awareness_performance_job \
  --type daily --start 2026-03-22 --end 2026-03-22
```

### Issue: Stage 4 (insight signals) fails

9 signal jobs run in parallel. Individual failures do not stop others in the same stage, but if any fail, the stage as a whole is marked failed.

**Fix — Run individual signal jobs:**

```bash
# Replace <signal_name> with one of:
# competitive_dominance, competitive_erosion, competitor_breakthrough,
# growth_deceleration, weak_structural_position, rank_displacement,
# fragile_leadership, volatility_spike, new_entrant
docker exec kila-scraper-1 \
  python -m app.jobs.brand_insight_jobs.<signal_name>_signal_job
```

**Fix — Run all Stage 4 jobs manually (sequential for debugging):**

```bash
for job in competitive_dominance competitive_erosion competitor_breakthrough \
           growth_deceleration weak_structural_position rank_displacement \
           fragile_leadership volatility_spike new_entrant; do
  echo "Running ${job}_signal_job..."
  docker exec kila-scraper-1 python -m app.jobs.brand_insight_jobs.${job}_signal_job
  echo "Exit: $?"
done
```

### Issue: Pipeline ran but metrics are wrong / missing for a date

**Verify — Check data exists for the date:**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT search_date, COUNT(*) as result_count
FROM brand_search_results
WHERE search_date = '2026-03-22'
GROUP BY search_date;
"

psql -U <db_user> -d kila_intelligence -c "
SELECT COUNT(*) FROM brand_search_visibility WHERE date = '2026-03-22';
SELECT COUNT(*) FROM brand_search_ranking WHERE date = '2026-03-22';
SELECT COUNT(*) FROM brand_awareness_daily_performance WHERE date = '2026-03-22';
"
```

**Fix — Backfill a specific date:** See Section 12.

---

## 5. Ofelia Job Scheduler Issues

### Issue: Ofelia not running the correct command

**Root cause:** Ofelia loads Docker container labels only at startup. After any scraper redeploy, Ofelia must be restarted to pick up the new labels.

**Verify current registered jobs:**

```bash
docker logs kila-ofelia-1 2>&1 | grep -E "job|schedule|command"
```

**Fix:**

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml restart ofelia
sleep 10
docker logs kila-ofelia-1 2>&1 | tail -20
# Expected output includes: "python -m app.jobs.daily_pipeline" - "0 0 2 * * *"
```

### Issue: Ofelia schedule is wrong (wrong time, not firing)

The schedule format is **6-field cron** (seconds, minutes, hours, day, month, weekday):

```
0 0 2 * * *
│ │ │
│ │ └── Hour: 2 (= 02:00 UTC)
│ └──── Minute: 0
└────── Second: 0
```

**Verify the label in docker-compose.prod.yml:**

```bash
grep -A5 "ofelia" /opt/geo/kila/docker-compose.prod.yml
```

**Fix — If schedule needs changing:** Edit `docker-compose.prod.yml`, then:

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml up -d scraper
docker compose -f kila/docker-compose.prod.yml restart ofelia
```

### Issue: Ofelia container crashed

```bash
# Check logs for crash reason
docker logs kila-ofelia-1 --tail=50

# Restart
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml restart ofelia
```

---

## 6. Nginx / TLS Issues

### Issue: Site returns 502 Bad Gateway

**502 means nginx is up but cannot reach backend or frontend.**

**Verify:**

```bash
# Check nginx logs
docker logs kila-nginx-1 --tail=50 | grep -i "502\|error\|upstream"

# Verify backend is reachable from nginx's network
docker exec kila-nginx-1 curl -s http://backend:8000/
# Should return something (JSON error or HTML), not "connection refused"

# Verify frontend is reachable
docker exec kila-nginx-1 curl -s http://frontend:80/ | head -3
```

**Fix:**

```bash
cd /opt/geo
# Restart the failing upstream
docker compose -f kila/docker-compose.prod.yml restart backend
# Or frontend if that's failing
docker compose -f kila/docker-compose.prod.yml restart frontend
```

### Issue: SSL/TLS certificate expired or errors

**Verify:**

```bash
# Check cert expiry
openssl x509 -enddate -noout -in /opt/geo/kila/certs/origin.crt
# Output: notAfter=<date>

# Test TLS from outside
openssl s_client -connect www.spekila.com:443 -servername www.spekila.com < /dev/null 2>&1 | grep -E "Verify|expire"
```

**Fix — Replace expired certs (Cloudflare Origin CA):**

1. Log in to Cloudflare → SSL/TLS → Origin Server → Create Certificate
2. Copy the certificate and key to `/opt/geo/kila/certs/origin.crt` and `origin.key`
3. Reload nginx:

```bash
docker compose -f kila/docker-compose.prod.yml restart nginx
```

### Issue: API calls return 504 Gateway Timeout

**504 means the backend took longer than 120 seconds to respond** (nginx read_timeout is 120s).

**Fix:**

```bash
# Check what's slow in backend logs
docker logs kila-backend-1 --tail=100 | grep -i "slow\|timeout\|error"

# Check DB query performance
psql -U <db_user> -d kila_intelligence -c "
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

### Issue: HTTP not redirecting to HTTPS

**Verify nginx config:**

```bash
grep -A3 "listen 80" /opt/geo/kila/nginx.prod.conf
# Should show: return 301 https://...
```

**Fix — Reload nginx config without downtime:**

```bash
docker exec kila-nginx-1 nginx -t    # Verify config is valid first
docker exec kila-nginx-1 nginx -s reload
```

---

## 7. Backend API Issues

### Issue: Backend fails to start

**Check startup logs:**

```bash
docker logs kila-backend-1 --tail=100
```

**Common causes:**

1. **Database migration failure** (most common)

```bash
# Run prestart manually to see exact error
docker exec kila-backend-1 bash scripts/prestart.sh
```

2. **Missing environment variable**

```bash
docker exec kila-backend-1 env | grep -E "ENVIRONMENT|DATABASE|STRIPE|CLERK"
# Check /opt/geo/kila/backend/.env.prod has all required values
```

3. **Cannot reach database**

```bash
docker exec kila-backend-1 python app/backend_pre_start.py
# This runs the DB readiness check — will show exact connection error
```

### Issue: API returns 500 Internal Server Error on specific endpoints

**Check backend logs in real time:**

```bash
docker logs kila-backend-1 -f 2>&1 | grep -i "error\|exception\|traceback"
```

**Reproduce with curl:**

```bash
curl -sk https://www.spekila.com/api/v1/<endpoint> \
  -H "Authorization: Bearer <token>" \
  -w "\nHTTP Status: %{http_code}\n"
```

**Fix — Restart backend:**

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml restart backend
```

### Issue: Clerk JWT validation failing (401 on all API calls)

The frontend uses Clerk for authentication. The Clerk publishable key is baked into the frontend Docker image at build time. The backend validates Clerk JWTs.

**Verify:**

```bash
# Check backend has the correct Clerk settings
docker exec kila-backend-1 env | grep CLERK

# Check frontend was built with correct Clerk key (test vs prod)
docker inspect kila-frontend-1 | grep CLERK
# IMPORTANT: The compose file currently has pk_test_... (test key)
# If production Clerk account requires pk_live_..., the frontend image must be rebuilt
```

**Fix — Rebuild frontend with correct Clerk key:**

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml build frontend
docker compose -f kila/docker-compose.prod.yml up -d frontend
```

---

## 8. Frontend Issues

### Issue: Frontend shows blank page / JS errors

**Verify build was successful:**

```bash
docker logs kila-frontend-1 --tail=30
# The frontend is a static nginx — should show successful startup
```

**Verify static files are served:**

```bash
curl -sk https://www.spekila.com/ | grep -c "<!DOCTYPE"
# Should return 1 (the HTML page)
```

**Fix — Force rebuild and redeploy frontend:**

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml build --no-cache frontend
docker compose -f kila/docker-compose.prod.yml up -d frontend
```

### Issue: Frontend cannot reach the backend API (CORS errors)

CORS is controlled by the backend configuration, not nginx.

**Verify:**

```bash
curl -sk https://www.spekila.com/api/v1/ \
  -H "Origin: https://www.spekila.com" \
  -I | grep -i "access-control"
# Should show: Access-Control-Allow-Origin: https://www.spekila.com
```

**Fix — Check and update CORS config in backend:**

```bash
docker exec kila-backend-1 grep -r "CORS\|origins" /app/app/main.py
```

---

## 9. Stripe & Billing Issues

### Issue: User paid but subscription not upgraded

**Verify — Check Stripe webhook delivery:**

1. Go to Stripe Dashboard → Developers → Webhooks
2. Find your webhook endpoint (`https://www.spekila.com/api/v1/webhooks/stripe`)
3. Check recent events for `checkout.session.completed` — was it delivered? What was the response?

**Verify — Check backend logs for the event:**

```bash
docker logs kila-backend-1 | grep -i "stripe\|checkout\|webhook" | tail -30
```

**Verify — Check user subscription state in DB:**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT u.email, s.tier, s.status, s.stripe_customer_id, s.stripe_subscription_id, s.current_period_end
FROM users u
JOIN user_subscriptions s ON u.user_id = s.user_id
WHERE u.email = '<user@example.com>';
"
```

**Fix — Manually replay the webhook:**

1. Stripe Dashboard → Developers → Webhooks → Select endpoint
2. Find the failed event → Click "Resend"

**Fix — Manually upgrade user subscription in DB (emergency only):**

```bash
psql -U <db_user> -d kila_intelligence -c "
UPDATE user_subscriptions
SET tier = 'pro',
    status = 'active',
    stripe_customer_id = '<cus_xxx>',
    stripe_subscription_id = '<sub_xxx>'
WHERE user_id = '<user_id>';
"
```

### Issue: Stripe webhook signature verification failing

**Symptoms:** Backend logs show "Invalid Stripe webhook signature"; Stripe dashboard shows 400 responses.

**Root cause:** The `STRIPE_WEBHOOK_SECRET` in `.env.prod` does not match the webhook secret in Stripe Dashboard.

**Fix:**

1. Go to Stripe Dashboard → Developers → Webhooks → Select endpoint → Signing secret → Reveal
2. Copy the secret (starts with `whsec_...`)
3. Update `/opt/geo/kila/backend/.env.prod`:

```bash
# Edit on server
nano /opt/geo/kila/backend/.env.prod
# Update: STRIPE_WEBHOOK_SECRET=whsec_...
```

4. Restart backend:

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml restart backend
```

### Issue: Webhook events handled but fields not mapped correctly

The webhook handler uses the following lookup priority for `customer.subscription.updated`:

1. `metadata.user_id` (set during checkout — most reliable)
2. `stripe_subscription_id`
3. `stripe_customer_id`

If none match, the event is logged as "ignored". Check:

```bash
docker logs kila-backend-1 | grep -i "not_found\|ignored\|missing metadata" | tail -20
```

### Events handled by the webhook

| Stripe Event | Action |
|--------------|--------|
| `checkout.session.completed` | Upgrade tier to `pro`, set `status=active`, save Stripe IDs |
| `customer.subscription.updated` | Update tier/status, handle `cancel_at_period_end` |
| `customer.subscription.deleted` | Set `status=cancelled`, deactivate all brands and prompts |
| `invoice.payment_failed` | Set `status=past_due` (grace period — user keeps access) |

---

## 10. Subscription State Issues

### Issue: User cannot access the app (gets blocked)

Subscription states that block access: `expired`, `cancelled`. `past_due` users keep access.

**Verify:**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT u.email, s.tier, s.status, s.is_super_user, s.trial_expires_at, s.current_period_end
FROM users u
JOIN user_subscriptions s ON u.user_id = s.user_id
WHERE u.email = '<user@example.com>';
"
```

**Fix — Re-activate a legitimate user (emergency):**

```bash
psql -U <db_user> -d kila_intelligence -c "
UPDATE user_subscriptions
SET status = 'active'
WHERE user_id = '<user_id>';
"

-- Also re-activate their brands and prompts:
UPDATE brands SET is_active = true
WHERE brand_id IN (
  SELECT brand_id FROM brand_user WHERE user_id = '<user_id>'
);

UPDATE brand_prompts SET is_active = true
WHERE user_id = '<user_id>';
```

### Issue: All user prompts were deactivated unexpectedly

The `subscription_eligibility_job` (Stage 0 of daily pipeline) deactivates prompts for:
- Users with `status IN (expired, cancelled)` who are not super users
- Free trial users whose `trial_expires_at` has passed

**Verify — Find recently deactivated users:**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT u.email, s.tier, s.status, s.trial_expires_at, s.is_super_user
FROM users u
JOIN user_subscriptions s ON u.user_id = s.user_id
WHERE s.status IN ('expired', 'cancelled')
  AND s.is_super_user = false;
"
```

**Fix — Grant super_user status to bypass all checks:**

```bash
psql -U <db_user> -d kila_intelligence -c "
UPDATE user_subscriptions
SET is_super_user = true
WHERE user_id = '<user_id>';
"
```

### Issue: User cancellation not reflected in dashboard

After `customer.subscription.deleted` fires, brands and prompts are immediately deactivated.

**Verify the scraper will skip them:**

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT bp.prompt_text, bp.is_active, b.is_active as brand_active
FROM brand_prompts bp
JOIN brands b ON bp.brand_id = b.brand_id
WHERE bp.user_id = '<user_id>';
"
```

---

## 11. Deployment Procedures

### Deploying kila (frontend + backend)

**Trigger:** Push to `main` or `master` branch of `brucezy/kila` on GitHub.

**GitHub Actions does:**
1. SSH to server as `deployer`
2. `cd /opt/geo && git pull` (for kila-models and kila)
3. `docker compose -f kila/docker-compose.prod.yml up --build -d`
4. Runs `prestart.sh` in backend on startup: alembic upgrade head → initial_data

**Monitor deployment:**

```bash
# Watch container rebuild in real time
docker compose -f kila/docker-compose.prod.yml logs -f backend frontend

# Verify new image is running
docker compose -f kila/docker-compose.prod.yml ps
```

### Deploying kila-scraper

**Trigger:** Push to `main` or `master` branch of `brucezy/kila-scraper` on GitHub.

**GitHub Actions does:**
1. SSH to server as `deployer`
2. `cd /opt/geo/kila-scraper && git pull`
3. `docker compose -f kila/docker-compose.prod.yml up --build -d scraper`
4. `docker compose -f kila/docker-compose.prod.yml restart ofelia`

**CRITICAL:** Always restart Ofelia after scraper redeploy. The deploy workflow does this automatically now, but if doing a manual redeploy, always follow with an Ofelia restart.

### Manual deployment (bypassing CI)

```bash
ssh -i ~/.ssh/id_ed25519_hetzner spekila_admin@89.167.87.10
cd /opt/geo

# Pull latest code
cd kila && git pull origin main && cd ..
cd kila-scraper && git pull origin main && cd ..

# Rebuild and restart all
docker compose -f kila/docker-compose.prod.yml up --build -d

# Always restart Ofelia after any scraper change
docker compose -f kila/docker-compose.prod.yml restart ofelia
```

### Issue: Deployment failed mid-way (containers in mixed state)

**Verify:**

```bash
docker compose -f kila/docker-compose.prod.yml ps
docker compose -f kila/docker-compose.prod.yml logs --tail=50
```

**Fix — Force clean redeploy:**

```bash
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml down
docker compose -f kila/docker-compose.prod.yml up --build -d
```

### Issue: New migration fails during deployment

The backend prestart.sh runs `alembic upgrade head` on every startup. If a migration has a bug, the backend will fail to start.

**Fix — Roll back the migration:**

```bash
# The backend container is failing, so use `run --rm` to start a temporary one
docker compose -f kila/docker-compose.prod.yml run --rm backend alembic downgrade -1

# Fix the migration code, redeploy
```

---

## 12. Data Backfill Procedures

### Backfill — Run pipeline for a past date

The pipeline uses `date.today()` for Stage 3 date arguments. To backfill a specific date:

**Step 1 — Backfill search responses (Stage 1):**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.brand_search_jobs.brand_search_response_job \
  --mode daily --full-run
# Note: search responses are always written with today's date.
# For true historical backfill, you need to write a custom script or restore from backup.
```

**Step 2 — Backfill basic metrics for a specific date:**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_search_basic_metrics_job
# Pass --date flag if supported, otherwise check the job for date override options
```

**Step 3 — Backfill awareness performance for a date range:**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_awareness_performance_job \
  --type daily --start 2026-03-20 --end 2026-03-22

docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_competitors_awareness_performance_job \
  --type daily --start 2026-03-20 --end 2026-03-22
```

**Step 4 — Backfill weekly metrics:**

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.brand_analysis_jobs.brand_awareness_performance_job \
  --type weekly --start 2026-03-16 --end 2026-03-22
```

### Backfill — Restore from JSON backup files

The scraper writes daily JSON backups to `/opt/geo/data/brand/YYYY-MM-DD/`.

**Check available backups:**

```bash
ls -la /opt/geo/data/brand/
```

**Load from backup into DB:**

The `brand_search_result_backup_job.py` handles backup/restore. Check for a `--restore` flag:

```bash
docker exec kila-scraper-1 \
  python -m app.jobs.brand_search_result_backup_job --help
```

### Backfill — Fix missing signal insights

After backfilling metrics through Stage 3, rerun signal jobs:

```bash
for job in competitive_dominance competitive_erosion competitor_breakthrough \
           growth_deceleration weak_structural_position rank_displacement \
           fragile_leadership volatility_spike new_entrant; do
  echo "=== Running ${job}_signal_job ==="
  docker exec kila-scraper-1 \
    python -m app.jobs.brand_insight_jobs.${job}_signal_job
done
```

### Backfill — Delete and redo a specific date's data

Use with caution — this is destructive.

```bash
psql -U <db_user> -d kila_intelligence

-- Delete all data for a specific date
BEGIN;

DELETE FROM brand_search_results WHERE search_date = '2026-03-22';
DELETE FROM brand_search_visibility WHERE date = '2026-03-22';
DELETE FROM brand_search_ranking WHERE date = '2026-03-22';
DELETE FROM brand_awareness_daily_performance WHERE date = '2026-03-22';

-- Also delete competitor data
DELETE FROM brand_search_competitor_visibility WHERE date = '2026-03-22';
DELETE FROM brand_search_competitor_ranking WHERE date = '2026-03-22';
DELETE FROM brand_competitors_awareness_daily_performance WHERE date = '2026-03-22';

-- Signal data (may not be date-partitioned — check schema before deleting)
-- DELETE FROM brand_insight_signals WHERE date = '2026-03-22';

COMMIT;
```

Then re-run the full pipeline for that date as described above.

---

## 13. Log Access Guide

### Real-time log tailing

```bash
# All containers combined
docker compose -f kila/docker-compose.prod.yml logs -f

# Specific container
docker compose -f kila/docker-compose.prod.yml logs -f backend
docker compose -f kila/docker-compose.prod.yml logs -f scraper
docker compose -f kila/docker-compose.prod.yml logs -f ofelia
docker compose -f kila/docker-compose.prod.yml logs -f nginx
```

### Historical logs

```bash
# Last N lines
docker compose -f kila/docker-compose.prod.yml logs --tail=200 scraper

# Since a specific time (ISO 8601 or relative)
docker compose -f kila/docker-compose.prod.yml logs --since="2026-03-22T02:00:00" scraper
docker compose -f kila/docker-compose.prod.yml logs --since=24h backend

# Between time range
docker compose -f kila/docker-compose.prod.yml logs \
  --since="2026-03-22T02:00:00" \
  --until="2026-03-22T06:00:00" \
  scraper
```

### Searching logs

```bash
# Pipeline failures
docker compose -f kila/docker-compose.prod.yml logs scraper | grep -i "failed\|error\|exception"

# Stripe webhook activity
docker compose -f kila/docker-compose.prod.yml logs backend | grep -i "stripe\|webhook\|subscription"

# Gemini API errors
docker compose -f kila/docker-compose.prod.yml logs scraper | grep -i "gemini\|quota\|429\|403"

# Nginx access log format: method path status size
docker logs kila-nginx-1 | grep " 5[0-9][0-9] "  # 5xx errors
docker logs kila-nginx-1 | grep "/api/"           # API requests
```

### Pipeline run logs (from DB)

```bash
psql -U <db_user> -d kila_intelligence -c "
SELECT
  pr.started_at,
  pr.status as pipeline_status,
  pj.job_name,
  pj.status as job_status,
  pj.attempts,
  LEFT(pj.error_message, 200) as error_preview
FROM pipeline_run pr
LEFT JOIN pipeline_job_run pj ON pr.run_id = pj.run_id
WHERE pr.started_at > NOW() - INTERVAL '7 days'
ORDER BY pr.started_at DESC, pj.started_at;
"
```

---

## 14. Emergency Runbook

### Site is completely down (all requests failing)

**Triage order:**

```bash
ssh -i ~/.ssh/id_ed25519_hetzner spekila_admin@89.167.87.10

# Step 1: Check all containers are running
cd /opt/geo
docker compose -f kila/docker-compose.prod.yml ps

# Step 2: If any are down, restart them
docker compose -f kila/docker-compose.prod.yml up -d

# Step 3: Check nginx health
docker logs kila-nginx-1 --tail=30

# Step 4: Verify nginx can reach upstreams
docker exec kila-nginx-1 curl -s http://backend:8000/ | head -5
docker exec kila-nginx-1 curl -s http://frontend:80/ | head -5

# Step 5: Check DB is up
psql -U <db_user> -d kila_intelligence -c "SELECT 1;"

# Step 6: Check server resources
free -h       # Memory
df -h /       # Disk
top -bn1 | head -20  # CPU
```

### Daily pipeline has not run for 2+ days

```bash
# 1. Check last successful run
psql -U <db_user> -d kila_intelligence -c "
SELECT run_id, status, started_at
FROM pipeline_run
ORDER BY started_at DESC
LIMIT 5;
"

# 2. Check Ofelia is running and has correct schedule
docker compose -f kila/docker-compose.prod.yml ps ofelia
docker logs kila-ofelia-1 | grep "brand-search" | tail -10

# 3. If Ofelia has wrong schedule or job:
docker compose -f kila/docker-compose.prod.yml restart ofelia

# 4. Manually trigger missed runs (one per day)
docker exec kila-scraper-1 python -m app.jobs.daily_pipeline

# 5. For each missed day, backfill metrics (see Section 12)
```

### User reports data is stale (dashboard shows old data)

```bash
# Check last pipeline run
psql -U <db_user> -d kila_intelligence -c "
SELECT started_at, status FROM pipeline_run ORDER BY started_at DESC LIMIT 3;
"

# Check latest data date in metrics tables
psql -U <db_user> -d kila_intelligence -c "
SELECT MAX(search_date) FROM brand_search_results;
SELECT MAX(date) FROM brand_awareness_daily_performance;
"

# If data is stale, trigger manual pipeline run:
docker exec kila-scraper-1 python -m app.jobs.daily_pipeline
```

### Stripe payment succeeded but user stuck on free tier

```bash
# 1. Check user's current state
psql -U <db_user> -d kila_intelligence -c "
SELECT s.tier, s.status, s.stripe_customer_id, s.stripe_subscription_id
FROM user_subscriptions s
JOIN users u ON u.user_id = s.user_id
WHERE u.email = '<user@example.com>';
"

# 2. If stripe_customer_id is NULL but payment succeeded:
#    The webhook didn't fire or failed. Resend from Stripe Dashboard.

# 3. Emergency manual fix:
psql -U <db_user> -d kila_intelligence -c "
UPDATE user_subscriptions
SET tier = 'pro', status = 'active',
    stripe_customer_id = '<cus_xxx>',
    stripe_subscription_id = '<sub_xxx>'
WHERE user_id = '<user_id>';
"

# 4. Re-activate their brands and prompts
psql -U <db_user> -d kila_intelligence -c "
UPDATE brands SET is_active = true
WHERE brand_id IN (SELECT brand_id FROM brand_user WHERE user_id = '<user_id>');

UPDATE brand_prompts SET is_active = true WHERE user_id = '<user_id>';
"
```

### Disk space critical (>90% full)

```bash
# Find largest directories
du -sh /opt/geo/* /opt/geo/data/brand/* | sort -rh | head -20

# Clean Docker build cache (safe)
docker builder prune -f

# Clean old images (safe — keeps running containers' images)
docker image prune -f

# Remove old data backups (keep last 14 days)
find /opt/geo/data/brand/ -maxdepth 1 -type d -mtime +14 -exec rm -rf {} \;

# Remove Docker logs (Docker keeps container logs indefinitely by default)
# To check log file sizes:
find /var/lib/docker/containers/ -name "*.log" -exec du -sh {} \; | sort -rh | head -10
# Truncate a specific container log (container will keep running):
truncate -s 0 /var/lib/docker/containers/<container_id>/<container_id>-json.log
```

---

*Last updated: 2026-03-22*
*Maintainer: Engineering Team*
