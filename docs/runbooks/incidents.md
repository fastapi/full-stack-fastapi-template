# Incident Response Runbook

## Incident Classification

### Severity Levels

**P1 - Critical**
- Application completely down
- Data loss or corruption
- Security breach
- Response time: Immediate

**P2 - High**
- Major feature broken
- Performance degradation
- Intermittent errors
- Response time: < 1 hour

**P3 - Medium**
- Minor feature issues
- Non-critical bugs
- Response time: < 4 hours

**P4 - Low**
- Cosmetic issues
- Feature requests
- Response time: Next business day

## Common Incidents

### Application Not Starting

**Symptoms**: Docker containers fail to start or crash immediately

**Diagnosis:**
```bash
# Check container status
docker compose ps

# View logs
docker compose logs backend -f
docker compose logs frontend -f

# Check environment variables
docker compose exec backend env | grep -E "SECRET|POSTGRES|DOMAIN"
```

**Common Causes:**
1. Invalid environment variables
2. Database not accessible
3. Missing secrets
4. Port conflicts

**Resolution:**
```bash
# Verify .env file
cat .env

# Restart services
docker compose down
docker compose up -d

# Check database connectivity
docker compose exec backend python -c "from app.core.db import engine; engine.connect()"
```

### Database Connection Errors

**Symptoms**: Backend logs show "could not connect to server"

**Diagnosis:**
```bash
# Check PostgreSQL container
docker compose ps db

# Test connection
docker compose exec db psql -U postgres -d app
```

**Resolution:**
```bash
# Restart database
docker compose restart db

# Verify connection string in .env
grep POSTGRES .env

# Check migrations
docker compose exec backend alembic current
```

### Frontend 404 Errors

**Symptoms**: Frontend routes return 404 in production

**Common Cause**: Vite build configuration or routing issue

**Resolution:**
1. Verify Vite build output
2. Check TanStack Router configuration
3. Ensure proper deployment of `dist/` folder

### API 500 Errors

**Symptoms**: API endpoints returning 500 Internal Server Error

**Diagnosis:**
```bash
# Check backend logs
docker compose logs backend --tail=100 -f

# Check Sentry (if configured)
# View error details in Sentry dashboard
```

**Resolution:**
1. Identify error in logs
2. Check database state
3. Verify migrations applied
4. Rollback if recent deployment

### Authentication Failures

**Symptoms**: Users unable to login or "Unauthorized" errors

**Diagnosis:**
```bash
# Check SECRET_KEY is set
docker compose exec backend python -c "from app.core.config import settings; print(len(settings.SECRET_KEY))"

# Verify token generation
docker compose logs backend | grep -i "token"
```

**Resolution:**
- Verify `SECRET_KEY` not changed (breaks existing tokens)
- Check token expiry (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- Verify CORS settings

### Email Not Sending

**Symptoms**: Password reset emails not received

**Diagnosis:**
```bash
# Check SMTP settings
docker compose exec backend python -c "from app.core.config import settings; print(settings.emails_enabled)"
```

**Resolution:**
1. Verify SMTP credentials in `.env`
2. Test SMTP connection
3. Check email logs
4. Verify `EMAILS_FROM_EMAIL` set

## Escalation Path

1. **On-call engineer** attempts resolution
2. If unresolved in 30 minutes for P1, escalate to **senior engineer**
3. If data loss suspected, notify **tech lead**
4. For security incidents, immediately notify **security team**

## Post-Incident

After resolution:
1. Document incident details
2. Update this runbook if new issue
3. Create GitHub issue for preventive measures
4. Schedule postmortem for P1/P2 incidents

## Emergency Contacts

- **On-call rotation**: [Link to PagerDuty/schedule]
- **Tech lead**: [Contact info]
- **Database admin**: [Contact info]
- **Security team**: [Contact info]

## Useful Commands

```bash
# Full stack restart
docker compose down && docker compose up -d

# View all logs
docker compose logs -f

# Access backend shell
docker compose exec backend bash

# Access database
docker compose exec db psql -U postgres -d app

# Check database migrations
docker compose exec backend alembic current
docker compose exec backend alembic history

# Rollback migration
docker compose exec backend alembic downgrade -1

# Force rebuild
docker compose build --no-cache
docker compose up -d
```

## Monitoring

Check these when investigating:
- Application logs (Docker Compose logs)
- Sentry errors (if configured)
- Database logs
- Resource usage (CPU, memory, disk)

---

For operational procedures, see [procedures/](./procedures/)
