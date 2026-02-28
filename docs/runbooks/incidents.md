---
title: "Incident Response Runbook"
doc-type: how-to
status: published
id: "RB-0001"
service: "Full Stack FastAPI Project"
severity: "P1-P4"
owner: "DevOps Team"
last-reviewed: 2026-02-26
estimated-duration: "15-60 minutes"
last-updated: 2026-02-28
updated-by: "infra docs writer"
related-code:
  - compose.yml
  - backend/app/core/config.py
  - backend/app/api/utils.py
related-docs:
  - docs/deployment/environments.md
  - docs/getting-started/setup.md
tags: [runbook, operations, incidents, production]
---

# Incident Response Runbook

## Overview

This runbook guides response to production incidents. Use the severity table to assess and act immediately.

## Severity Assessment

Before starting any procedure, classify the incident:

| Severity | Definition | Examples | Response Time | Notify |
|----------|-----------|----------|---|--|
| **P1 - Critical** | Service completely down, data loss, security breach | API returns 500 for all requests, database unreachable, all users affected | **Immediate** | On-call engineer + Manager + Slack #incidents |
| **P2 - High** | Major functionality broken, significant impact | Login broken, payments failing, 50%+ features unavailable | **< 1 hour** | On-call engineer + Slack #incidents |
| **P3 - Medium** | Minor features degraded, workaround exists | Slow API responses, one feature broken, non-critical issue | **< 4 hours** | Slack #incidents |
| **P4 - Low** | Cosmetic issue, minimal impact | Typo in UI, minor styling issue, documentation needs update | **Next business day** | GitHub issue |

**If unsure of severity, escalate to P2.**

---

## P1 Incident Response (Critical)

### 1. Alert & Escalate (< 5 minutes)

```
IMMEDIATE ACTIONS - No delay:

1. Post to #incidents Slack channel
   "P1 INCIDENT: [Service] - [Brief Description]"

2. Call on-call manager/CTO

3. Start incident bridge (Google Meet/Zoom)
   Post link in #incidents

4. Assign incident commander (most senior available)

5. Document:
   - Incident start time (now)
   - What's down / affected users
   - Initial suspect (if known)
```

### 2. Assess Severity (1-2 minutes)

Confirm it's actually P1 by checking:

```bash
# Is backend down?
curl -f https://api.example.com/api/v1/utils/health-check/
# Expected: 200 OK with response
# If: timeout, 500, or no response = MAJOR issue

# Is frontend down?
curl -f https://dashboard.example.com
# Expected: 200 OK with HTML
# If: timeout, 502, or no response = MAJOR issue

# Database accessible?
# SSH to production server:
ssh root@example.com
docker compose ps | grep db
# Should show "healthy"
```

**Expected output:**
```
HEALTHY:
HTTP/1.1 200 OK
<Response includes {"status": "ok"}>

DEGRADED/DOWN:
Connection timeout
HTTP/1.1 500 Internal Server Error
HTTP/1.1 502 Bad Gateway
```

**If confirmed down:** Go to step 3 (Investigate)
**If false alarm:** Post resolution to #incidents, close incident

### 3. Investigate Root Cause (5-10 minutes)

SSH to production server:

```bash
ssh root@example.com
cd /root/code/app

# Check service health
docker compose ps
# Look for "unhealthy" or "Exited" services

# Check recent deployments
git log --oneline -5
# Look for recent commits that correlate with incident time

# Check backend logs
docker compose logs backend | tail -100
# Look for ERROR, traceback, database connection errors

# Check database logs
docker compose logs db | tail -50
# Look for connection errors, disk full, etc.

# Check Sentry for errors
# Open: https://sentry.io/organizations/[org]/issues/
# Filter by timestamp of incident
```

**Common Issues & Diagnostics:**

| Symptom | Likely Cause | Check Command |
|---------|-------------|---|
| Backend returns 500 on all requests | Code error, database unreachable | `docker compose logs backend \| grep ERROR` |
| Database unreachable | DB container crashed, disk full, password wrong | `docker compose ps \| grep db` and `docker system df` |
| Frontend 502 Bad Gateway | Backend unhealthy | `docker compose logs backend \| tail -20` |
| High memory usage | Memory leak, too many requests | `docker stats` |
| High disk usage | Log files full, database bloated | `docker system df` and `df -h` |

### 4. Immediate Mitigation (5-15 minutes)

**Option A: Restart Services** (simplest, ~2 min)

