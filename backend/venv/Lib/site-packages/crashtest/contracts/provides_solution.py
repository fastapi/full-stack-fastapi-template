from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from crashtest.contracts.solution import Solution


class ProvidesSolution:
    @property
    def solution(self) -> Solution:
        raise NotImplementedError()
