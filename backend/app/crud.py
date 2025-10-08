import uuid
from typing import Any
from datetime import datetime, timedelta

from sqlmodel import Session, select, func, or_

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserUpdate,
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    Project,
    ProjectCreate,
    ProjectUpdate,
    Gallery,
    GalleryCreate,
    GalleryUpdate,
    DashboardStats,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
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
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# ============================================================================
# ORGANIZATION CRUD
# ============================================================================

def create_organization(*, session: Session, organization_in: OrganizationCreate) -> Organization:
    db_obj = Organization.model_validate(organization_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_organization(*, session: Session, organization_id: uuid.UUID) -> Organization | None:
    return session.get(Organization, organization_id)


def update_organization(
    *, session: Session, db_organization: Organization, organization_in: OrganizationUpdate
) -> Organization:
    organization_data = organization_in.model_dump(exclude_unset=True)
    db_organization.sqlmodel_update(organization_data)
    session.add(db_organization)
    session.commit()
    session.refresh(db_organization)
    return db_organization


# ============================================================================
# PROJECT CRUD
# ============================================================================

def create_project(*, session: Session, project_in: ProjectCreate) -> Project:
    db_obj = Project.model_validate(project_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_project(*, session: Session, project_id: uuid.UUID) -> Project | None:
    return session.get(Project, project_id)


def get_projects_by_organization(
    *, session: Session, organization_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
        .order_by(Project.created_at.desc())
    )
    return list(session.exec(statement).all())


def count_projects_by_organization(*, session: Session, organization_id: uuid.UUID) -> int:
    statement = select(func.count()).select_from(Project).where(Project.organization_id == organization_id)
    return session.exec(statement).one()


def update_project(*, session: Session, db_project: Project, project_in: ProjectUpdate) -> Project:
    project_data = project_in.model_dump(exclude_unset=True)
    project_data["updated_at"] = datetime.utcnow()
    db_project.sqlmodel_update(project_data)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


def delete_project(*, session: Session, project_id: uuid.UUID) -> None:
    project = session.get(Project, project_id)
    if project:
        session.delete(project)
        session.commit()


# ============================================================================
# GALLERY CRUD
# ============================================================================

def create_gallery(*, session: Session, gallery_in: GalleryCreate) -> Gallery:
    db_obj = Gallery.model_validate(gallery_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_gallery(*, session: Session, gallery_id: uuid.UUID) -> Gallery | None:
    return session.get(Gallery, gallery_id)


def get_galleries_by_project(
    *, session: Session, project_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Gallery]:
    statement = (
        select(Gallery)
        .where(Gallery.project_id == project_id)
        .offset(skip)
        .limit(limit)
        .order_by(Gallery.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_galleries_by_organization(
    *, session: Session, organization_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Gallery]:
    """Get all galleries for projects in an organization"""
    statement = (
        select(Gallery)
        .join(Project)
        .where(Project.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
        .order_by(Gallery.created_at.desc())
    )
    return list(session.exec(statement).all())


def count_galleries_by_organization(*, session: Session, organization_id: uuid.UUID) -> int:
    statement = (
        select(func.count())
        .select_from(Gallery)
        .join(Project)
        .where(Project.organization_id == organization_id)
    )
    return session.exec(statement).one()


def update_gallery(*, session: Session, db_gallery: Gallery, gallery_in: GalleryUpdate) -> Gallery:
    gallery_data = gallery_in.model_dump(exclude_unset=True)
    db_gallery.sqlmodel_update(gallery_data)
    session.add(db_gallery)
    session.commit()
    session.refresh(db_gallery)
    return db_gallery


def delete_gallery(*, session: Session, gallery_id: uuid.UUID) -> None:
    gallery = session.get(Gallery, gallery_id)
    if gallery:
        session.delete(gallery)
        session.commit()


# ============================================================================
# DASHBOARD STATS
# ============================================================================

def get_dashboard_stats(*, session: Session, organization_id: uuid.UUID) -> DashboardStats:
    """Calculate dashboard statistics for an organization"""
    
    # Count active projects (in_progress or review status)
    active_projects_stmt = (
        select(func.count())
        .select_from(Project)
        .where(
            Project.organization_id == organization_id,
            or_(Project.status == "in_progress", Project.status == "review")
        )
    )
    active_projects = session.exec(active_projects_stmt).one()
    
    # Count upcoming deadlines (projects with deadline in next 14 days, not completed)
    today = datetime.utcnow().date()
    two_weeks = today + timedelta(days=14)
    upcoming_deadlines_stmt = (
        select(func.count())
        .select_from(Project)
        .where(
            Project.organization_id == organization_id,
            Project.deadline.isnot(None),
            Project.deadline >= today,
            Project.deadline <= two_weeks,
            Project.status != "completed"
        )
    )
    upcoming_deadlines = session.exec(upcoming_deadlines_stmt).one()
    
    # Count team members in organization
    team_members_stmt = (
        select(func.count())
        .select_from(User)
        .where(User.organization_id == organization_id)
    )
    team_members = session.exec(team_members_stmt).one()
    
    # Count completed projects this month
    first_day_of_month = today.replace(day=1)
    completed_this_month_stmt = (
        select(func.count())
        .select_from(Project)
        .where(
            Project.organization_id == organization_id,
            Project.status == "completed",
            Project.updated_at >= first_day_of_month
        )
    )
    completed_this_month = session.exec(completed_this_month_stmt).one()
    
    return DashboardStats(
        active_projects=active_projects,
        upcoming_deadlines=upcoming_deadlines,
        team_members=team_members,
        completed_this_month=completed_this_month,
    )
