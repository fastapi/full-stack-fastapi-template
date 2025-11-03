import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, desc, func, or_, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    DashboardStats,
    Gallery,
    GalleryCreate,
    GalleryUpdate,
    Item,
    ItemCreate,
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    Project,
    ProjectAccess,
    ProjectAccessCreate,
    ProjectAccessUpdate,
    ProjectCreate,
    ProjectUpdate,
    User,
    UserCreate,
    UserUpdate,
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


def create_organization(
    *, session: Session, organization_in: OrganizationCreate
) -> Organization:
    db_obj = Organization.model_validate(organization_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_organization(
    *, session: Session, organization_id: uuid.UUID
) -> Organization | None:
    return session.get(Organization, organization_id)


def get_default_organization(*, session: Session) -> Organization | None:
    """Get the default organization (typically 'Default Organization')"""
    statement = select(Organization).where(Organization.name == "Default Organization")
    return session.exec(statement).first()


def update_organization(
    *,
    session: Session,
    db_organization: Organization,
    organization_in: OrganizationUpdate,
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
        .order_by(desc(Project.created_at))
    )
    return list(session.exec(statement).all())


def count_projects_by_organization(
    *, session: Session, organization_id: uuid.UUID
) -> int:
    statement = (
        select(func.count())
        .select_from(Project)
        .where(Project.organization_id == organization_id)
    )
    return session.exec(statement).one()


def update_project(
    *, session: Session, db_project: Project, project_in: ProjectUpdate
) -> Project:
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
        .order_by(desc(Gallery.created_at))
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
        .order_by(desc(Gallery.created_at))
    )
    return list(session.exec(statement).all())


def count_galleries_by_organization(
    *, session: Session, organization_id: uuid.UUID
) -> int:
    statement = (
        select(func.count())
        .select_from(Gallery)
        .join(Project)
        .where(Project.organization_id == organization_id)
    )
    return session.exec(statement).one()


def update_gallery(
    *, session: Session, db_gallery: Gallery, gallery_in: GalleryUpdate
) -> Gallery:
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
# PROJECT ACCESS CRUD
# ============================================================================


def create_project_access(
    *, session: Session, access_in: ProjectAccessCreate
) -> ProjectAccess:
    """Grant a user access to a project"""
    # Check if access already exists
    existing = session.exec(
        select(ProjectAccess).where(
            ProjectAccess.project_id == access_in.project_id,
            ProjectAccess.user_id == access_in.user_id,
        )
    ).first()
    
    if existing:
        # Update existing access
        for key, value in access_in.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    
    # Create new access
    db_obj = ProjectAccess.model_validate(access_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_project_access(
    *, session: Session, project_id: uuid.UUID, user_id: uuid.UUID
) -> ProjectAccess | None:
    """Get a user's access to a specific project"""
    statement = select(ProjectAccess).where(
        ProjectAccess.project_id == project_id,
        ProjectAccess.user_id == user_id,
    )
    return session.exec(statement).first()


def get_project_access_list(
    *, session: Session, project_id: uuid.UUID
) -> list[ProjectAccess]:
    """Get all users with access to a project"""
    statement = select(ProjectAccess).where(ProjectAccess.project_id == project_id)
    return list(session.exec(statement).all())


def get_user_accessible_projects(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Project]:
    """Get all projects a user has access to (for clients)"""
    statement = (
        select(Project)
        .join(ProjectAccess)
        .where(ProjectAccess.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(desc(Project.created_at))
    )
    return list(session.exec(statement).all())


def count_user_accessible_projects(*, session: Session, user_id: uuid.UUID) -> int:
    """Count projects a user has access to"""
    statement = (
        select(func.count())
        .select_from(Project)
        .join(ProjectAccess)
        .where(ProjectAccess.user_id == user_id)
    )
    return session.exec(statement).one()


def update_project_access(
    *, session: Session, db_access: ProjectAccess, access_in: ProjectAccessUpdate
) -> ProjectAccess:
    """Update project access permissions"""
    access_data = access_in.model_dump(exclude_unset=True)
    db_access.sqlmodel_update(access_data)
    session.add(db_access)
    session.commit()
    session.refresh(db_access)
    return db_access


def delete_project_access(
    *, session: Session, project_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    """Remove a user's access to a project"""
    access = get_project_access(
        session=session, project_id=project_id, user_id=user_id
    )
    if access:
        session.delete(access)
        session.commit()


def user_has_project_access(
    *, session: Session, project_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    """Check if a user has access to a project"""
    statement = (
        select(func.count())
        .select_from(ProjectAccess)
        .where(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id,
        )
    )
    count = session.exec(statement).one()
    return count > 0


# ============================================================================
# DASHBOARD STATS
# ============================================================================


def get_dashboard_stats(
    *, session: Session, organization_id: uuid.UUID
) -> DashboardStats:
    """Calculate dashboard statistics for an organization"""

    # Count active projects (in_progress or review status)
    active_projects_stmt = (
        select(func.count())
        .select_from(Project)
        .where(
            Project.organization_id == organization_id,
            or_(Project.status == "in_progress", Project.status == "review"),
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
            Project.deadline.isnot(None),  # type: ignore[union-attr]
            Project.deadline >= today,  # type: ignore[operator]
            Project.deadline <= two_weeks,  # type: ignore[operator]
            Project.status != "completed",
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
            Project.updated_at >= first_day_of_month,
        )
    )
    completed_this_month = session.exec(completed_this_month_stmt).one()

    return DashboardStats(
        active_projects=active_projects,
        upcoming_deadlines=upcoming_deadlines,
        team_members=team_members,
        completed_this_month=completed_this_month,
    )
