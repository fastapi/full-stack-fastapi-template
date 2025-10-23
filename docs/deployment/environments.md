# Deployment Environments

**CurriculumExtractor Infrastructure**

## Environment Overview

This project supports three environments:
- **Local**: Development on your machine
- **Staging**: Pre-production testing (future)
- **Production**: Live application (future)

## Environment Configuration

Configuration via `.env` file and `ENVIRONMENT` variable.

### Local Environment (Current)

```bash
ENVIRONMENT=local
DOMAIN=localhost
FRONTEND_HOST=http://localhost:5173
PROJECT_NAME="CurriculumExtractor"
STACK_NAME=curriculum-extractor
```

**Characteristics:**
- ✅ Docker Compose with hot reload (`docker compose watch`)
- ✅ Permissive CORS (localhost)
- ✅ Default secrets allowed (with warnings)
- ✅ Debug logging enabled
- ✅ **Supabase PostgreSQL** (managed, Session Mode)
- ✅ Redis in Docker (ephemeral)
- ✅ Celery worker (4 processes)
- ✅ MailCatcher for email testing

**Access Points:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MailCatcher**: http://localhost:1080
- **Traefik Dashboard**: http://localhost:8090
- **Supabase Dashboard**: https://app.supabase.com/project/wijzypbstiigssjuiuvh

**Infrastructure:**
```
✅ Backend (FastAPI)      - localhost:8000
✅ Frontend (React)       - localhost:5173
✅ Database (Supabase)    - Managed PostgreSQL 17
✅ Redis                  - localhost:6379
✅ Celery Worker          - 4 processes
✅ Proxy (Traefik)        - localhost:80
✅ MailCatcher             - localhost:1080
```

### Staging Environment (Future)

```bash
ENVIRONMENT=staging
DOMAIN=staging.curriculumextractor.com
FRONTEND_HOST=https://dashboard.staging.curriculumextractor.com

# Supabase Staging Project (separate from dev)
SUPABASE_URL=https://staging-project.supabase.co
DATABASE_URL=postgresql+psycopg://postgres.staging-ref:***@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# Managed Redis (Upstash or Redis Cloud)
REDIS_URL=redis://username:password@staging-redis.upstash.io:6379
```

**Characteristics:**
- ✅ Production-like setup
- ✅ Supabase paid tier (dedicated resources)
- ✅ Managed Redis with persistence
- ✅ Celery workers (horizontal scaling)
- ✅ Sentry error tracking
- ✅ HTTPS via Traefik + Let's Encrypt
- ✅ Strict CORS (staging domain only)
- ✅ Secrets required (not "changethis")
- ✅ Real SMTP server (AWS SES)

**Infrastructure:**
```
Backend      - Docker container (auto-scaling)
Frontend     - Docker container (Nginx)
Database     - Supabase (paid tier, 2 GB+)
Redis        - Managed (Upstash/Redis Cloud)
Celery       - Multiple workers (scale based on load)
Storage      - Supabase Storage (5 GB+)
Monitoring   - Sentry
Proxy        - Traefik with HTTPS
```

### Production Environment (Future)

```bash
ENVIRONMENT=production
DOMAIN=curriculumextractor.com
FRONTEND_HOST=https://dashboard.curriculumextractor.com

# Supabase Production Project
SUPABASE_URL=https://prod-project.supabase.co
DATABASE_URL=postgresql+psycopg://postgres.prod-ref:***@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# Managed Redis with HA
REDIS_URL=redis://username:password@prod-redis.upstash.io:6379
```

**Characteristics:**
- ✅ High availability
- ✅ Supabase Pro/Team tier (dedicated compute)
- ✅ Redis with persistence + replication
- ✅ Celery workers (auto-scaling, 10+ processes)
- ✅ Sentry monitoring + alerts
- ✅ HTTPS via Traefik + Let's Encrypt
- ✅ Strict security (CORS, CSP headers)
- ✅ Performance optimization (caching, CDN)
- ✅ Secrets required (enforced, validated)
- ✅ Database backups (daily + PITR)
- ✅ Real SMTP (AWS SES with bounce handling)

