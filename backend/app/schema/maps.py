from typing import Optional

from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lng: float


class Place(BaseModel):
    name: Optional[str]
    address: Optional[str]
    location: Optional[Location]
    place_id: Optional[str]


class SearchResponse(BaseModel):
    results: list[Place]


class LocationDetailsResponse(BaseModel):
    name: Optional[str]
    address: Optional[str]
    phone_number: Optional[str]
    location: Optional[Location]
    place_id: Optional[str]
    url: Optional[str]


class LocationByCoordinatesResponse(BaseModel):
    name: Optional[str]
    place_id: Optional[str]
