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

### Database Tables Missing After Migration (P1 - Critical)

**Date**: 2025-10-30
**Severity**: P1 - Critical (Data Loss Risk)
**Status**: Resolved with preventive measures implemented

**Symptoms**:
- All application tables (user, ingestions) missing from database
- Only `alembic_version` table exists
- Alembic reports latest migration version but schema doesn't match
- Application fails with "relation does not exist" errors

**Root Causes**:
1. **Buggy Autogenerate Migration**: Alembic's autogenerate created a migration file with `CREATE TABLE` operations instead of `ALTER TABLE ADD COLUMN` operations for existing tables
2. **Manual Version Stamping**: Someone ran `alembic stamp <revision>` instead of `alembic upgrade head`, updating the version number without applying the migration
3. **Missing Safety Checks**: No validation in env.py to prevent CREATE TABLE on existing tables

**Diagnosis:**
```bash
# Check current database state
docker compose exec backend uv run alembic current

# List tables in database (via Supabase MCP or direct SQL)
mcp_supabase_list_tables(project_id="wijzypbstiigssjuiuvh", schemas=["public"])

# Check alembic version table directly
docker compose exec backend psql $DATABASE_URL -c "SELECT version_num FROM alembic_version;"

# Inspect migration files for dangerous operations
grep -r "op.create_table" backend/app/alembic/versions/

# Compare database schema with models
docker compose exec backend uv run alembic check
```

**Resolution Steps**:

1. **Immediate Recovery** (if tables are missing):
```bash
# Reset alembic version to last known good state
docker compose exec backend psql $DATABASE_URL -c "UPDATE alembic_version SET version_num = '<previous_revision>';"

# Apply migrations properly
docker compose exec backend uv run alembic upgrade head

# Verify tables created
docker compose exec backend uv run alembic current
docker compose exec backend psql $DATABASE_URL -c "\dt"
```

2. **Enable RLS** (if using Supabase):
```sql
-- Enable RLS on all tables
ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestions ENABLE ROW LEVEL SECURITY;

-- Create service role policy
CREATE POLICY "Service role has full access to ingestions" ON ingestions
  FOR ALL USING (true) WITH CHECK (true);

-- Verify with security advisors
mcp_supabase_get_advisors(project_id="wijzypbstiigssjuiuvh", type="security")
```

3. **Delete Buggy Migration**:
```bash
# Identify the bad migration (look for CREATE TABLE on existing tables)
# Delete it BEFORE creating a replacement
rm backend/app/alembic/versions/<bad_revision>_*.py
```

4. **Create Proper Replacement Migration**:
```bash
# Create new migration manually (not autogenerate)
docker compose exec backend uv run alembic revision -m "add_ocr_fields_to_ingestions"

# Edit the migration to use ALTER TABLE operations:
# ✅ CORRECT:
# op.add_column('ingestions', sa.Column('ocr_provider', ...))
#
# ❌ WRONG:
# op.create_table('ingestions', ...)
```

5. **Mark Migration as Applied** (if schema changes already exist):
```bash
# If you manually applied the schema changes, stamp the migration
docker compose exec backend uv run alembic stamp <new_revision>

# Verify
docker compose exec backend uv run alembic current
```

**Preventive Measures Implemented**:

1. **Enhanced env.py with Safety Hooks** (`backend/app/alembic/env.py`):
   - Added `prevent_table_recreation()` rewriter to catch CREATE TABLE on existing tables
   - Added `include_object()` filter to prevent autogenerate false positives
   - Added `process_revision_directives()` to prevent empty migrations
   - Added `compare_type=True` and `compare_server_default=True` for accuracy

2. **Pre-commit Hooks** (`.pre-commit-config.yaml`):
   - `alembic-check`: Runs `alembic check` to detect migration drift
   - `alembic-migration-safety`: Validates migration files for dangerous operations

3. **Migration Safety Checker** (`backend/scripts/check_migration_safety.py`):
   - Detects CREATE TABLE operations (requires confirmation comment)
   - Detects DROP TABLE/COLUMN operations (requires confirmation comment)
   - Ensures migrations have both upgrade() and downgrade() functions
   - Prevents empty migrations

**Testing Preventive Measures**:
```bash
# Install pre-commit hooks
cd /path/to/CurriculumExtractor
pre-commit install

# Test migration safety checker
python backend/scripts/check_migration_safety.py

# Test alembic check
cd backend && uv run alembic check

# Try creating a migration (should now prevent dangerous operations)
cd backend && uv run alembic revision --autogenerate -m "test"
```

**Warning Signs to Watch For**:
- ❌ Alembic reports version but tables missing
- ❌ Migration files contain `op.create_table()` for existing tables
- ❌ Someone used `alembic stamp` instead of `alembic upgrade`
- ❌ Security advisors show missing RLS policies after migration
- ❌ `alembic check` reports drift

**When to Escalate**:
- Immediately escalate if data loss suspected
- Contact database admin if unable to recover tables
- Notify tech lead if migrations are corrupted

**Lessons Learned**:
1. Never use `alembic stamp` unless you know exactly what you're doing
2. Always review autogenerated migrations before applying
3. Use `alembic check` regularly to detect drift
4. Enable RLS immediately after table creation (Supabase)
5. Keep migration files in version control - they are source of truth
6. Use Alembic for team development, Supabase MCP only for debugging

**Related Documentation**:
- `@docs/getting-started/development.md#database-changes` - Migration workflows
- `@CLAUDE.md#keeping-alembic-synchronized` - Sync guidelines
- `@CLAUDE.md#supabase-mcp-commands` - MCP vs Alembic usage

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