**Infrastructure:**
```
Backend      - Docker Swarm/Kubernetes (multi-container)
Frontend     - Docker + CDN (Cloudflare)
Database     - Supabase Pro (8 GB+, read replicas)
Redis        - Managed HA cluster
Celery       - Auto-scaling workers (10-50 processes)
Storage      - Supabase Storage (50 GB+)
Monitoring   - Sentry + Grafana + Prometheus
Proxy        - Traefik with HTTPS + WAF
```

---

## Current Configuration (Local Development)

**Project Details:**
- **Supabase Project**: wijzypbstiigssjuiuvh
- **Region**: ap-south-1 (Mumbai, India)
- **Database**: PostgreSQL 17.6.1 (Session Mode)
- **Connection**: port 5432 (Supavisor pooler)
- **Pool Size**: 10 base + 20 overflow

**Configured Secrets:**
```bash
# ✅ Already configured in .env
SECRET_KEY=H_cEi7eTOM-uJxjB6v1LwxW0S1i4jK4TP2x6eH5RlvA
REDIS_PASSWORD=5WEQ47_uuNd-289-_ZnN79GmNY8LFWzy
FIRST_SUPERUSER=admin@curriculumextractor.com
FIRST_SUPERUSER_PASSWORD=kRZtEcmM3tRevtEh1CitNL6s_s5ciE7q

# Database (Supabase)
DATABASE_URL=postgresql+psycopg://postgres.wijzypbstiigssjuiuvh:Curriculumextractor1234!@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

---

## Required Secret Changes for Staging/Production

**MUST change before deployment:**

```bash
# Generate new secrets (do NOT reuse development secrets!)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Staging/Production .env
SECRET_KEY=<new-generated-key>
FIRST_SUPERUSER_PASSWORD=<new-strong-password>
REDIS_PASSWORD=<new-redis-password>

# Create separate Supabase projects
# - Staging: Create new Supabase project for staging
# - Production: Create new Supabase project for production
SUPABASE_URL=https://staging-or-prod.supabase.co
SUPABASE_SERVICE_KEY=<new-service-key>
DATABASE_URL=postgresql+psycopg://postgres.new-ref:***@...
```

**Security Requirements:**
- ✅ Secrets ≥32 characters
- ✅ Different secrets per environment
- ✅ Secrets stored in secret manager (not in git)
- ✅ Rotate secrets every 90 days
- ✅ Separate Supabase projects (dev/staging/prod)

The application will **fail to start** in staging/production with default or development secrets.

---

## Deployment with Docker Compose

See [deployment.md](../../deployment.md) in project root for detailed deployment instructions.

### Building Images

```bash
# Set environment
export ENVIRONMENT=production  # or staging

# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend
```

### Service Scaling

**Celery Workers** (horizontal scaling):
```bash
# Scale to 8 workers
docker compose up -d --scale celery-worker=8

# In docker-compose.yml (production):
services:
  celery-worker:
    deploy:
      replicas: 10  # Auto-scale to 10 workers
```

### Traefik Configuration

Production uses Traefik for:
- ✅ Reverse proxy
- ✅ Load balancing
- ✅ Automatic HTTPS certificates (Let's Encrypt)
- ✅ Domain routing
- ✅ Rate limiting (future)

**Subdomains:**
- `api.curriculumextractor.com` → Backend
- `dashboard.curriculumextractor.com` → Frontend

**Configuration** (docker-compose.yml labels):
```yaml
labels:
  - traefik.http.routers.backend.rule=Host(`api.curriculumextractor.com`)
  - traefik.http.routers.backend.tls.certresolver=le
  - traefik.http.routers.frontend.rule=Host(`dashboard.curriculumextractor.com`)
  - traefik.http.routers.frontend.tls.certresolver=le
