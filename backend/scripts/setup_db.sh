#!/bin/bash
set -e

# Change to the backend directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    fi
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Python is not installed or not in PATH"
    exit 1
fi

# Install dependencies if not already installed
pip install -e ".[dev]"

# Check if database is accessible
if ! python -c "
import sys
from sqlalchemy import create_engine
from app.core.config import settings

try:
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✅ Database connection successful!')
    sys.exit(0)
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('\nPlease ensure that:')
    print('1. PostgreSQL is installed and running')
    print('2. The database exists and is accessible')
    print(f'3. The connection string is correct: {settings.SQLALCHEMY_DATABASE_URI}')
    sys.exit(1)
"; then
    exit 1
fi

# Run migrations
echo "🚀 Running migrations..."
python -m scripts.migrate upgrade head

# Create initial data if needed
echo "✨ Setting up initial data..."
python -c "
import sys
from app.db.session import SessionLocal
from app.core.config import settings
from app.models import UserInDB
from app.core.security import get_password_hash

try:
    db = SessionLocal()
    # Create initial admin user if it doesn't exist
    admin = db.query(UserInDB).filter(UserInDB.email == settings.FIRST_SUPERUSER).first()
    if not admin and settings.FIRST_SUPERUSER and settings.FIRST_SUPERUSER_PASSWORD:
        admin = UserInDB(
            email=settings.FIRST_SUPERUSER,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_active=True,
            is_verified=True,
            email_verified=True,
            role='superuser',
            full_name='Admin User'
        )
        db.add(admin)
        db.commit()
        print('✅ Created initial admin user')
    else:
        print('ℹ️  Admin user already exists')
    
    db.close()
except Exception as e:
    print(f'❌ Error setting up initial data: {e}')
    sys.exit(1)
"

echo "🎉 Database setup complete!"
