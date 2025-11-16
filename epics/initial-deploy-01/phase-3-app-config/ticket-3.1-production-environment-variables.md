# Ticket 3.1: Environment Variables for Production

## Overview
Configure production-ready environment variables for your FastAPI application. This involves updating default values to secure credentials, setting proper domain names, and configuring CORS settings.

## Prerequisites
- Access to your home server
- Domain name configured (a-seashell-company.com)
- Code repository cloned to server

## Step 1: Locate and Backup Current .env File

### Navigate to Project
```bash
cd ~/full-stack-fastapi-template
```

### Backup Current .env
```bash
# Create backup
cp .env .env.backup

# View current settings
cat .env
```

## Step 2: Generate Secure Secrets

### Generate SECRET_KEY
```bash
# Generate a secure random secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use openssl
openssl rand -base64 32
```

Save this value - you'll need it for the .env file.

### Generate Strong Passwords
```bash
# Generate password for database
openssl rand -base64 24

# Generate password for admin user
openssl rand -base64 16
```

Save these values as well.

## Step 3: Update .env File

### Edit .env File
```bash
nano .env
```

Update the following variables:

```bash
# Domain Configuration
DOMAIN=a-seashell-company.com
FRONTEND_HOST=https://a-seashell-company.com
ENVIRONMENT=production

# Project Info
PROJECT_NAME="A Seashell Company"
STACK_NAME=seashell-company-prod

# Backend Security
BACKEND_CORS_ORIGINS="https://a-seashell-company.com,https://www.a-seashell-company.com,https://api.a-seashell-company.com"
SECRET_KEY=your-generated-secret-key-from-step-2
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days default, adjust as needed

# Admin User
FIRST_SUPERUSER=admin@a-seashell-company.com  # Change to your actual email
FIRST_SUPERUSER_PASSWORD=your-secure-admin-password

# Database (using Docker PostgreSQL)
POSTGRES_SERVER=db  # Docker service name
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-db-password  # CHANGE THIS!

# Email Configuration (leave blank for now, configure in Ticket 3.3)
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=noreply@a-seashell-company.com
SMTP_TLS=True
SMTP_SSL=False
SMTP_PORT=587

# Sentry (Optional - for error tracking)
SENTRY_DSN=

# Docker Images
DOCKER_IMAGE_BACKEND=backend
DOCKER_IMAGE_FRONTEND=frontend
```

### Important Security Notes:

**MUST CHANGE:**
- `SECRET_KEY` - Use generated value from Step 2
- `POSTGRES_PASSWORD` - Use generated value from Step 2
- `FIRST_SUPERUSER_PASSWORD` - Use generated value from Step 2
- `FIRST_SUPERUSER` - Use your actual email

**SHOULD UPDATE:**
- `PROJECT_NAME` - Your actual project name
- `STACK_NAME` - Unique name for your stack
- `BACKEND_CORS_ORIGINS` - Your actual domains
- `EMAILS_FROM_EMAIL` - Your actual sender email

**CAN LEAVE AS-IS:**
- `POSTGRES_SERVER=db` (Docker service name)
- `POSTGRES_USER=postgres` (default is fine)
- `POSTGRES_DB=app` (default is fine)
- `SMTP_*` (configure later in Ticket 3.3)

## Step 4: Verify Environment Variables

### Check for Sensitive Data
```bash
# Make sure .env is not committed to git
cat .gitignore | grep .env

# Should show ".env" is ignored
```

### Validate .env Format
```bash
# Check for syntax errors (no output = good)
grep -E '^\s*[^#].*=.*\s+' .env

# Check for common mistakes
grep -E 'changethis|example\.com|localhost:5173' .env
```

If the second command shows any matches, you still have default values that need updating.

## Step 5: Update Frontend Environment Variables

The frontend needs to know the API URL in production.

### Check Current Frontend Build Args
```bash
# View docker-compose override
grep -A 5 "VITE_API_URL" docker-compose.override.yml
```

### Create Production Frontend Config

For production, the frontend should use the production API URL. You have two options:

**Option A: Update docker-compose.override.yml**
```bash
nano docker-compose.override.yml
```

Find the frontend service and update:
```yaml
  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_URL=https://api.a-seashell-company.com
        - NODE_ENV=production
```

**Option B: Create docker-compose.production.yml** (Recommended)
```bash
nano docker-compose.production.yml
```

Add:
```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_URL=https://api.a-seashell-company.com
        - NODE_ENV=production
    restart: unless-stopped

  backend:
    restart: unless-stopped

  db:
    restart: unless-stopped
```

## Step 6: Set Proper File Permissions

