import h3

def get_h3_index(latitude: float, longitude: float, resolution: int = 9) -> str:
    return h3.geo_to_h3(latitude, longitude, resolution)

def is_within_radius(user_h3_index: str, poster_h3_index: str, radius: int) -> bool:
    return h3.h3_distance(user_h3_index, poster_h3_index) <= radius