```bash
# If a service crashed
docker compose restart backend
# Wait for health check to pass (30-60 seconds)

# If database unhealthy
docker compose restart db
# Wait longer for DB to recover (1-2 minutes)

# If multiple services down
docker compose down
docker compose up -d
# Wait 2-3 minutes for full startup
```

**Verify recovery:**

```bash
# Check health
curl -f https://api.example.com/api/v1/utils/health-check/

# Check logs for errors
docker compose logs backend | tail -20
docker compose logs db | tail -20
```

**Option B: Rollback Deployment** (if recent deploy caused issue)

Two rollback paths are available. Use Option B-1 (GHCR image rollback) whenever possible — it skips a full rebuild and is significantly faster.

**Option B-1 (preferred — GHCR image rollback, no rebuild):**

```bash
# Find the last known-good commit SHA from GitHub Actions run history
# GitHub → Actions → Deploy to Staging → identify the last successful run SHA

# Staging rollback: re-tag a previous SHA as staging
docker pull ghcr.io/{repo}/backend:{previous-sha}
docker tag ghcr.io/{repo}/backend:{previous-sha} ghcr.io/{repo}/backend:staging
docker push ghcr.io/{repo}/backend:staging
# Then trigger your platform's deploy for the staging tag

# Production rollback: re-tag a previous version as latest
docker pull ghcr.io/{repo}/backend:v1.2.2
docker tag ghcr.io/{repo}/backend:v1.2.2 ghcr.io/{repo}/backend:latest
docker push ghcr.io/{repo}/backend:latest
# Or create a new GitHub Release pointing to v1.2.2 to trigger the production deploy workflow
```

No code change is required. The previously validated image is redeployed immediately without waiting for a rebuild.

**Option B-2 (git revert — triggers full rebuild):**

```bash
# Check when incident started
# If <10 minutes after deployment, likely caused by it

# Revert last commit
git revert HEAD
git push  # This triggers automatic redeployment (full image rebuild)

# Wait 3-5 minutes for image rebuild and redeploy
# Verify: curl https://api.example.com/api/v1/utils/health-check/
```

Use Option B-2 when the problematic image has already been removed from GHCR or when the rollback target predates GHCR image history.

**Option C: Scale Resources** (if resource exhaustion)

```bash
# Check resource usage
docker stats

# If out of disk
docker system prune -a  # Remove unused images (CAUTION)
du -sh /root/code/app/*  # Check what's taking space

# If out of memory
# Increase Docker resource limits or scale to larger machine
```

**After mitigation:**

- [ ] Service returned to healthy status
- [ ] Health checks passing
- [ ] Users reporting service restored
- [ ] Logs show no errors

### 5. Stabilize (ongoing)

Keep incident commander in bridge. Monitor:

```bash
# Continuous monitoring
watch -n 5 'docker compose ps && docker stats'

# Check logs for recurring errors
docker compose logs -f backend | grep ERROR

# Monitor Sentry for new error patterns
```

**Exit criteria:**
- Service healthy for 10+ minutes
- No error spikes in logs
- No user reports of issues
- All services green

### 6. Post-Incident (after stabilization)

```
In Slack #incidents channel:

INCIDENT RESOLVED
- Time to detect: Xm
- Time to resolve: Ym
- Root cause: [brief summary]
- Actions taken: [list mitigations]

Post-mortem scheduled for [date] at [time]
```

Create GitHub issue: `Post-mortem: [Incident Date] - [Title]`

---

## P2 Incident Response (High)

### 1. Alert (< 5 minutes)

```bash
# Post to #incidents
"P2 INCIDENT: [Service] - [Feature broken] - [Impact]"

# Assign on-call engineer
# Start investigating immediately
```

### 2. Investigate (5-10 minutes)

Follow same investigation steps as P1 (step 3 above).

### 3. Mitigate (5-20 minutes)

Execute same mitigation steps as P1 (step 4 above).

**Additional steps for high-severity bugs:**

```bash
# If code bug (not infrastructure)
cd /root/code/app

# Check recent code changes
git log --oneline -10 --since="1 hour ago"

# If specific PR caused it
git revert <commit-hash>
git push  # Auto-redeploys
```

### 4. Verify Fix

```bash
# Test the broken feature works
# E.g., if login broken: test login flow in browser

# Check logs
docker compose logs backend | grep ERROR

# Monitor for 10 minutes
# No new errors, no user reports = resolved
```

---

## P3/P4 Incident Response (Medium/Low)