```

---

## Environment Variables by Service

### Backend (FastAPI)

**Local Development:**
```env
# Core
ENVIRONMENT=local
PROJECT_NAME="CurriculumExtractor"
FRONTEND_HOST=http://localhost:5173

# Security
SECRET_KEY=<generated-32-chars>
FIRST_SUPERUSER=admin@curriculumextractor.com
FIRST_SUPERUSER_PASSWORD=<strong-password>

# Supabase (Managed PostgreSQL + Storage)
DATABASE_URL=postgresql+psycopg://postgres.wijzypbstiigssjuiuvh:***@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://wijzypbstiigssjuiuvh.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_KEY=<service-role-key>

# Redis + Celery
REDIS_PASSWORD=<redis-password>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# Storage Buckets
SUPABASE_STORAGE_BUCKET_WORKSHEETS=worksheets
SUPABASE_STORAGE_BUCKET_EXTRACTIONS=extractions

# CORS
BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173"

# Monitoring (optional)
SENTRY_DSN=

# Email (optional)
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=noreply@curriculumextractor.com
```

**Staging/Production:**
```env
# Core
ENVIRONMENT=production  # or staging
PROJECT_NAME="CurriculumExtractor"
FRONTEND_HOST=https://dashboard.curriculumextractor.com

# Security (NEW secrets, not dev ones!)
SECRET_KEY=<new-generated-secret>
FIRST_SUPERUSER=admin@curriculumextractor.com
FIRST_SUPERUSER_PASSWORD=<new-strong-password>

# Supabase (Separate projects for staging/prod!)
DATABASE_URL=postgresql+psycopg://postgres.prod-ref:***@aws-1-REGION.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://prod-ref.supabase.co
SUPABASE_ANON_KEY=<prod-anon-key>
SUPABASE_SERVICE_KEY=<prod-service-key>

# Managed Redis (Upstash, Redis Cloud, or AWS ElastiCache)
REDIS_PASSWORD=<new-redis-password>
REDIS_URL=redis://username:password@prod-redis.upstash.io:6379
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# Storage (same buckets, different project)
SUPABASE_STORAGE_BUCKET_WORKSHEETS=worksheets
SUPABASE_STORAGE_BUCKET_EXTRACTIONS=extractions

# CORS (strict!)
BACKEND_CORS_ORIGINS="https://dashboard.curriculumextractor.com"

# Monitoring (required!)
SENTRY_DSN=<your-sentry-dsn>

# Email (production SMTP)
SMTP_HOST=email-smtp.ap-south-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=<aws-ses-user>
SMTP_PASSWORD=<aws-ses-password>
SMTP_TLS=True
EMAILS_FROM_EMAIL=noreply@curriculumextractor.com
```

### Frontend (React)

**Local:**
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://wijzypbstiigssjuiuvh.supabase.co
VITE_SUPABASE_ANON_KEY=<anon-key>
```

**Production:**
```env
VITE_API_URL=https://api.curriculumextractor.com
VITE_SUPABASE_URL=https://prod-ref.supabase.co
VITE_SUPABASE_ANON_KEY=<prod-anon-key>
```

### Celery Worker

**Uses same environment variables as backend:**
- `DATABASE_URL` - For task database operations
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` - For Storage operations
- `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` - For task queue

---

## Database Management (Supabase)

### Migrations in Production

**Option 1: Via Alembic (Recommended)**
```bash
# Run migrations on deployment
docker compose exec backend alembic upgrade head

# Check current version
docker compose exec backend alembic current

# Rollback if needed
docker compose exec backend alembic downgrade -1
```

**Option 2: Via Supabase MCP (Hotfixes)**
```python
# Apply urgent fix without deployment
mcp_supabase_apply_migration(
    project_id="production-project-id",
    name="hotfix_add_index",
    query="CREATE INDEX CONCURRENTLY idx_extractions_status ON extractions(status);"
)

