#!/bin/bash
set -e

echo "🚀 Starting Genius Industries..."

# Create log directories
mkdir -p /var/log/supervisor /var/log/nginx /var/log/postgresql

# Initialize PostgreSQL if needed
if [ ! -d "/var/lib/postgresql/14/main/base" ]; then
    echo "🐘 Initializing PostgreSQL..."
    su - postgres -c "/usr/lib/postgresql/14/bin/initdb -D /var/lib/postgresql/14/main"
    
    # Basic PostgreSQL configuration
    {
        echo "listen_addresses = '*'"
        echo "port = 5432"
        echo "max_connections = 100"
        echo "shared_buffers = 128MB"
    } > /var/lib/postgresql/14/main/postgresql.conf
    
    {
        echo "local   all             postgres                peer"
        echo "local   all             all                     md5"
        echo "host    all             all             127.0.0.1/32   md5"
        echo "host    all             all             ::1/128        md5"
    } > /var/lib/postgresql/14/main/pg_hba.conf
    
    chown postgres:postgres /var/lib/postgresql/14/main/postgresql.conf
    chown postgres:postgres /var/lib/postgresql/14/main/pg_hba.conf
fi

echo "✅ Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
