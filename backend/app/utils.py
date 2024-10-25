import re
from typing import Optional, List, Tuple
import unshortenit

class CoordinatesNotFoundError(Exception):
    """Custom exception raised when coordinates cannot be found in the Google Maps link."""
    pass

def extract_coordinates_from_full_link(link: str) -> Optional[Tuple[float, float]]:
    """
    Extracts latitude and longitude from a full Google Maps link.

    Args:
        link (str): The full Google Maps URL.

    Returns:
        Optional[Tuple[float, float]]: A tuple containing latitude and longitude, or None if not found.
    """
    lat_long_regex = r"@([-+]?\d*\.\d+),([-+]?\d*\.\d+)"
    match = re.search(lat_long_regex, link)
    
    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        return latitude, longitude
    
    return None

def get_coordinates_from_google_maps(link: str) -> Optional[List[Tuple[str, float, float]]]:
    """
    Retrieves latitude and longitude from a Google Maps link by unshortening it and extracting coordinates.

    Args:
        link (str): The Google Maps URL.

    Raises:
        CoordinatesNotFoundError: If coordinates are not found in the link.

    Returns:
        Optional[List[Tuple[str, float, float]]]: A list of tuples containing the link, latitude, and longitude,
        or raises an exception if coordinates are not found.
    """
    # Unshorten the URL if it's a shortened link
    unshortened_url = unshortenit.unshorten(link)

    # Attempt to extract coordinates from the full link
    coordinates = extract_coordinates_from_full_link(unshortened_url)
    if coordinates:
        latitude, longitude = coordinates
        return [(unshortened_url, latitude, longitude)]
    
    raise CoordinatesNotFoundError(f"No coordinates found in the provided link: {link}")