"""
Database initialization script.
This script initializes the database and runs migrations.
"""
import sys
import subprocess
from pathlib import Path

# Add the backend directory to the path so we can import our app
sys.path.append(str(Path(__file__).parent.parent))

def run_command(command: str) -> bool:
    """Run a shell command and return True if successful.
    
    SECURITY WARNING: This function uses shell=True which can be dangerous
    if used with untrusted input. Only use with hardcoded commands.
    """
    try:
        print(f"🚀 Running: {command}")
        # SECURITY NOTE: shell=True is used here but all commands are hardcoded
        # and do not accept user input, making it safe in this context
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  {result.stderr}", file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with error: {e}", file=sys.stderr)
        print(f"Command output: {e.output}", file=sys.stderr)
        print(f"Command stderr: {e.stderr}", file=sys.stderr)
        return False

def check_database() -> bool:
    """Check if the database is accessible."""
    print("🔍 Checking database connection...")
    return run_command("python -m scripts.check_db")

def run_migrations() -> bool:
    """Run database migrations."""
    print("🚀 Running migrations...")
    return run_command("python -m scripts.migrate upgrade head")

def create_initial_data() -> bool:
    """Create initial data in the database."""
    print("✨ Creating initial data...")
    return run_command("python -c \"
import sys
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import UserInDB
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
    sys.exit(0)
except Exception as e:
    print(f'❌ Error setting up initial data: {e}', file=sys.stderr)
    sys.exit(1)
\""")

def main():
    """Main function to run database initialization."""
    print("🚀 Starting database initialization...")
    
    # Check if the database is accessible
    if not check_database():
        print("❌ Database connection check failed. Please check your database configuration.")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Database migrations failed. Please check the error messages above.")
        sys.exit(1)
    
    # Create initial data
    if not create_initial_data():
        print("⚠️  Failed to create initial data. Continuing anyway...")
    
    print("✅ Database initialization complete!")
    sys.exit(0)

if __name__ == "__main__":
    main()
