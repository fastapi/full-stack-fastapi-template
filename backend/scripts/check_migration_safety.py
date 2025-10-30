#!/usr/bin/env python3
"""Pre-commit hook to check Alembic migration files for dangerous operations.

This script prevents migrations that could cause data loss by:
1. Detecting CREATE TABLE operations (should use ALTER TABLE instead)
2. Detecting DROP TABLE operations without explicit confirmation
3. Detecting DROP COLUMN operations without explicit confirmation
4. Ensuring migrations have both upgrade() and downgrade() functions

Exit codes:
0 - All migrations are safe
1 - Dangerous operations detected
"""
import re
import sys
from pathlib import Path


def check_migration_file(filepath: Path) -> list[str]:
    """Check a single migration file for dangerous operations.

    Args:
        filepath: Path to the migration file

    Returns:
        List of error messages (empty if no issues)
    """
    errors = []
    content = filepath.read_text()

    # Check if this is a baseline migration (down_revision = None)
    is_baseline = re.search(r"down_revision\s*=\s*None", content) is not None

    # Check for CREATE TABLE operations (allowed for baseline migrations)
    if re.search(r"op\.create_table\s*\(", content):
        if not is_baseline:
            errors.append(
                f"❌ {filepath.name}: Contains CREATE TABLE operation. "
                "This may drop and recreate existing tables, causing DATA LOSS. "
                "Use ALTER TABLE ADD COLUMN instead."
            )

    # Check for DROP TABLE operations without explicit confirmation
    if re.search(r"op\.drop_table\s*\(", content):
        if "# CONFIRMED: Safe to drop table" not in content and not is_baseline:
            errors.append(
                f"⚠️  {filepath.name}: Contains DROP TABLE operation without confirmation. "
                "Add comment '# CONFIRMED: Safe to drop table' if this is intentional."
            )

    # Check for DROP COLUMN operations without explicit confirmation
    if re.search(r"op\.drop_column\s*\(", content):
        if "# CONFIRMED: Safe to drop column" not in content:
            errors.append(
                f"⚠️  {filepath.name}: Contains DROP COLUMN operation without confirmation. "
                "Add comment '# CONFIRMED: Safe to drop column' if this is intentional."
            )

    # Check for empty upgrade() or downgrade() functions (skip for baseline)
    if re.search(r"def upgrade\(\):\s+pass", content) and not is_baseline:
        errors.append(
            f"⚠️  {filepath.name}: upgrade() function is empty. "
            "This migration does nothing."
        )

    if not re.search(r"def downgrade\(\):", content):
        errors.append(
            f"❌ {filepath.name}: Missing downgrade() function. "
            "All migrations must be reversible."
        )

    return errors


def main() -> int:
    """Check all staged migration files for dangerous operations."""
    migrations_dir = Path(__file__).parent.parent / "app" / "alembic" / "versions"

    if not migrations_dir.exists():
        print("❌ Alembic versions directory not found")
        return 1

    # Get all Python migration files (excluding __pycache__)
    migration_files = [
        f for f in migrations_dir.glob("*.py")
        if f.name != "__init__.py" and not f.name.startswith(".")
    ]

    all_errors = []
    for filepath in migration_files:
        errors = check_migration_file(filepath)
        all_errors.extend(errors)

    if all_errors:
        print("\n🚨 MIGRATION SAFETY ERRORS DETECTED:\n")
        for error in all_errors:
            print(error)
        print(
            "\n💡 To fix:\n"
            "   1. For existing tables: Use ALTER TABLE ADD COLUMN instead of CREATE TABLE\n"
            "   2. For DROP operations: Add explicit confirmation comments\n"
            "   3. For empty migrations: Delete the file or add actual operations\n"
        )
        return 1

    print("✅ All migration files passed safety checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