# Verify
mcp_supabase_get_advisors(
    project_id="production-project-id",
    type="performance"
)
```

### Backups (Managed by Supabase)

**Supabase Automatic Backups:**
- ✅ **Free Tier**: Daily backups (7-day retention)
- ✅ **Pro Tier**: Daily backups (30-day retention)
- ✅ **Team/Enterprise**: Configurable retention + PITR

**Additional Backup Strategy:**
```bash
# Manual backup via pg_dump (if needed)
SUPABASE_DB_URL="postgresql://postgres:[PASSWORD]@db.wijzypbstiigssjuiuvh.supabase.co:5432/postgres"

pg_dump $SUPABASE_DB_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $SUPABASE_DB_URL < backup_20251023.sql
```

**Backup Verification:**
- Go to Supabase Dashboard → Database → Backups
- Test restore to staging environment monthly

### Database Monitoring via MCP

```python
# Check database health
mcp_supabase_get_project(id="wijzypbstiigssjuiuvh")

# View connection usage
mcp_supabase_get_advisors(
    project_id="wijzypbstiigssjuiuvh",
    type="performance"
)

# Check logs for issues
mcp_supabase_get_logs(
    project_id="wijzypbstiigssjuiuvh",
    service="postgres"
)

# Security audit
mcp_supabase_get_advisors(
    project_id="wijzypbstiigssjuiuvh",
    type="security"
)
```

## Monitoring

### Sentry Integration

Configure `SENTRY_DSN` for error tracking:
- Backend: FastAPI integration
- Environment tagging
- Release tracking

### Health Checks

Available endpoints:
- Backend: `GET /api/v1/utils/health-check`
- Database connectivity verified automatically

---

## Redis Configuration by Environment

### Local (Docker)
```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  command: redis-server --requirepass ${REDIS_PASSWORD}
  # Ephemeral - data lost on restart
```

### Staging/Production (Managed)

**Option 1: Upstash (Recommended)**
- Serverless Redis with persistence
- Pay-per-use pricing
- Global replication
- Dashboard: https://upstash.com

**Option 2: Redis Cloud**
- Managed Redis Enterprise
- High availability
- Automatic failover
- Dashboard: https://redis.com/cloud

**Option 3: AWS ElastiCache**
- Integrated with AWS infrastructure
- VPC isolation
- Multi-AZ replication

**Configuration:**
```env
# Managed Redis connection
REDIS_URL=redis://username:password@managed-redis.upstash.io:6379
REDIS_PASSWORD=<managed-password>
```

---

## Celery Worker Deployment

### Local (Docker Compose)
```yaml
# docker-compose.yml
celery-worker:
  image: backend:latest
  command: celery -A app.worker worker --loglevel=info --concurrency=4
  # 1 container, 4 processes
```

### Staging/Production

**Option 1: Docker Compose Scaling**
```bash
# Scale workers horizontally
docker compose up -d --scale celery-worker=8

# 8 containers × 4 processes = 32 workers
```

**Option 2: Separate Worker Containers**
```yaml
# docker-compose.prod.yml
celery-worker-extraction:
  command: celery -A app.worker worker --loglevel=info --concurrency=8 --queues=extraction
  
celery-worker-default:
  command: celery -A app.worker worker --loglevel=info --concurrency=4 --queues=default
```

**Monitoring**: Use Flower (Celery web UI)
```bash
# Add to docker-compose.yml
flower:
  image: mher/flower
  command: celery --broker=${CELERY_BROKER_URL} flower
  ports:
    - "5555:5555"
