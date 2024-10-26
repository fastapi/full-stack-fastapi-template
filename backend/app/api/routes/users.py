from typing import List, Union
import uuid
from fastapi import APIRouter, Query, HTTPException, Depends
from app.api.deps import SessionDep, get_business_user, get_current_user, get_public_user, get_super_user
from app.models import UserBusiness, UserPublic
from app.util import get_all_records, get_record_by_id, create_record, update_record, delete_record, patch_record

router = APIRouter()

@router.get("/user-businesses/", response_model=List[UserBusiness])
async def read_user_businesses(
    session: SessionDep,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100),
    current_user: UserBusiness = Depends(get_super_user)
):
    """
    Retrieve a paginated list of user businesses.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    return get_all_records(session, UserBusiness, skip=skip, limit=limit)

@router.get("/user-businesses/{user_business_id}", response_model=UserBusiness)
async def read_user_business(
    user_business_id: uuid.UUID,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_super_user)
):
    """
    Retrieve a single user business by ID.
    - **user_business_id**: The ID of the user business to retrieve
    """
    return get_record_by_id(session, UserBusiness, user_business_id)

@router.get("/me/user-businesses/{user_business_id}", response_model=UserBusiness)
async def read_user_business_me(
    session: SessionDep,
    current_user: UserBusiness = Depends(get_super_user)
):
    """
    Retrieve a single user business by ID.
    - **user_business_id**: The ID of the user business to retrieve
    """
    return get_record_by_id(session, UserBusiness, current_user.id)


@router.post("/user-businesses/", response_model=UserBusiness)
async def create_user_business(
    user_business: UserBusiness,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_super_user)
):
    """
    Create a new user business.
    - **user_business**: The user business data to create
    """
    return create_record(session, UserBusiness, user_business)

@router.put("/user-businesses/{user_business_id}", response_model=UserBusiness)
async def update_user_business(
    user_business: UserBusiness,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_current_user)
):
    """
    Update an existing user business.
    - **user_business_id**: The ID of the user business to update
    - **user_business**: The updated user business data
    """
    return update_record(session, UserBusiness, current_user.id, user_business)

@router.delete("/user-businesses/{user_business_id}", response_model=UserBusiness)
async def delete_user_business(
    user_business_id: uuid.UUID,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_super_user)
):
    """
    Delete a user business by ID.
    - **user_business_id**: The ID of the user business to delete
    """
    delete_record(session, UserBusiness, user_business_id)
    return {"message": f"UserBusiness with ID {user_business_id} has been deleted."}

@router.get("/user-public/", response_model=List[UserPublic])
async def read_user_public(
    session: SessionDep,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100),
    current_user: UserBusiness = Depends(get_business_user)
):
    """
    Retrieve a paginated list of user public.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    return get_all_records(session, UserPublic, skip=skip, limit=limit)

@router.get("/user-public/{user_public_id}", response_model=UserPublic)
async def read_user_public(
    user_public_id: uuid.UUID,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_business_user)
):
    """
    Retrieve a single user public by ID.
    - **user_public_id**: The ID of the user public to retrieve
    """
    return get_record_by_id(session, UserPublic, user_public_id)

@router.get("/me/user-public/", response_model=UserPublic)
async def read_user_public_me(
    session: SessionDep,
    current_user: UserPublic = Depends(get_public_user)
):
    print("current_user  : ",current_user)
    """
    Retrieve a single user public by ID.
    - **user_public_id**: The ID of the user public to retrieve
    """
    return get_record_by_id(session, UserPublic, current_user.id)

@router.put("/me/user-public/", response_model=UserPublic)
async def update_user_public_me(
    user_public: UserPublic,
    session: SessionDep,
    current_user: UserPublic = Depends(get_public_user)
):
    """
    Update an existing user public.
    - **user_public_id**: The ID of the user public to update
    - **user_public**: The updated user public data
    """
    return update_record(session, UserPublic, current_user.id , user_public)

@router.delete("/user-public/{user_public_id}", response_model=UserPublic)
async def delete_user_public(
    user_public_id: uuid.UUID,
    session: SessionDep,
    current_user: UserBusiness = Depends(get_super_user)
):
    """
    Delete a user public by ID.
    - **user_public_id**: The ID of the user public to delete
    """
    delete_record(session, UserPublic, user_public_id)
    return {"message": f"UserPublic with ID {user_public_id} has been deleted."}