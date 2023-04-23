from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Permission])
def read_permissions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve permissions.
    """
    if crud.user.is_superuser(current_user):
        permissions = crud.permission.get_multi(db, skip=skip, limit=limit)
    else:
        permissions = crud.permission.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return permissions


@router.post("/", response_model=schemas.Permission)
def create_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_in: schemas.PermissionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new permission.
    """
    permission = crud.permission.create_with_owner(db=db, obj_in=permission_in, owner_id=current_user.id)
    return permission


@router.put("/{id}", response_model=schemas.Permission)
def update_permission(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    permission_in: schemas.PermissionUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an permission.
    """
    permission = crud.permission.get(db=db, id=id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if not crud.user.is_superuser(current_user) and (permission.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    permission = crud.permission.update_with_owner(db=db, obj_in=permission_in, owner_id=current_user)
    return permission


@router.get("/{id}", response_model=schemas.Permission)
def read_permission(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get permission by ID.
    """
    permission = crud.permission.get(db=db, id=id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if not crud.user.is_superuser(current_user) and (permission.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return permission


@router.delete("/{id}", response_model=schemas.Permission)
def delete_permission(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an permission.
    """
    permission = crud.permission.get(db=db, id=id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if not crud.user.is_superuser(current_user) and (permission.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    permission = crud.permission.remove(db=db, id=id)
    return permission
