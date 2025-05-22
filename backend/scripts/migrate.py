import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

from alembic.config import Config
from alembic import command

# Add the backend directory to the path so we can import our app
sys.path.append(str(Path(__file__).parent.parent))

def run_alembic_command(command_name: str, *args) -> bool:
    """Run an alembic command and return True if successful."""
    try:
        # Get the directory containing this script
        base_dir = Path(__file__).parent.parent
        
        # Set up the Alembic configuration
        config = Config(str(base_dir / 'alembic.ini'))
        config.set_main_option('script_location', str(base_dir / 'app' / 'alembic'))
        
        # Import the models to ensure they're registered with SQLAlchemy
        from app.models import *  # noqa
        from app.core.config import settings
        
        # Set the database URL
        config.set_main_option('sqlalchemy.url', str(settings.SQLALCHEMY_DATABASE_URI))
        
        # Run the command
        getattr(command, command_name)(config, *args)
        return True
    except Exception as e:
        print(f"Error running {command_name}: {e}", file=sys.stderr)
        return False

def create_migration(message: Optional[str] = None) -> bool:
    """Create a new migration."""
    if not message:
        print("Please provide a message for the migration with --message")
        return False
    
    print(f"Creating migration: {message}")
    return run_alembic_command('revision', '--autogenerate', '-m', message)

def upgrade_database(revision: str = 'head') -> bool:
    """Upgrade the database to the specified revision."""
    print(f"Upgrading database to revision: {revision}")
    return run_alembic_command('upgrade', revision)

def downgrade_database(revision: str) -> bool:
    """Downgrade the database to the specified revision."""
    print(f"Downgrading database to revision: {revision}")
    return run_alembic_command('downgrade', revision)

def show_current() -> bool:
    """Show the current revision."""
    print("Current database revision:")
    return run_alembic_command('current')

def show_history() -> bool:
    """Show migration history."""
    print("Migration history:")
    return run_alembic_command('history')

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration utility')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('--message', '-m', required=True, help='Migration message')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('--revision', '-r', default='head', help='Target revision')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', help='Target revision')
    
    # Show current revision
    subparsers.add_parser('current', help='Show current revision')
    
    # Show history
    subparsers.add_parser('history', help='Show migration history')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'create':
        success = create_migration(args.message)
    elif args.command == 'upgrade':
        success = upgrade_database(args.revision)
    elif args.command == 'downgrade':
        success = downgrade_database(args.revision)
    elif args.command == 'current':
        success = show_current()
    elif args.command == 'history':
        success = show_history()
    else:
        print(f"Unknown command: {args.command}")
        return 1
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
