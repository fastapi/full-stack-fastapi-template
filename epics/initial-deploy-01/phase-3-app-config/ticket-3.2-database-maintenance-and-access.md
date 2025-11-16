# Ticket 3.2: Database Maintenance and Remote Access

## Overview
Configure database backups, verify migrations, and set up remote access to PostgreSQL via DBeaver from your laptop using Tailscale. Since you're using the bundled PostgreSQL container, the database is already set up - this ticket focuses on maintenance and access.

## Prerequisites
- PostgreSQL container running in Docker
- Tailscale installed on both server and laptop
- DBeaver installed on your laptop
- Database password updated in .env (from Ticket 3.1)

## Step 1: Verify Database is Running

### Check Database Container
```bash
# Check if database container is running
docker compose ps db

# Should show "healthy" status
```

### Test Database Connection from Server
```bash
# Connect to database from server
docker compose exec db psql -U postgres -d app

# You should get a PostgreSQL prompt
# Type \q to exit
```

### Verify Migrations Ran
```bash
# Check migration logs
docker compose logs prestart | grep -i "migration"

# Check tables exist
docker compose exec db psql -U postgres -d app -c "\dt"

# Should show tables: user, item, alembic_version, etc.
```

## Step 2: Configure Remote Access via Tailscale

### Find Server Tailscale IP
```bash
# On your server, get Tailscale IP
tailscale ip -4

# Save this IP - you'll use it in DBeaver
# Example: 100.x.x.x
```

### Verify PostgreSQL Port is Accessible
```bash
# Check if PostgreSQL port is exposed
docker compose ps db

# Should show: 0.0.0.0:5432->5432/tcp
```

If not exposed, update docker-compose.override.yml:
```yaml
  db:
    ports:
      - "5432:5432"  # Should already be there
```

### Test Connection from Laptop
From your laptop (connected to Tailscale):
```bash
# Install PostgreSQL client if needed
# Mac: brew install postgresql
# Linux: sudo apt install postgresql-client

# Test connection (replace 100.x.x.x with your server's Tailscale IP)
psql -h 100.x.x.x -U postgres -d app

# Enter the password from your .env file
# If successful, you'll get a PostgreSQL prompt
```

## Step 3: Configure DBeaver Connection

### Open DBeaver
1. Download DBeaver Community from https://dbeaver.io/download/ if not installed
2. Open DBeaver

### Create New PostgreSQL Connection

**Step-by-step:**

1. Click **Database** → **New Database Connection**
2. Select **PostgreSQL**
3. Click **Next**

**Connection Settings:**

```
Host: <your-server-tailscale-ip>  (e.g., 100.x.x.x)
Port: 5432
Database: app
Username: postgres
Password: <your-postgres-password-from-.env>
```

**Additional Settings:**

- Click **Test Connection** to verify
- If successful, click **Finish**
- Name the connection: "Seashell Company - Production DB"

### Configure SSH Tunnel (Alternative Method)

If direct connection doesn't work, use SSH tunnel:

1. In DBeaver connection settings, go to **SSH** tab
2. Check **Use SSH Tunnel**
3. Configure:
   ```
   Host: <your-server-tailscale-ip>
   Port: 22
   Username: <your-ssh-username>
   Authentication: Public Key or Password
   ```

### Security Best Practices

**Option A: Tailscale Only (Recommended)**
- Keep PostgreSQL port bound to 0.0.0.0:5432
- Only accessible via Tailscale network
- Most secure for home server

**Option B: Localhost Only**
If you don't want PostgreSQL accessible even via Tailscale:
```yaml
  db:
    ports:
      - "127.0.0.1:5432:5432"  # Only accessible from server itself
```

Then use SSH tunnel in DBeaver.

## Step 4: Set Up Database Backups

### Create Backup Script
```bash
# Create backup directory
mkdir -p ~/db-backups

# Create backup script
nano ~/backup-database.sh
```

