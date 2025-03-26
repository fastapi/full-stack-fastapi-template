from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from crashtest.contracts.solution import Solution


class HasSolutionsForException:
    def can_solve(self, exception: Exception) -> bool:
        raise NotImplementedError()

    def get_solutions(self, exception: Exception) -> list[Solution]:
        raise NotImplementedError()
