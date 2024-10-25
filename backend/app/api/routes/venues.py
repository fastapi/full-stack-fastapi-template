from typing import List
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlmodel import Session
from app.models.venue import QSR, Foodcourt, Restaurant, Nightclub, Venue
from app.schema.venue import (
    FoodcourtCreate,
    QSRCreate,
    RestaurantCreate,
    NightclubCreate,
    FoodcourtRead,
    QSRRead,
    RestaurantRead,
    NightclubRead,
)
from app.api.deps import get_db  # Assuming you have a dependency to get the database session
from app.crud import (
    create_record,
    get_all_records,
)

app = FastAPI()
router = APIRouter()

# POST endpoint for Foodcourt
@router.post("/foodcourts/", response_model=FoodcourtRead)
def create_foodcourt(foodcourt: FoodcourtCreate, db: Session = Depends(get_db)):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(foodcourt.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        foodcourt_instance = Foodcourt.from_create_schema(venue_instance.id, foodcourt)
        # Create the new Foodcourt record in the database
        create_record(db, foodcourt_instance)
        # Return the read schema for the created foodcourt
        return foodcourt_instance.to_read_schema()
    
    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error

# GET endpoint for Foodcourt
@router.get("/foodcourts/", response_model=List[FoodcourtRead])
def read_foodcourts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, Foodcourt, skip=skip, limit=limit)

# POST endpoint for QSR
@router.post("/qsrs/", response_model=QSRRead)
def create_qsr(qsr: QSRCreate, db: Session = Depends(get_db)):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(qsr.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        qsr_instance = QSR.from_create_schema(venue_instance.id, qsr)
        # Create the new Foodcourt record in the database
        create_record(db, qsr_instance)
        # Return the read schema for the created foodcourt
        return qsr_instance.to_read_schema()
    
    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error

# GET endpoint for QSR
@router.get("/qsrs/", response_model=List[QSRRead])
def read_qsrs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, QSR, skip=skip, limit=limit)

# POST endpoint for Restaurant
@router.post("/restaurants/", response_model=RestaurantRead)
def create_restaurant(restaurant: RestaurantCreate, db: Session = Depends(get_db)):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(restaurant.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        restaurant_instance = Restaurant.from_create_schema(venue_instance.id, restaurant)
        # Create the new Foodcourt record in the database
        create_record(db, restaurant_instance)
        # Return the read schema for the created foodcourt
        return restaurant_instance.to_read_schema()
    
    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error

# GET endpoint for Restaurant
@router.get("/restaurants/", response_model=List[RestaurantRead])
def read_restaurants(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, Restaurant, skip=skip, limit=limit)

# POST endpoint for Nightclub
@router.post("/nightclubs/", response_model=NightclubRead)
def create_nightclub(nightclub: NightclubCreate, db: Session = Depends(get_db)):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(nightclub.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        nightclub_instance = Nightclub.from_create_schema(venue_instance.id, nightclub)
        # Create the new Foodcourt record in the database
        create_record(db, nightclub_instance)
        # Return the read schema for the created foodcourt
        return nightclub_instance.to_read_schema()
    
    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error

# GET endpoint for Nightclub
@router.get("/nightclubs/", response_model=List[NightclubRead])
def read_nightclubs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, Nightclub, skip=skip, limit=limit)