Add this content:
```bash
#!/bin/bash

# Configuration
BACKUP_DIR=~/db-backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/seashell_db_${DATE}.sql"
POSTGRES_CONTAINER="full-stack-fastapi-template-db-1"
DB_NAME="app"
DB_USER="postgres"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Create backup
echo "Creating backup: ${BACKUP_FILE}"
docker exec ${POSTGRES_CONTAINER} pg_dump -U ${DB_USER} ${DB_NAME} > ${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_FILE}
echo "Backup created: ${BACKUP_FILE}.gz"

# Delete backups older than 30 days
find ${BACKUP_DIR} -name "*.sql.gz" -type f -mtime +30 -delete
echo "Old backups cleaned up (kept last 30 days)"

# Show backup size
ls -lh ${BACKUP_FILE}.gz
```

Make executable:
```bash
chmod +x ~/backup-database.sh
```

### Test Backup
```bash
# Run backup script
~/backup-database.sh

# Verify backup was created
ls -lh ~/db-backups/

# Check backup contents (should show SQL)
zcat ~/db-backups/*.sql.gz | head -20
```

### Set Up Automated Backups

#### Create Daily Backup Cron Job
```bash
# Edit crontab
crontab -e
```

Add this line:
```
# Daily database backup at 2 AM
0 2 * * * ~/backup-database.sh >> ~/db-backups/backup.log 2>&1
```

#### Verify Cron Job
```bash
# List cron jobs
crontab -l

# Check if cron is running
sudo systemctl status cron
```

## Step 5: Create Database Restore Procedure

### Create Restore Script
```bash
nano ~/restore-database.sh
```

Add this content:
```bash
#!/bin/bash

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: ./restore-database.sh <backup-file.sql.gz>"
    echo "Available backups:"
    ls -lh ~/db-backups/*.sql.gz
    exit 1
fi

BACKUP_FILE=$1
POSTGRES_CONTAINER="full-stack-fastapi-template-db-1"
DB_NAME="app"
DB_USER="postgres"

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Warning
echo "WARNING: This will restore the database from backup."
echo "Backup file: $BACKUP_FILE"
echo "This will OVERWRITE the current database!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Stop application containers
echo "Stopping application..."
cd ~/full-stack-fastapi-template
docker compose stop backend frontend

# Drop and recreate database
echo "Recreating database..."
docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -c "DROP DATABASE IF EXISTS ${DB_NAME};"
docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -c "CREATE DATABASE ${DB_NAME};"

# Restore backup
echo "Restoring backup..."
if [[ $BACKUP_FILE == *.gz ]]; then
    zcat $BACKUP_FILE | docker exec -i ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}
else
    cat $BACKUP_FILE | docker exec -i ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}
fi

# Restart application
echo "Restarting application..."
docker compose up -d

echo "Restore complete!"
```

Make executable:
```bash
chmod +x ~/restore-database.sh
```

### Test Restore (Optional)

**WARNING:** Only do this in development/testing!

```bash
# Create a test backup
~/backup-database.sh

# Restore from that backup
~/restore-database.sh ~/db-backups/seashell_db_*.sql.gz
```

## Step 6: Database Maintenance Tasks

### Analyze Database Size
```bash
# Check database size
docker compose exec db psql -U postgres -d app -c "
SELECT
    pg_size_pretty(pg_database_size('app')) as database_size;
"

# Check table sizes
docker compose exec db psql -U postgres -d app -c "
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Vacuum Database (Cleanup)
```bash
# Run vacuum to clean up dead tuples
docker compose exec db psql -U postgres -d app -c "VACUUM ANALYZE;"

# For more aggressive cleanup (locks tables briefly)
docker compose exec db psql -U postgres -d app -c "VACUUM FULL ANALYZE;"
```

### Check Database Statistics
```bash
# View connection stats
docker compose exec db psql -U postgres -d app -c "
SELECT
    datname,
    numbackends as connections,
    xact_commit as commits,
    xact_rollback as rollbacks
