import secrets
import uuid
from typing import Any

from sqlmodel import Session, col, func, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    AuditAction,
    AuditLog,
    AuditLogPublic,
    Company,
    CompanyCreate,
    CompanyInvite,
    CompanyRegistrationComplete,
    CompanyStatus,
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    password = user_create.password or secrets.token_urlsafe(32)
    is_superuser = (
        user_create.role == UserRole.super_admin
        if hasattr(user_create, "role")
        else False
    )
    db_obj = User.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(password),
            "is_superuser": is_superuser,
            "is_active": True,
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    if "role" in user_data and user_data["role"] is not None:
        extra_data["is_superuser"] = user_data["role"] == UserRole.super_admin
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_company_by_cnpj(*, session: Session, cnpj: str) -> Company | None:
    statement = select(Company).where(Company.cnpj == cnpj)
    return session.exec(statement).first()


def create_company(*, session: Session, company_in: CompanyCreate) -> Company:
    db_company = Company.model_validate(company_in)
    session.add(db_company)
    session.commit()
    session.refresh(db_company)
    return db_company


def create_company_initial(
    *, session: Session, cnpj: str, email: str, razao_social: str
) -> Company:
    db_company = Company(
        cnpj=cnpj,
        email=email,
        razao_social=razao_social,
        status=CompanyStatus.pending,
    )
    session.add(db_company)
    session.commit()
    session.refresh(db_company)
    return db_company


def create_company_invite(
    *, session: Session, company_id: uuid.UUID, email: str, token: str, expires_at: Any
) -> CompanyInvite:
    db_invite = CompanyInvite(
        company_id=company_id,
        email=email,
        token=token,
        expires_at=expires_at,
    )
    session.add(db_invite)
    session.commit()
    session.refresh(db_invite)
    return db_invite


def get_invite_by_token(*, session: Session, token: str) -> CompanyInvite | None:
    statement = select(CompanyInvite).where(CompanyInvite.token == token)
    return session.exec(statement).first()


def complete_company_registration(
    *,
    session: Session,
    company: Company,
    invite: CompanyInvite,
    registration_data: CompanyRegistrationComplete,
) -> Company:
    update_data = registration_data.model_dump(exclude={"token"})
    company.sqlmodel_update(update_data)
    company.status = CompanyStatus.completed
    session.add(company)

    invite.used = True
    session.add(invite)

    session.commit()
    session.refresh(company)
    return company


def create_audit_log(
    *,
    session: Session,
    action: AuditAction,
    target_user_id: uuid.UUID,
    performed_by_id: uuid.UUID,
    changes: str = "",
) -> AuditLog:
    db_log = AuditLog(
        action=action,
        target_user_id=target_user_id,
        performed_by_id=performed_by_id,
        changes=changes,
    )
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


def get_audit_logs(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[AuditLogPublic], int]:
    count_statement = select(func.count()).select_from(AuditLog)
    count = session.exec(count_statement).one()

    statement = (
        select(AuditLog)
        .order_by(col(AuditLog.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    logs = session.exec(statement).all()

    result = []
    for log in logs:
        target = session.get(User, log.target_user_id)
        performer = session.get(User, log.performed_by_id)
        result.append(
            AuditLogPublic(
                id=log.id,
                action=log.action,
                target_user_id=log.target_user_id,
                performed_by_id=log.performed_by_id,
                changes=log.changes,
                created_at=log.created_at,
                target_user_email=target.email if target else None,
                performed_by_email=performer.email if performer else None,
            )
        )
    return result, count
