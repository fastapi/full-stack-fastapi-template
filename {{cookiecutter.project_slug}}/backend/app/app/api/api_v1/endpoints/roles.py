from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.api_v1.api_permissions import check_user_permissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Role])
def read_roles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve roles.
    """
    if check_user_permissions('roles', 'read', current_user):
        if crud.user.is_superuser(current_user):
            roles = crud.role.get_multi(db, skip=skip, limit=limit)
        else:
            roles = crud.role.get_multi_by_owner(
                db=db, owner_id=current_user.id, skip=skip, limit=limit
            )

        return roles
    else:
        raise HTTPException(status_code=401, detail="Not allowed")


@router.post("/", response_model=schemas.Role)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role_in: schemas.RoleCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new role.
    """
    role = crud.role.create_with_owner(db=db, obj_in=role_in, owner_id=current_user.id)
    return role


@router.put("/{id}", response_model=schemas.Role)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    role_in: schemas.RoleUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an role.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not crud.user.is_superuser(current_user) and (role.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    role = crud.role.update(db=db, db_obj=role, obj_in=role_in)
    return role


@router.get("/{id}", response_model=schemas.Role)
def read_role(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get role by ID.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not crud.user.is_superuser(current_user) and (role.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return role


@router.delete("/{id}", response_model=schemas.Role)
def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an role.
    """
    role = crud.role.get(db=db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if not crud.user.is_superuser(current_user) and (role.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    role = crud.role.remove(db=db, id=id)
    return role