FROM pg_stat_database
WHERE datname = 'app';
"
```

## Step 7: DBeaver Usage Tips

### Execute Queries
1. Right-click connection → **SQL Editor** → **New SQL Script**
2. Write your query
3. Press **Ctrl+Enter** to execute

### View Tables
1. Expand connection → **Databases** → **app** → **Schemas** → **public** → **Tables**
2. Right-click table → **View Data**

### Export Data
1. Right-click table → **Export Data**
2. Choose format (CSV, JSON, SQL, etc.)
3. Follow wizard

### Common Queries

**View all users:**
```sql
SELECT id, email, full_name, is_active, is_superuser
FROM public.user;
```

**View all items:**
```sql
SELECT id, title, description, owner_id
FROM public.item;
```

**Check migrations:**
```sql
SELECT * FROM alembic_version;
```

## Verification Checklist

- [ ] Database container running and healthy
- [ ] Migrations completed successfully
- [ ] Can connect from server via psql
- [ ] Server Tailscale IP identified
- [ ] DBeaver connection configured and tested
- [ ] Can view tables and data in DBeaver
- [ ] Backup script created and tested
- [ ] Daily backup cron job configured
- [ ] Restore script created
- [ ] Database maintenance commands documented

## Troubleshooting

### Can't Connect from DBeaver

**Check Tailscale:**
```bash
# On server
tailscale status

# On laptop
tailscale status
```

Both should show connected.

**Check PostgreSQL Port:**
```bash
# On server
sudo ss -tulpn | grep 5432

# Should show PostgreSQL listening
```

**Check Firewall:**
Since you're using Tailscale, firewall should allow it:
```bash
# UFW should allow Tailscale network
sudo ufw status

# If needed, allow Tailscale
sudo ufw allow from 100.64.0.0/10 to any port 5432
```

**Check Docker Port Binding:**
```bash
docker compose ps db

# Should show: 0.0.0.0:5432->5432/tcp
```

### Backup Script Fails

**Check container name:**
```bash
# Find actual container name
docker ps | grep postgres

# Update POSTGRES_CONTAINER in script if different
```

**Check permissions:**
```bash
# Ensure backup directory exists and is writable
mkdir -p ~/db-backups
chmod 755 ~/db-backups
```

### DBeaver Shows "No Schema"

- Click refresh button in database navigator
- Right-click connection → **Edit Connection** → **PostgreSQL** tab → check "Show all databases"

## Security Considerations

1. **PostgreSQL Password**: Use strong password from Ticket 3.1
2. **Backup Encryption**: Consider encrypting backups:
   ```bash
   gpg -c backup.sql.gz  # Encrypt with password
   ```
3. **Access Control**: Only allow Tailscale network access to PostgreSQL
4. **Regular Backups**: Automated daily backups are critical
5. **Test Restores**: Periodically test restore procedure

## Backup Strategy Recommendations

### Daily Backups
- Automated via cron at 2 AM
- Keep last 30 days
- Stored locally on server

### Weekly Full Backups
- Copy to external location
- Use rsync or rclone to cloud storage

### Before Major Changes
- Manual backup before:
  - Migrations
  - Major updates
  - Schema changes

## Next Steps

After completing this ticket:
1. Ticket 3.3: Configure email service
2. Phase 4: Deploy application
3. Test database connectivity from running app
4. Monitor backup logs

## Useful DBeaver Features

- **ER Diagrams**: Right-click database → **View Diagram**
- **SQL History**: View → **Database Navigator** → **SQL History**
- **Data Compare**: Tools → **Compare → Databases**
- **Query Manager**: Organize and save common queries
- **Dark Theme**: Window → Preferences → Appearance → Theme

## Cost

All tools and configurations in this ticket are FREE:
- PostgreSQL (bundled)
- DBeaver Community Edition
- Backup scripts (custom)
- Tailscale Free tier