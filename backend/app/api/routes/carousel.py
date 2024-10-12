import uuid
import h3
from fastapi import APIRouter, Depends, Path
from sqlmodel import select
from typing import List
from datetime import datetime, timezone
from app.models.carousel_poster import CarouselPoster
from app.schema.carousel_poster import CarouselPosterCreate, CarouselPosterRead
from app.api.deps import SessionDep
from app.utils import get_h3_index
from app.crud import create_record, delete_record, update_record

router = APIRouter()

@router.get("/poster/", response_model=List[CarouselPoster])
async def get_carousel_posters(latitude: float, longitude: float, session: SessionDep, radius: int = 3000):
    user_h3_index = get_h3_index(latitude=latitude, longitude=longitude)

    distance_in_km = radius / 1000  
    k_ring_size = int(distance_in_km / 1.2)

    nearby_h3_indexes = h3.k_ring(user_h3_index, k_ring_size)

    posters = session.execute(
        select(CarouselPoster)
        .where(CarouselPoster.h3_index.in_(nearby_h3_indexes))  
        # .where(CarouselPoster.expires_at > current_time)   
    ).scalars().all()

    return posters

@router.post("/poster/", response_model=CarouselPosterRead)
async def create_carousel_poster(poster: CarouselPosterCreate, session: SessionDep):
    h3_index = get_h3_index(latitude=poster.latitude, longitude=poster.longitude, resolution=9)
    carousel_poster_obj = CarouselPoster(
        **poster.model_dump(),  
        h3_index=h3_index 
    )

    return create_record(session=session, model=CarouselPoster, obj_in=carousel_poster_obj)


@router.put("/poster/{poster_id}", response_model=CarouselPosterRead)
async def update_carousel_poster(
    poster_id: uuid.UUID,
    updated_data: CarouselPosterCreate,
    session: SessionDep
):
    return update_record(session=session, record_id=poster_id, obj_in=updated_data, model=CarouselPoster)


@router.delete("/poster/{poster_id}")
async def delete_carousel_poster(poster_id: uuid.UUID, session: SessionDep):
    return delete_record(session=session, model=CarouselPoster, record_id=poster_id)