```

---

## Supabase Environment Strategy

### Multi-Project Setup (Recommended)

**Development** (Current):
- Project: wijzypbstiigssjuiuvh
- Tier: Free
- Region: ap-south-1
- Purpose: Local development, testing

**Staging** (Future):
- Project: Create new Supabase project
- Tier: Pro ($25/month)
- Region: Same as production
- Purpose: Pre-production testing, QA

**Production** (Future):
- Project: Create new Supabase project
- Tier: Pro or Team
- Region: ap-south-1 (or closest to users)
- Purpose: Live application

**Benefits of Separate Projects:**
- ✅ Complete isolation (no accidental prod data in dev)
- ✅ Independent scaling
- ✅ Different access policies
- ✅ Separate backups
- ✅ Can pause dev/staging when not in use

### Storage Buckets per Environment

**Same bucket names, different projects:**
```
Development:  wijzypbstiigssjuiuvh.supabase.co/storage/v1/object/worksheets/
Staging:      staging-ref.supabase.co/storage/v1/object/worksheets/
Production:   prod-ref.supabase.co/storage/v1/object/worksheets/
```

---

## CI/CD Pipeline

### GitHub Actions Workflow (Future)

**On Push to `develop` branch → Deploy to Staging:**
```yaml
1. Run tests (lint, unit, E2E)
2. Build Docker images (backend, frontend)
3. Push to Docker Hub/GHCR
4. Deploy to staging server
5. Run database migrations (Alembic)
6. Restart services with health check wait
7. Run smoke tests
8. Notify team (Slack/Discord)
```

**On Release Tag (v*) → Deploy to Production:**
```yaml
1. Run full test suite
2. Build production Docker images
3. Push to Docker Hub/GHCR
4. Create database backup via MCP
5. Deploy to production server
6. Run migrations (with backup ready)
7. Restart services with zero-downtime
8. Health check verification
9. Rollback on failure
10. Notify team
```

### Deployment Checklist

**Pre-Deployment:**
- [ ] All tests pass (backend + frontend + E2E)
- [ ] Database migrations reviewed
- [ ] Secrets rotated (if needed)
- [ ] Backup created
- [ ] Sentry release created
- [ ] Team notified

**During Deployment:**
- [ ] Apply migrations
- [ ] Deploy new containers
- [ ] Health checks pass
- [ ] Smoke tests pass

**Post-Deployment:**
- [ ] Monitor error rates (Sentry)
- [ ] Check performance metrics
- [ ] Verify Celery workers processing
- [ ] Monitor database connections
- [ ] Check storage usage

---

## Rollback Strategy

### If Deployment Fails

**Immediate Rollback:**
```bash
# 1. Stop new containers
docker compose down

# 2. Restart previous version
docker compose up -d --force-recreate

# 3. Rollback database if needed
docker compose exec backend alembic downgrade -1

