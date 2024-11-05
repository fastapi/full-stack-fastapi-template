import requests
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schema.maps import (
    LocationByCoordinatesResponse,
    LocationDetailsResponse,
    SearchResponse,
)

router = APIRouter()
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
GOOGLE_REVERSE_GEOCODE_URL = settings.GOOGLE_REVERSE_GEOCODE_URL
GOOGLE_PLACES_URL = settings.GOOGLE_PLACES_URL
GOOGLE_PLACE_DETAILS_URL = settings.GOOGLE_PLACE_DETAILS_URL

@router.get("/search", response_model=SearchResponse)
def search_places(query: str, radius: float = 1000):
    params = {
        "query": query,
        "key": GOOGLE_API_KEY,
    }

    if radius:
        params["radius"] = radius

    response = requests.get(GOOGLE_PLACES_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error fetching data from Google Maps API",
        )

    data = response.json()

    results = [
        {
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "location": place.get("geometry", {}).get("location"),
            "place_id": place.get("place_id"),
        }
        for place in data.get("results", [])
    ]

    return {"results": results}


@router.get("/location-details", response_model=LocationDetailsResponse)
async def get_location_details(place_id: str):
    GOOGLE_PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "key": GOOGLE_API_KEY}

    response = requests.get(GOOGLE_PLACE_DETAILS_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch location details")

    details = response.json().get("result", {})

    location_details = {
        "name": details.get("name"),
        "address": details.get("formatted_address"),
        "phone_number": details.get("formatted_phone_number"),
        "location": details.get("geometry", {}).get("location"),
        "place_id": place_id,
        "url": details.get("url")
    }

    return location_details

@router.get("/location-by-coordinates", response_model=LocationByCoordinatesResponse)
async def get_location_by_coordinates(lat: float, lng: float):
    reverse_geocode_params = {"latlng": f"{lat},{lng}", "key": GOOGLE_API_KEY}

    reverse_response = requests.get(
        GOOGLE_REVERSE_GEOCODE_URL, params=reverse_geocode_params
    )

    if reverse_response.status_code != 200:
        raise HTTPException(
            status_code=500, detail="Failed to fetch place ID from coordinates"
        )

    results = reverse_response.json().get("results", [])

    if not results:
        raise HTTPException(
            status_code=404, detail="No location found for these coordinates"
        )

    place_id = results[0].get("place_id")
    name = results[0].get("formatted_address")

    return {
        "name": name,
        "place_id": place_id,
    }
