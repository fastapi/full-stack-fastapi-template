from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from poetry.core.packages.dependency import Dependency
    from poetry.core.packages.package import Package

    from poetry.mixology.failure import SolveFailureError


class SolverProblemError(Exception):
    def __init__(self, error: SolveFailureError) -> None:
        self._error = error

        super().__init__(str(error))

    @property
    def error(self) -> SolveFailureError:
        return self._error


class OverrideNeededError(Exception):
    def __init__(self, *overrides: dict[Package, dict[str, Dependency]]) -> None:
        self._overrides = overrides

    @property
    def overrides(self) -> tuple[dict[Package, dict[str, Dependency]], ...]:
        return self._overrides
