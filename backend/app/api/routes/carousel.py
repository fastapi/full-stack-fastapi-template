from datetime import datetime

import h3
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import SessionDep, get_business_user, get_current_user, get_db
from app.models.carousel_poster import CarouselPoster
from app.models.event import Event
from app.models.user import UserBusiness, UserPublic
from app.models.venue import Venue
from app.schema.carousel_poster import CarouselPosterCreate, CarouselPosterRead
from app.util import check_user_permission, create_record, get_record_by_id
from app.utils import get_h3_index

router = APIRouter()


@router.get("/poster/", response_model=list[CarouselPosterRead])
async def get_carousel_posters(
    latitude: float,
    longitude: float,
    session: SessionDep,
    radius: int = 3000,
    current_user: UserPublic = Depends(get_current_user),  # noqa: ARG001
):
    user_h3_index = get_h3_index(latitude=latitude, longitude=longitude)

    distance_in_km = radius / 1000
    k_ring_size = int(distance_in_km / 1.2)

    nearby_h3_indexes = h3.k_ring(user_h3_index, k_ring_size)

    posters = (
        session.execute(
            select(CarouselPoster)
            .where(CarouselPoster.h3_index.in_(nearby_h3_indexes))
            .where(CarouselPoster.expires_at > datetime.now())
        )
        .scalars()
        .all()
    )

    return [poster.to_read_schema() for poster in posters]


@router.post("/poster/", response_model=CarouselPosterRead)
async def create_carousel_poster(
    poster: CarouselPosterCreate,
    db: Session = Depends(get_db),
    current_user: UserBusiness = Depends(get_business_user),
):
    print("Creating carousel poster,   poster: ", poster)
    poster_instance = CarouselPoster.from_create_schema(poster)
    print("Creating carousel poster,   poster_instance: ", poster_instance)
    venue = None
    if poster_instance.venue_id:
        print("Creating carousel poster,   venue_id: ", poster_instance.venue_id)
        try:
            venue = get_record_by_id(db, Venue, poster_instance.venue_id)
        except Exception:
            raise HTTPException(status_code=404, detail="Venue not found")
        print("Creating carousel poster,   venue: ", venue)
    elif poster_instance.event_id:
        try:
            event = db.get(poster_instance.event_id, Event)
        except Exception:
            raise HTTPException(status_code=404, detail="Event not found")
        venue = event.venue
    else:
        raise ValueError("Either event_id or venue_id must be provided")

    check_user_permission(db, current_user, venue.id)

    h3_index = get_h3_index(
        latitude=venue.latitude, longitude=venue.longitude, resolution=9
    )

    poster_instance.h3_index = h3_index

    created_poster = create_record(db, poster_instance)

    assert isinstance(
        created_poster, CarouselPoster
    ), "The returned object is not of type CarouselPoster"

    x =  created_poster.to_read_schema()
    return x


# @router.put("/poster/{poster_id}", response_model=CarouselPosterRead)
# async def update_carousel_poster(
#     poster_id: uuid.UUID, updated_data: CarouselPosterCreate, session: SessionDep
# ):
#     return update_record(
#         session=session, record_id=poster_id, obj_in=updated_data, model=CarouselPoster
#     )


# @router.delete("/poster/{poster_id}")
# async def delete_carousel_poster(poster_id: uuid.UUID, session: SessionDep):
#     return delete_record(session=session, model=CarouselPoster, record_id=poster_id)