For P3: Create GitHub issue with reproduction steps. Fix within 24 hours.

For P4: Create GitHub issue. Fix in next sprint.

---

## Common Incident Scenarios

### Scenario 1: Backend Returns 500 Errors

```bash
ssh root@example.com && cd /root/code/app

# Check what's happening
docker compose logs backend | tail -50 | grep -A 5 ERROR

# Common causes and fixes

# 1. Database unreachable
docker compose logs db | tail -20
docker compose restart db
# Wait 2 minutes

# 2. Environment variable missing or wrong
docker compose logs backend | grep "ERROR.*config\|ERROR.*settings"
# Review .env or GitHub Secrets
# Check: git log shows recent env var changes?

# 3. Out of memory
docker stats
# If backend using >90% memory: restart
docker compose restart backend

# 4. Recent code deploy broke something
git log --oneline -5
# If recent change correlates with incident time:
git revert <commit-hash> && git push
```

### Scenario 2: Database Unreachable

```bash
ssh root@example.com && cd /root/code/app

# Check database container
docker compose ps | grep db
# If "Exited" or "unhealthy"

# Check disk space (databases need space)
df -h
# If /var/lib/ or / is >90% full: need to clean up

# Check database logs
docker compose logs db | tail -50

# Try restart
docker compose restart db

# Wait 2 minutes, verify
docker compose logs db | grep "ready to accept"
```

### Scenario 3: Frontend Not Loading

```bash
# Test backend is working
curl https://api.example.com/api/v1/utils/health-check/
# Should return 200

# Check frontend logs
ssh root@example.com && cd /root/code/app
docker compose logs frontend | tail -20

# If Nginx error, restart
docker compose restart frontend

# Check Traefik routing
docker compose logs proxy | grep "dashboard.example.com"
```

### Scenario 4: Email Not Sending (Staging/Prod)

```bash
ssh root@example.com && cd /root/code/app

# Check SMTP config
docker compose logs backend | grep -i smtp

# Verify secrets are set
# Can't see values, but check they're referenced:
docker compose config | grep SMTP_HOST

# Test SMTP connectivity
# Requires telnet or similar (not available in Docker)
# Instead: trigger email from admin panel
# Check backend logs for SMTP errors

# If still broken: escalate to email provider
```

### Scenario 5: High Memory or CPU Usage

```bash
ssh root@example.com && cd /root/code/app

# See what's using resources
docker stats

# If backend memory spike
docker compose logs backend | tail -100 | grep -i memory

# If requests causing memory leak
# Restart affected service
docker compose restart backend

# Long-term fix
# Investigate code for memory leak (check Sentry)
```

---

## Rollback Procedure (Complete)

Use if deployment introduced a critical bug. Two options are available — prefer Option A when a previous GHCR image exists (faster, no rebuild).

### Option A (preferred — GHCR image rollback, no rebuild)

Re-tag a previously built and validated image and redeploy without triggering a full image rebuild:

```bash
# Find the last known-good commit SHA from GitHub Actions run history
# GitHub → Actions → Deploy to Staging → last successful run

# Staging rollback: re-tag a previous SHA as staging
docker pull ghcr.io/{repo}/backend:{previous-sha}
docker tag ghcr.io/{repo}/backend:{previous-sha} ghcr.io/{repo}/backend:staging
docker push ghcr.io/{repo}/backend:staging
# Then trigger your platform's deploy for the staging tag

# Production rollback: re-tag a previous version as latest
docker pull ghcr.io/{repo}/backend:v1.2.2
docker tag ghcr.io/{repo}/backend:v1.2.2 ghcr.io/{repo}/backend:latest
docker push ghcr.io/{repo}/backend:latest
# Or create a new GitHub Release pointing to v1.2.2 to trigger the production deploy workflow
```

**Expected outcome:** Redeployment completes in 1-2 minutes (no rebuild). Verify with health check immediately after deploy completes.

### Option B (git revert — triggers full rebuild)

Use when the rollback target image is no longer available in GHCR, or when you need to roll back a code change that was never built:

```bash
ssh root@example.com
cd /root/code/app

# See recent commits
git log --oneline -10

# Revert the problematic commit
git revert <commit-hash>

# Push triggers automatic redeployment (full image rebuild)
git push

# Wait 3-5 minutes for image rebuild and deploy
# Monitor
docker compose logs backend | tail -20

# Verify service healthy
curl https://api.example.com/api/v1/utils/health-check/
```

