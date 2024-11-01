from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlmodel import Session

from app.api.deps import (
    get_business_user,
    get_db,
)
from app.models.user import UserBusiness, UserVenueAssociation
from app.models.venue import QSR, Foodcourt, Nightclub, Restaurant, Venue
from app.schema.venue import (
    FoodcourtCreate,
    FoodcourtRead,
    NightclubCreate,
    NightclubRead,
    QSRCreate,
    QSRRead,
    RestaurantCreate,
    RestaurantRead,
    VenueListResponse,
)

# Assuming you have a dependency to get the database session
from app.util import (
    create_record,
    get_all_records,
)

app = FastAPI()
router = APIRouter()


# POST endpoint for Foodcourt
@router.post("/foodcourts/", response_model=FoodcourtRead)
def create_foodcourt(
    foodcourt: FoodcourtCreate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_business_user),
):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(foodcourt.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        foodcourt_instance = Foodcourt.from_create_schema(venue_instance.id, foodcourt)
        # Create the new Foodcourt record in the database
        create_record(db, foodcourt_instance)
        association = UserVenueAssociation(
            user_id=current_user.id, venue_id=venue_instance.id
        )
        create_record(db, association)

        return foodcourt_instance.to_read_schema()

    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error


# GET endpoint for Foodcourt
@router.get("/foodcourts/", response_model=list[FoodcourtRead])
def read_foodcourts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, Foodcourt, skip=skip, limit=limit)


# POST endpoint for QSR
@router.post("/qsrs/", response_model=QSRRead)
def create_qsr(
    qsr: QSRCreate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_business_user),
):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(qsr.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        qsr_instance = QSR.from_create_schema(venue_instance.id, qsr)
        # Create the new Foodcourt record in the database
        create_record(db, qsr_instance)
        association = UserVenueAssociation(
            user_id=current_user.id, venue_id=venue_instance.id
        )
        create_record(db, association)
        return qsr_instance.to_read_schema()

    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error


# GET endpoint for QSR
@router.get("/qsrs/", response_model=list[QSRRead])
def read_qsrs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, QSR, skip=skip, limit=limit)


# POST endpoint for Restaurant
@router.post("/restaurants/", response_model=RestaurantRead)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_business_user),
):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(restaurant.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        restaurant_instance = Restaurant.from_create_schema(
            venue_instance.id, restaurant
        )
        # Create the new Foodcourt record in the database
        create_record(db, restaurant_instance)
        association = UserVenueAssociation(
            user_id=current_user.id, venue_id=venue_instance.id
        )
        create_record(db, association)
        return restaurant_instance.to_read_schema()

    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error


# GET endpoint for Restaurant
@router.get("/restaurants/", response_model=list[RestaurantRead])
def read_restaurants(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, Restaurant, skip=skip, limit=limit)


# POST endpoint for Nightclub
@router.post("/nightclubs/", response_model=NightclubRead)
def create_nightclub(
    nightclub: NightclubCreate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_business_user),
):
    try:
        # Check if the venue exists
        venue_instance = Venue.from_create_schema(nightclub.venue)
        create_record(db, venue_instance)  # Persist the new venue
        # Use the newly created venue instance
        nightclub_instance = Nightclub.from_create_schema(venue_instance.id, nightclub)
        # Create the new Foodcourt record in the database
        create_record(db, nightclub_instance)
        association = UserVenueAssociation(
            user_id=current_user.id, venue_id=venue_instance.id
        )
        create_record(db, association)
        return nightclub_instance.to_read_schema()

    except Exception as e:
        # Rollback the session in case of any error
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))  # Respond with a 500 error


# GET endpoint for Nightclub
@router.get("/nightclubs/", response_model=list[NightclubRead])
def read_nightclubs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_records(db, Nightclub, skip=skip, limit=limit)


@router.get("/my-venues/", response_model=VenueListResponse)
async def get_my_venues(
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_business_user),
):
    """
    Retrieve the venues managed by the current user, organized by venue type.

    This method leverages SQLAlchemy's efficient querying capabilities to minimize database load
    while ensuring data integrity through the association table, UserVenueAssociation.
    """

    # Fetch all venues managed by the current user
    managed_venues = (
        db.query(Venue)
        .join(UserVenueAssociation)
        .filter(UserVenueAssociation.user_id == current_user.id)
        .all()
    )

    # Create a set for fast membership testing
    managed_venue_ids = {venue.id for venue in managed_venues}

    # Initialize lists for categorized venues
    nightclubs, qsrs, foodcourts, restaurants = [], [], [], []

    # Efficiently query and convert Nightclubs
    for nightclub in (
        db.query(Nightclub).filter(Nightclub.venue_id.in_(managed_venue_ids)).all()
    ):
        nightclubs.append(nightclub.to_read_schema())

    # Efficiently query and convert QSRs
    for qsr in db.query(QSR).filter(QSR.venue_id.in_(managed_venue_ids)).all():
        qsrs.append(qsr.to_read_schema())

    # Efficiently query and convert Foodcourts
    for foodcourt in (
        db.query(Foodcourt).filter(Foodcourt.venue_id.in_(managed_venue_ids)).all()
    ):
        foodcourts.append(foodcourt.to_read_schema())

    # Efficiently query and convert Restaurants
    for restaurant in (
        db.query(Restaurant).filter(Restaurant.venue_id.in_(managed_venue_ids)).all()
    ):
        restaurants.append(restaurant.to_read_schema())

    # Construct and return the response
    return VenueListResponse(
        nightclubs=nightclubs, qsrs=qsrs, foodcourts=foodcourts, restaurants=restaurants
    )