# 4. Investigate
docker compose logs backend --tail=100
docker compose logs celery-worker --tail=100
```

**Using Supabase MCP for Emergency Fixes:**
```python
# Quick schema fix without redeployment
mcp_supabase_apply_migration(
    project_id="prod-project-id",
    name="hotfix_critical_issue",
    query="ALTER TABLE extractions ADD COLUMN IF NOT EXISTS status_backup VARCHAR(50);"
)
```

---

## Security Checklist

### Before Staging/Production Deployment

**Secrets & Authentication:**
- [ ] All secrets changed from development defaults
- [ ] `SECRET_KEY` is new and ≥32 characters
- [ ] `FIRST_SUPERUSER_PASSWORD` is strong (≥16 chars)
- [ ] `REDIS_PASSWORD` is unique per environment
- [ ] Database password is strong and rotated
- [ ] Supabase `SERVICE_KEY` never exposed to frontend
- [ ] Different Supabase projects for dev/staging/prod

**Infrastructure:**
- [ ] HTTPS configured with valid certificates (Traefik + Let's Encrypt)
- [ ] CORS restricted to known origins only
- [ ] Firewall rules configured (only ports 80, 443 exposed)
- [ ] Redis password authentication enabled
- [ ] Supabase RLS policies enabled (for multi-tenancy)

**Monitoring:**
- [ ] Sentry DSN configured for error tracking
- [ ] Sentry releases tagged with version
- [ ] Database backups verified (Supabase dashboard)
- [ ] Health check endpoints working
- [ ] Log aggregation configured (future)

**Database:**
- [ ] Supabase Pro tier (for production)
- [ ] Connection pooling optimized
- [ ] Indexes added for frequent queries
- [ ] RLS policies tested
- [ ] Backup retention configured (30+ days)

**Storage:**
- [ ] Supabase Storage buckets created
- [ ] Bucket policies configured (private)
- [ ] File size limits enforced
- [ ] Signed URL expiry appropriate (7 days)

**Celery:**
- [ ] Worker concurrency appropriate for load
- [ ] Task time limits configured
- [ ] Dead letter queue configured (future)
- [ ] Flower monitoring UI (optional)

**Application:**
- [ ] All environment variables validated
- [ ] Rate limiting configured (future)
- [ ] File upload validation (size, type)
- [ ] Error handling comprehensive
- [ ] Logging levels appropriate (INFO in prod, DEBUG in dev)

---

## Environment Verification Commands

### Check All Services

```bash
# Services running
docker compose ps

# Backend health
curl https://api.curriculumextractor.com/api/v1/utils/health-check

# Frontend accessible
curl https://dashboard.curriculumextractor.com

# Celery worker stats
docker compose exec celery-worker celery -A app.worker inspect stats

# Redis connection
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} PING
```

### Check Supabase via MCP

```python
# Project status
mcp_supabase_get_project(id="production-project-id")

# Database health
mcp_supabase_get_logs(project_id="production-project-id", service="postgres")

# Security audit
mcp_supabase_get_advisors(project_id="production-project-id", type="security")

# Performance check
mcp_supabase_get_advisors(project_id="production-project-id", type="performance")
```

---

## Monitoring & Observability

### Application Monitoring

**Sentry** (Error Tracking):
- Backend: Automatic exception capture
- Frontend: JavaScript error tracking
- Release tracking: Tag with git sha/version
- Alerts: Email/Slack on critical errors

**Celery Monitoring**:
- Flower web UI: http://localhost:5555 (development)
- Worker stats via API: `/api/v1/tasks/inspect/stats`
- Redis queue depth monitoring

**Supabase Monitoring**:
- Dashboard metrics (CPU, memory, connections)
- Query performance insights
- Storage usage tracking
- API usage analytics

### Log Aggregation (Future)

**Options:**
- Grafana Loki (self-hosted)
- Datadog (SaaS)
- New Relic (SaaS)

**Docker logging:**
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Performance Optimization

### Database (Supabase)

**Connection Pooling:**
- Session Mode: 10 base + 20 overflow = 30 max
- Monitor via Supabase dashboard
- Upgrade tier if hitting limits

**Indexes:**
```sql
-- Add indexes for frequent queries
CREATE INDEX CONCURRENTLY idx_extractions_user_status 
ON extractions(user_id, status);

CREATE INDEX CONCURRENTLY idx_questions_tags 
ON questions USING GIN (curriculum_tags);
```

**Query Optimization:**
- Use `SELECT` with specific columns
- Implement pagination (skip/limit)
- Add database-level caching (future)

### Celery Workers

**Scaling:**
- Monitor queue depth
- Scale workers based on pending tasks
- Use separate queues for different task types
- Set appropriate concurrency per worker

**Task Optimization:**
- Set realistic time limits
- Implement checkpointing for long tasks
- Use chunks for batch operations
- Monitor task execution times

### Frontend

**Build Optimization:**
- Code splitting (TanStack Router lazy loading)
- Image optimization before upload
- Vite build minification
- CDN for static assets (production)

---

For detailed deployment steps, see [../../deployment.md](../../deployment.md)
