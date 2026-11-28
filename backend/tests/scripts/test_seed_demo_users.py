import pytest
from sqlmodel import Session, col, select

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import User, UserRole, UserUpdate
from app.seed_demo_users import DEMO_USERS, main, seed

PASSWORD = "DemoPass123!"


def _demo_users(db: Session) -> dict[str, User]:
    users = db.exec(select(User).where(col(User.email).in_(DEMO_USERS))).all()
    for user in users:
        db.refresh(user)
    return {user.email: user for user in users}


def test_seed_creates_three_role_users_and_converges(db: Session) -> None:
    seed(db, PASSWORD)
    seed(db, PASSWORD)

    users = _demo_users(db)
    assert {email: u.role for email, u in users.items()} == {
        "demo-admin@example.com": UserRole.ADMIN,
        "demo-manager@example.com": UserRole.MANAGER,
        "demo-member@example.com": UserRole.MEMBER,
    }

    member = users["demo-member@example.com"]
    crud.update_user(
        session=db,
        db_user=member,
        user_in=UserUpdate(role=UserRole.ADMIN, is_active=False, password="other-pass"),
    )
    seed(db, PASSWORD)

    member = _demo_users(db)["demo-member@example.com"]
    assert member.role == UserRole.MEMBER
    assert member.is_active is True
    assert verify_password(PASSWORD, member.hashed_password)[0]
    admin = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert admin and admin.role == UserRole.ADMIN


def test_seed_refuses_outside_development(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "FASTAPI_ENV", None)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