```bash
# Secure .env file
chmod 600 .env

# Verify permissions
ls -la .env

# Should show: -rw------- (only owner can read/write)
```

## Step 7: Verify Configuration

### Check All Environment Variables
```bash
# View all variables (be careful - contains secrets!)
cat .env

# Check specific critical variables
grep -E '^(SECRET_KEY|POSTGRES_PASSWORD|FIRST_SUPERUSER|DOMAIN|FRONTEND_HOST)=' .env
```

### Verify No Defaults Remain
```bash
# This should return NOTHING if all defaults are changed
grep -E 'changethis|example\.com(?!pany)|localhost:5173' .env
```

### Test Environment Loading
```bash
# Source the env file to test
set -a
source .env
set +a

# Verify variables are loaded
echo $DOMAIN
echo $FRONTEND_HOST
echo $ENVIRONMENT
```

## Step 8: Document Your Configuration

### Create Secure Notes
Create a password manager entry or secure note with:
- SECRET_KEY value
- POSTGRES_PASSWORD value
- FIRST_SUPERUSER and password
- Any other critical credentials

**DO NOT** store these in plaintext files or commit them to git.

### Create Environment Template (Optional)
```bash
# Create example env without secrets
cp .env .env.example

# Edit to remove all secrets
nano .env.example
```

Replace all secret values with placeholders:
```bash
SECRET_KEY=your-secret-key-here
POSTGRES_PASSWORD=your-db-password-here
FIRST_SUPERUSER_PASSWORD=your-admin-password-here
```

This can be committed to git as a template.

## Configuration Reference

### Critical Variables Explained

**DOMAIN**
- Your root domain name
- Used by Traefik (though not needed with Cloudflare Tunnel)
- Set to: `a-seashell-company.com`

**FRONTEND_HOST**
- Full URL where frontend is accessible
- Used in password reset emails
- Set to: `https://a-seashell-company.com`

**ENVIRONMENT**
- Controls various behaviors (logging, validation, etc.)
- Options: `local`, `staging`, `production`
- Set to: `production`

**BACKEND_CORS_ORIGINS**
- Comma-separated list of allowed frontend origins
- Must include all domains that will access the API
- Include: main domain, www subdomain, api subdomain

**SECRET_KEY**
- Used for JWT token signing
- MUST be secure random string
- Never commit to git
- Never reuse across environments

**POSTGRES_PASSWORD**
- Database password
- Used by both backend and db container
- MUST be changed from default

**FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD**
- Initial admin account
- Created on first run
- Can create other users from this account

## Verification Checklist

- [ ] .env file backed up
- [ ] SECRET_KEY generated and set
- [ ] POSTGRES_PASSWORD changed from default
- [ ] FIRST_SUPERUSER_PASSWORD changed from default
- [ ] DOMAIN set to a-seashell-company.com
- [ ] FRONTEND_HOST set to https://a-seashell-company.com
- [ ] ENVIRONMENT set to production
- [ ] BACKEND_CORS_ORIGINS includes all your domains
- [ ] .env file permissions set to 600
- [ ] No "changethis" or default values remain
- [ ] Sensitive values stored in password manager
- [ ] .env confirmed in .gitignore

## Testing

### Test Environment Loading
```bash
# Start containers with new config (don't worry about errors yet)
docker compose down
docker compose up -d

# Check if backend loaded config correctly
docker compose logs backend | grep -i "environment"

# Check if any config warnings
docker compose logs backend | grep -i "warning"
```

### Common Issues

**"changethis" Warning**
If you see warnings about "changethis", you missed updating a variable. Check:
```bash
grep changethis .env
```

**CORS Errors in Browser**
If frontend can't connect to backend, check BACKEND_CORS_ORIGINS includes your domain.

**Database Connection Errors**
Verify POSTGRES_PASSWORD matches between .env and what the db container expects.

## Security Best Practices

1. **Never commit .env to git** - Always in .gitignore
2. **Use strong secrets** - At least 32 characters
3. **Unique passwords** - Different for each service
4. **Rotate secrets** - Change periodically (every 90 days)
5. **Secure backups** - Encrypt .env backups
6. **Access control** - Only you should have access
7. **Password manager** - Store all secrets securely

## Next Steps

After completing this ticket:
1. Ticket 3.2: Database security (simplified since using bundled DB)
2. Ticket 3.3: Email service configuration
3. Phase 4: Deploy application with new config
4. Test all functionality with production settings

## Rollback Procedure

If something goes wrong:
```bash
# Restore backup
cp .env.backup .env

# Restart services
docker compose down
docker compose up -d
```

## Additional Resources

- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Secrets Management](https://docs.docker.com/engine/swarm/secrets/)
- [OWASP Configuration Guide](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)