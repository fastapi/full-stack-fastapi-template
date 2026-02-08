import statistics
from typing import Tuple, List as TypingList


def calculate_median(values: TypingList[float]) -> float:
    """Calculate median from list of values"""
    if not values:
        return 0.0
    return statistics.median(values)
