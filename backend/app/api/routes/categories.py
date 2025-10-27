import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import AdministradorUser, CurrentUser, SessionDep
from app import crud
from app.models import (
    Category,
    CategoryCreate,
    CategoryPublic,
    CategoriesPublic,
    CategoryUpdate,
    Message,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=CategoriesPublic)
def read_categories(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> Any:
    """
    Retrieve categories.
    All authenticated users can view categories.
    """
    count_statement = select(func.count()).select_from(Category)
    statement = select(Category)

    if active_only:
        count_statement = count_statement.where(Category.is_active == True)
        statement = statement.where(Category.is_active == True)

    count = session.exec(count_statement).one()
    statement = statement.offset(skip).limit(limit).order_by(Category.name)
    categories = session.exec(statement).all()

    return CategoriesPublic(data=categories, count=count)


@router.get("/{id}", response_model=CategoryPublic)
def read_category(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get category by ID.
    All authenticated users can view categories.
    """
    category = crud.get_category_by_id(session=session, category_id=id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryPublic, status_code=201)
def create_category(
    *,
    session: SessionDep,
    current_user: AdministradorUser,
    category_in: CategoryCreate
) -> Any:
    """
    Create new category.
    Only administrador can create categories.
    """
    category = crud.create_category(
        session=session,
        category_in=category_in,
        created_by=current_user.id
    )
    return category


@router.patch("/{id}", response_model=CategoryPublic)
def update_category(
    *,
    session: SessionDep,
    current_user: AdministradorUser,
    id: uuid.UUID,
    category_in: CategoryUpdate,
) -> Any:
    """
    Update a category.
    Only administrador can update categories.
    """
    db_category = crud.get_category_by_id(session=session, category_id=id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    category = crud.update_category(
        session=session,
        db_category=db_category,
        category_in=category_in
    )
    return category


@router.delete("/{id}", response_model=Message)
def delete_category(
    session: SessionDep, current_user: AdministradorUser, id: uuid.UUID
) -> Any:
    """
    Soft delete a category (set is_active=False).
    Only administrador can delete categories.
    """
    db_category = crud.get_category_by_id(session=session, category_id=id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Soft delete by setting is_active=False
    category_update = CategoryUpdate(is_active=False)
    crud.update_category(
        session=session,
        db_category=db_category,
        category_in=category_update
    )

    return Message(message="Category deleted successfully")
