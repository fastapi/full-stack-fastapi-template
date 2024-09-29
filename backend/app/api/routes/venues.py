import uuid
from app.schema.venue import FoodcourtCreate, FoodcourtRead, NightclubCreate, NightclubRead, QSRCreate, QSRRead, RestaurantCreate, RestaurantRead
from app.models.user import UserBusiness, UserPublic
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Union

from app.models.venue import Nightclub, Restaurant, QSR, Foodcourt
from app.api.deps import SessionDep, get_current_user
from app.crud import (
    get_all_records,
    get_record_by_id,
    create_record,
    update_record,
    delete_record
)

router = APIRouter()

# CRUD operations for Nightclubs

@router.get("/nightclubs/", response_model=List[NightclubRead])
async def read_nightclubs(
    session: SessionDep,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100),
    current_user: Union[UserPublic, UserBusiness] = Depends(get_current_user)
):
    """
    Retrieve a paginated list of nightclubs.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    nightclubs = get_all_records(session, Nightclub, skip=skip, limit=limit)
    return nightclubs 

@router.get("/nightclubs/{venue_id}", response_model=NightclubRead)
async def read_nightclub(venue_id: uuid.UUID, session: SessionDep ):
    nightclub = get_record_by_id(session, Nightclub, venue_id)
    if not nightclub:
        raise HTTPException(status_code=404, detail="Nightclub not found")
    return nightclub

@router.post("/nightclubs/", response_model=NightclubRead)
async def create_nightclub(
    nightclub: NightclubCreate,
    session: SessionDep
):
    return create_record(session, Nightclub, nightclub)

@router.put("/nightclubs/{venue_id}", response_model=Nightclub)
async def update_nightclub(
    venue_id: uuid.UUID,
    updated_nightclub: NightclubCreate,
    session: SessionDep
    ):
    return update_record(session, Nightclub, venue_id, updated_nightclub)

@router.delete("/nightclubs/{venue_id}", response_model=None)
async def delete_nightclub(
    venue_id: uuid.UUID,
    session: SessionDep
    
):
    return delete_record(session, Nightclub, venue_id)

@router.get("/restaurants/", response_model=List[RestaurantRead])
async def read_restaurants(
    session: SessionDep,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100)
):
    """
    Retrieve a paginated list of restaurants.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    restaurants = get_all_records(session, Restaurant, skip=skip, limit=limit)
    return restaurants 

@router.get("/restaurants/{venue_id}", response_model=RestaurantRead)
async def read_restaurant(venue_id: uuid.UUID, session: SessionDep ):
    restaurant = get_record_by_id(session, Restaurant, venue_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="restaurant not found")
    return restaurant

@router.post("/restaurants/", response_model=RestaurantRead)
async def create_restaurant(
    restaurant: RestaurantCreate,
    session: SessionDep
):
    return create_record(session, Restaurant, restaurant)

@router.put("/restaurants/{venue_id}", response_model=Restaurant)
async def update_restaurant(
    venue_id: uuid.UUID,
    updated_restaurant: RestaurantCreate,
    session: SessionDep
    ):
    return update_record(session, Restaurant, venue_id, updated_restaurant)

@router.delete("/restaurants/{venue_id}", response_model=None)
async def delete_restaurant(
    venue_id: uuid.UUID,
    session: SessionDep
    
):
    return delete_record(session, Restaurant, venue_id)

@router.get("/qsrs/", response_model=List[QSRRead])
async def read_qsrs(
    session: SessionDep,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100)
):
    """
    Retrieve a paginated list of qsrs.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    qsrs = get_all_records(session, QSR, skip=skip, limit=limit)
    return qsrs 

@router.get("/qsrs/{venue_id}", response_model=QSRRead)
async def read_qsr(venue_id: uuid.UUID, session: SessionDep ):
    qsr = get_record_by_id(session, QSR, venue_id)
    if not qsr:
        raise HTTPException(status_code=404, detail="QSR not found")
    return qsr

@router.post("/qsrs/", response_model=QSRRead)
async def create_qsr(
    qsr: QSRCreate,
    session: SessionDep
):
    return create_record(session, QSR, qsr)

@router.put("/qsrs/{venue_id}", response_model=QSR)
async def update_qsr(
    venue_id: uuid.UUID,
    updated_qsr: QSRCreate,
    session: SessionDep
    ):
    return update_record(session, QSR, venue_id, updated_qsr)

@router.delete("/qsrs/{venue_id}", response_model=None)
async def delete_qsr(
    venue_id: uuid.UUID,
    session: SessionDep
    
):
    return delete_record(session, QSR, venue_id)

@router.get("/foodcourts/", response_model=List[FoodcourtRead])
async def read_foodcourts(
    session: SessionDep,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100)
):
    """
    Retrieve a paginated list of foodcourts.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    foodcourts = get_all_records(session, Foodcourt, skip=skip, limit=limit)
    return foodcourts 

@router.get("/foodcourts/{venue_id}", response_model=FoodcourtRead)
async def read_foodcourt(venue_id: uuid.UUID, session: SessionDep ):
    foodcourt = get_record_by_id(session, Foodcourt, venue_id)
    if not foodcourt:
        raise HTTPException(status_code=404, detail="foodcourt not found")
    return foodcourt

@router.post("/foodcourts/", response_model=FoodcourtRead)
async def create_foodcourt(
    foodcourt: FoodcourtCreate,
    session: SessionDep
):
    return create_record(session, Foodcourt, foodcourt)

@router.put("/foodcourts/{venue_id}", response_model=Foodcourt)
async def update_foodcourt(
    venue_id: uuid.UUID,
    updated_foodcourt: FoodcourtCreate,
    session: SessionDep
    ):
    return update_record(session, Foodcourt, venue_id, updated_foodcourt)

@router.delete("/foodcourts/{venue_id}", response_model=None)
async def delete_foodcourt(
    venue_id: uuid.UUID,
    session: SessionDep
    
):
    return delete_record(session, Foodcourt, venue_id)