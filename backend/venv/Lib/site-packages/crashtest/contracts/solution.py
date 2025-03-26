from __future__ import annotations


class Solution:
    @property
    def solution_title(self) -> str:
        raise NotImplementedError()

    @property
    def solution_description(self) -> str:
        raise NotImplementedError()

    @property
    def documentation_links(self) -> list[str]:
        raise NotImplementedError()
