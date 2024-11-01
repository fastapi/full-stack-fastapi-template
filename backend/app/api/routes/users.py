import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.deps import (
    SessionDep,
    get_business_user,
    get_current_user,
    get_db,
    get_public_user,
    get_super_user,
)
from app.models import UserBusiness, UserPublic
from app.schema.user import (
    UserBusinessCreate,
    UserBusinessRead,
    UserBusinessUpdate,
    UserPublicRead,
    UserPublicUpdate,
)
from app.util import (
    create_record,
    delete_record,
    get_all_records,
    get_record_by_id,
    update_record,
)

router = APIRouter()


@router.get("/me", response_model=UserPublicRead | UserBusinessRead)
async def read_user_me(
    current_user: UserPublic | UserBusiness = Depends(get_current_user),
):
    print("current_user", current_user)
    """
    Retrieve profile information of the currently authenticated user.
    """
    x = current_user.to_read_schema()
    print("hui", x)
    return x


@router.get("/all-user-business/", response_model=list[UserBusinessRead])
async def all_read_user_business(
    db: Session = Depends(get_db),
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100),
    current_user: UserBusiness = Depends(get_super_user),  # noqa: ARG001
):
    """
    Retrieve a paginated list of user businesses.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    all_users = get_all_records(db, UserBusiness, skip=skip, limit=limit)

    if all_users is None:
        raise HTTPException(status_code=404, detail="No user businesses found.")

    # Convert each record to its read schema
    assert all(
        hasattr(user, "to_read_schema") for user in all_users
    ), "Each user must implement 'to_read_schema'"

    return [user.to_read_schema() for user in all_users]


@router.get("/user-businesses/{user_business_id}", response_model=UserBusinessRead)
async def read_user_business(
    user_business_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_super_user),  # noqa: ARG001
):
    """
    Retrieve a single user business by ID.
    - **user_business_id**: The ID of the user business to retrieve
    """
    user_instance = get_record_by_id(db, UserBusiness, user_business_id)

    return user_instance.to_read_schema()


@router.post("/user-businesses/", response_model=UserBusinessRead)
async def create_user_business(
    user_business: UserBusinessCreate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_super_user),
):
    """
    Create a new user business.
    - **user_business**: The user business data to create
    """

    try:
        user_instance = UserBusiness.from_create_schema(user_business)
        user_instance.id = current_user.id
        return create_record(db, user_instance)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/user-businesses/{user_business_id}", response_model=UserBusinessRead)
async def update_user_business(
    user_business: UserBusinessUpdate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_current_user),
):
    """
    Update an existing user business.
    - **user_business_id**: The ID of the user business to update
    - **user_business**: The updated user business data
    """
    try:
        user_instance = UserBusiness.from_create_schema(user_business)
        return update_record(db, current_user, user_instance)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/user-businesses/{user_business_id}", response_model=dict)
async def delete_user_business(
    user_business_id: uuid.UUID,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_super_user),  # noqa: ARG001
):
    """
    Delete a user business by ID.
    - **user_business_id**: The ID of the user business to delete
    """
    user_instance = get_record_by_id(session, UserBusiness, user_business_id)

    delete_record(session, user_instance)
    return {"message": f"UserBusiness with ID {user_business_id} has been deleted."}


@router.get("/all-user-public/", response_model=list[UserPublicRead])
async def all_read_user_public(
    db: Session = Depends(get_db),
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100),
    current_user: UserBusiness = Depends(get_business_user),  # noqa: ARG001
):
    """
    Retrieve a paginated list of user public.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    all_users = get_all_records(db, UserPublic, skip=skip, limit=limit)

    if all_users is None:
        raise HTTPException(status_code=404, detail="No user found.")

    assert all(
        hasattr(user, "to_read_schema") for user in all_users
    ), "Each user must implement 'to_read_schema'"

    # Convert each record to its read schema
    return [user.to_read_schema() for user in all_users]


@router.get("/user-public/{user_public_id}", response_model=UserPublicRead)
async def read_user_public(
    user_public_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_business_user),  # noqa: ARG001
):
    """
    Retrieve a single user public by ID.
    - **user_public_id**: The ID of the user public to retrieve
    """
    user_instance = get_record_by_id(db, UserBusiness, user_public_id)

    return user_instance.to_read_schema()


@router.patch("/user-public/", response_model=UserPublicRead)
async def update_user_public_me(
    user_public: UserPublicUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_public_user),
):
    """
    Update an existing user public.
    - **user_public_id**: The ID of the user public to update
    - **user_public**: The updated user public data
    """
    print("user_public", user_public)
    try:
        user_instance = UserPublic.from_create_schema(user_public)
        return update_record(db, current_user, user_instance)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/user-public/{user_public_id}", response_model=dict)
async def delete_user_public(
    user_public_id: uuid.UUID,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_super_user),  # noqa: ARG001
):
    """
    Delete a user public by ID.
    - **user_public_id**: The ID of the user public to delete
    """
    user_instance = get_record_by_id(session, UserBusiness, user_public_id)

    delete_record(session, user_instance)
    return {"message": f"UserPublic with ID {user_public_id} has been deleted."}
