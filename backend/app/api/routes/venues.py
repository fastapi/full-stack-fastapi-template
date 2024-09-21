from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import List

from app.models.venue import Nightclub, Restaurant, QSR, Foodcourt
from app.api.deps import SessionDep
from app.crud import (
    get_all_records,
    get_record_by_id,
    create_record,
    update_record,
    delete_record
)

router = APIRouter()

# CRUD operations for Nightclubs

@router.get("/nightclubs/", response_model=List[Nightclub])
def read_nightclubs(
    session: SessionDep,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100)
):
    """
    Retrieve a paginated list of nightclubs.
    - **skip**: The page number (starting from 0)
    - **limit**: The number of items per page
    """
    return get_all_records(session, Nightclub, skip=skip, limit=limit)


@router.get("/nightclubs/{venue_id}", response_model=Nightclub)
def read_nightclub(venue_id: int, session: SessionDep ):
    nightclub = get_record_by_id(session, Nightclub, venue_id)
    if not nightclub:
        raise HTTPException(status_code=404, detail="Nightclub not found")
    return nightclub

@router.post("/nightclubs/", response_model=Nightclub)
def create_nightclub(
    nightclub: Nightclub,
    session: SessionDep
):
    return create_record(session, Nightclub, nightclub)

@router.put("/nightclubs/{venue_id}", response_model=Nightclub)
def update_nightclub(
    venue_id: int,
    updated_nightclub: Nightclub,
    session: SessionDep
    
):
    return update_record(session, Nightclub, venue_id, updated_nightclub)

@router.delete("/nightclubs/{venue_id}", response_model=None)
def delete_nightclub(
    venue_id: int,
    session: SessionDep
    
):
    return delete_record(session, Nightclub, venue_id)

# # CRUD operations for Restaurants

# @router.get("/restaurants/", response_model=List[Restaurant])
# def read_restaurants(session: SessionDep ):
#     return get_all_venues(session, Restaurant)

# @router.get("/restaurants/{venue_id}", response_model=Restaurant)
# def read_restaurant(venue_id: int, session: SessionDep ):
#     restaurant = get_venue_by_id(session, Restaurant, venue_id)
#     if not restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")
#     return restaurant

# @router.post("/restaurants/", response_model=Restaurant)
# def create_restaurant(
#     restaurant: Restaurant,
#     session: SessionDep
    
# ):
#     return create_venue(session, restaurant)

# @router.put("/restaurants/{venue_id}", response_model=Restaurant)
# def update_restaurant(
#     venue_id: int,
#     updated_restaurant: Restaurant,
#     session: SessionDep
    
# ):
#     existing_restaurant = get_venue_by_id(session, Restaurant, venue_id)
#     if not existing_restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")
#     return update_venue(session, venue_id, updated_restaurant)

# @router.delete("/restaurants/{venue_id}", response_model=Restaurant)
# def delete_restaurant(
#     venue_id: int,
#     session: SessionDep
    
# ):
#     existing_restaurant = get_venue_by_id(session, Restaurant, venue_id)
#     if not existing_restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")
#     return delete_venue(session, Restaurant, venue_id)

# # CRUD operations for QSRs

# @router.get("/qsrs/", response_model=List[QSR])
# def read_qsrs(session: SessionDep ):
#     return get_all_venues(session, QSR)

# @router.get("/qsrs/{venue_id}", response_model=QSR)
# def read_qsr(venue_id: int, session: SessionDep ):
#     qsr = get_venue_by_id(session, QSR, venue_id)
#     if not qsr:
#         raise HTTPException(status_code=404, detail="QSR not found")
#     return qsr

# @router.post("/qsrs/", response_model=QSR)
# def create_qsr(
#     qsr: QSR,
#     session: SessionDep
    
# ):
#     return create_venue(session, qsr)

# @router.put("/qsrs/{venue_id}", response_model=QSR)
# def update_qsr(
#     venue_id: int,
#     updated_qsr: QSR,
#     session: SessionDep
    
# ):
#     existing_qsr = get_venue_by_id(session, QSR, venue_id)
#     if not existing_qsr:
#         raise HTTPException(status_code=404, detail="QSR not found")
#     return update_venue(session, venue_id, updated_qsr)

# @router.delete("/qsrs/{venue_id}", response_model=QSR)
# def delete_qsr(
#     venue_id: int,
#     session: SessionDep
    
# ):
#     existing_qsr = get_venue_by_id(session, QSR, venue_id)
#     if not existing_qsr:
#         raise HTTPException(status_code=404, detail="QSR not found")
#     return delete_venue(session, QSR, venue_id)

# # CRUD operations for FoodCourts

# @router.get("/foodcourts/", response_model=List[Foodcourt])
# def read_foodcourts(session: SessionDep ):
#     return get_all_venues(session, Foodcourt)

# @router.get("/foodcourts/{venue_id}", response_model=Foodcourt)
# def read_foodcourt(venue_id: int, session: SessionDep ):
#     foodcourt = get_venue_by_id(session, Foodcourt, venue_id)
#     if not foodcourt:
#         raise HTTPException(status_code=404, detail="Foodcourt not found")
#     return foodcourt

# @router.post("/foodcourts/", response_model=Foodcourt)
# def create_foodcourt(
#     foodcourt: Foodcourt,
#     session: SessionDep
    
# ):
#     return create_venue(session, foodcourt)

# @router.put("/foodcourts/{venue_id}", response_model=Foodcourt)
# def update_foodcourt(
#     venue_id: int,
#     updated_foodcourt: Foodcourt,
#     session: SessionDep
    
# ):
#     existing_foodcourt = get_venue_by_id(session, Foodcourt, venue_id)
#     if not existing_foodcourt:
#         raise HTTPException(status_code=404, detail="Foodcourt not found")
#     return update_venue(session, venue_id, updated_foodcourt)

# @router.delete("/foodcourts/{venue_id}", response_model=Foodcourt)
# def delete_foodcourt(
#     venue_id: int,
#     session: SessionDep
    
# ):
#     existing_foodcourt = get_venue_by_id(session, Foodcourt, venue_id)
#     if not existing_foodcourt:
#         raise HTTPException(status_code=404, detail="Foodcourt not found")
#     return delete_venue(session, Foodcourt, venue_id)