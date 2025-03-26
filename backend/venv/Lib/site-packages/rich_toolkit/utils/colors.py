from rich.color import Color
from rich.color_triplet import ColorTriplet


def lighten(color: Color, amount: float) -> Color:
    assert color.triplet

    r, g, b = color.triplet

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return Color.from_triplet(ColorTriplet(r, g, b))
