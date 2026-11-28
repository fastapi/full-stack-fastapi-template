import os
import subprocess
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import IntegrityError

from app.core.config import settings

BACKEND_DIR = Path(__file__).resolve().parents[1]
SCRATCH_DB = "app_role_migration_test"


def _alembic(url: URL, *args: str) -> None:
    env = {**os.environ, "DATABASE_URL": url.render_as_string(hide_password=False)}
    subprocess.run(["alembic", *args], cwd=BACKEND_DIR, env=env, check=True)


@pytest.fixture
def scratch_url() -> Generator[URL]:
    base_url = make_url(str(settings.DATABASE_URL))
    admin_engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH_DB}"))
        conn.execute(text(f"CREATE DATABASE {SCRATCH_DB}"))
    yield base_url.set(database=SCRATCH_DB)
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH_DB} WITH (FORCE)"))
    admin_engine.dispose()


def test_role_migration_on_populated_db(scratch_url: URL) -> None:
    _alembic(scratch_url, "upgrade", "fe56fa70289e")
    engine = create_engine(scratch_url)
    with engine.begin() as conn:
        conn.execute(
            text(
                'INSERT INTO "user" (id, email, is_active, is_superuser, hashed_password) VALUES '
                "(gen_random_uuid(), 'super@example.com', true, true, 'x'), "
                "(gen_random_uuid(), 'normal@example.com', true, false, 'x'), "
                "(gen_random_uuid(), 'inactive-super@example.com', false, true, 'x')"
            )
        )

    _alembic(scratch_url, "upgrade", "head")
    with engine.begin() as conn:
        roles = dict(conn.execute(text('SELECT email, role FROM "user"')).all())
        columns = {
            row[0]
            for row in conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'user'"
                )
            )
        }
    assert roles == {
        "super@example.com": "admin",
        "normal@example.com": "member",
        "inactive-super@example.com": "admin",
    }
    assert "is_superuser" not in columns

    with pytest.raises(IntegrityError), engine.begin() as conn:
        conn.execute(
            text(
                'INSERT INTO "user" (id, email, is_active, role, hashed_password) '
                "VALUES (gen_random_uuid(), 'bad@example.com', true, 'owner', 'x')"
            )
        )

    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE \"user\" SET role = 'manager' WHERE email = 'normal@example.com'"
            )
        )

    _alembic(scratch_url, "downgrade", "fe56fa70289e")
    with engine.begin() as conn:
        superusers = dict(
            conn.execute(text('SELECT email, is_superuser FROM "user"')).all()
        )
    engine.dispose()
    assert superusers == {
        "super@example.com": True,
        "normal@example.com": False,
        "inactive-super@example.com": True,
    }