**Don't use `git reset --hard`** — it removes commit history. Use `git revert` instead.

---

## Communication During Incident

### Status Updates

Post to #incidents every 10 minutes during P1, every 30 minutes during P2:

```
[11:30 AM] INVESTIGATING
- Confirmed backend unhealthy
- Checking logs for error pattern
- ETA 20 minutes

[11:40 AM] ROOT CAUSE IDENTIFIED
- Recent deploy caused memory leak
- Reverting commit...

[11:45 AM] MITIGATION IN PROGRESS
- Rollback in progress
- Redeployment underway
- Expected resolution: 5 minutes

[11:50 AM] RESOLVED
- Service restored at 11:47 AM
- All systems healthy
- Post-mortem scheduled for Thursday
```

### Notify Customers (P1 only)

```
STATUS PAGE UPDATE (if you have one):

"We are experiencing issues with dashboard.example.com.
Our team is actively investigating. More updates in 15 minutes."

After resolution:

"Issue resolved at 11:47 AM. Service fully restored.
Apologies for the disruption."
```

---

## Post-Incident Process

### Immediately After Resolution

1. Post to #incidents: incident resolved, duration, time to mitigation
2. Create GitHub issue labeled `incident` with title: `Post-mortem: [Date] - [Title]`
3. Schedule post-mortem meeting (within 48 hours for P1, 1 week for P2)

### Post-Mortem Meeting

Attend: incident commander, on-call engineer, relevant developers, manager

Discuss:

1. **Timeline** - What happened, when, duration
2. **Root Cause** - Why it happened
3. **Detection** - How we found it, time to detection
4. **Resolution** - How we fixed it
5. **Actions** - What we'll do to prevent recurrence
   - Code fixes
   - Monitoring improvements
   - Documentation updates
   - Testing additions

### Update This Runbook

If incident revealed gap in this runbook:

```bash
# Edit this file
vim docs/runbooks/incidents.md

# Add new scenario or clarify steps
# Commit and push
git add docs/runbooks/incidents.md
git commit -m "docs: update incidents runbook based on [incident date] post-mortem"
git push
```

---

## Prevention

### Monitoring

Setup/verify these are configured:

- [ ] **Health checks** - Backend responds to `/api/v1/utils/health-check/` every 10 seconds
- [ ] **Sentry** - Error tracking initialized in lifespan startup (only if `SENTRY_DSN` is set), flushed gracefully on shutdown
- [ ] **Uptime monitoring** - External service checks https://api.example.com every 5 minutes
- [ ] **Resource monitoring** - Server monitoring memory, disk, CPU usage

**Sentry Integration Notes:**
- Sentry is conditionally initialized in the application lifespan (startup phase) if `SENTRY_DSN` environment variable is configured
- On graceful shutdown, `sentry_sdk.flush(timeout=2.0)` ensures pending error events are sent before the HTTP client closes
- If `SENTRY_DSN` is not set, Sentry remains disabled (no overhead)

### Testing

Before deploying to production:

- [ ] Run full test suite: `docker compose -f scripts/test.sh`
- [ ] Test in staging environment
- [ ] Load test critical paths
- [ ] Chaos test (kill containers, restart, see if system recovers)

### Infrastructure as Code

All configurations should be:

- [ ] In git (`compose.yml`, Traefik config, etc.)
- [ ] Documented in `.env` file
- [ ] Backed up daily (database)
- [ ] Have runbooks for recovery

---

## Useful Commands Reference

```bash
# Basic status
docker compose ps
docker compose logs backend | tail -50

# Service restart
docker compose restart <service>
docker compose restart backend

# Full restart
docker compose down && docker compose up -d

# Check resource usage
docker stats
docker system df

# Database access
docker compose exec db psql -U postgres -d app -c "SELECT COUNT(*) FROM users;"

# View deployment history
git log --oneline -20

# Rollback Option A (preferred — GHCR image, no rebuild)
docker pull ghcr.io/{repo}/backend:{previous-sha}
docker tag ghcr.io/{repo}/backend:{previous-sha} ghcr.io/{repo}/backend:staging
docker push ghcr.io/{repo}/backend:staging

# Rollback Option B (git revert — triggers full rebuild)
git revert <commit-hash>
git push

# Clean up disk
docker system prune -a
docker volume prune
```

---

## Related Documentation

- [Deployment Environments](../deployment/environments.md)
- [Development Workflow](../getting-started/development.md)
- [Setup Guide](../getting-started/setup.md)
