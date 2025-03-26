from __future__ import annotations

from crashtest.contracts.solution import Solution


class BaseSolution(Solution):
    def __init__(self, title: str = "", description: str = "") -> None:
        self._title = title
        self._description = description
        self._links: list[str] = []

    @property
    def solution_title(self) -> str:
        return self._title

    @property
    def solution_description(self) -> str:
        return self._description

    @property
    def documentation_links(self) -> list[str]:
        return self._links
