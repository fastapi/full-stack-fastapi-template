from __future__ import annotations

import math

from dataclasses import dataclass
from html.parser import HTMLParser

from rapidfuzz.distance import Levenshtein


class TagStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)

        self.reset()
        self.fed: list[str] = []

    def handle_data(self, d: str) -> None:
        self.fed.append(d)

    def handle_entityref(self, name: str) -> None:
        self.fed.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.fed.append(f"&#{name};")

    def get_data(self) -> str:
        return "".join(self.fed)


def _strip(value: str) -> str:
    s = TagStripper()
    s.feed(value)
    s.close()

    return s.get_data()


def strip_tags(value: str) -> str:
    while "<" in value and ">" in value:
        new_value = _strip(value)
        if value.count("<") == new_value.count("<"):
            break

        value = new_value

    return value


def find_similar_names(name: str, names: list[str]) -> list[str]:
    """
    Finds names similar to a given command name.
    """
    threshold = 1e3
    distance_by_name = {}

    for actual_name in names:
        # Get Levenshtein distance between the input and each command name
        distance = Levenshtein.distance(name, actual_name)

        is_similar = distance <= len(name) / 3
        substring_index = actual_name.find(name)
        is_substring = substring_index != -1

        if is_similar or is_substring:
            distance_by_name[actual_name] = (
                distance,
                substring_index if is_substring else float("inf"),
            )

    # Only keep results with a distance below the threshold
    distance_by_name = {
        key: value
        for key, value in distance_by_name.items()
        if value[0] < 2 * threshold
    }
    # Display results with shortest distance first
    return sorted(distance_by_name, key=lambda key: distance_by_name[key])


@dataclass
class TimeFormat:
    threshold: int
    alias: str
    divisor: int | None = None

    def apply(self, secs: float) -> str:
        if self.divisor:
            return f"{math.ceil(secs / self.divisor)} {self.alias}"
        return self.alias


_TIME_FORMATS: list[TimeFormat] = [
    TimeFormat(1, "< 1 sec"),
    TimeFormat(2, "1 sec"),
    TimeFormat(60, "secs", 1),
    TimeFormat(61, "1 min"),
    TimeFormat(3600, "mins", 60),
    TimeFormat(5401, "1 hr"),
    TimeFormat(86400, "hrs", 3600),
    TimeFormat(129601, "1 day"),
    TimeFormat(604801, "days", 86400),
]


def format_time(secs: float) -> str:
    time_format = next(
        (fmt for fmt in _TIME_FORMATS if secs < fmt.threshold), _TIME_FORMATS[-1]
    )
    return time_format.apply(secs)
