from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from poetry.core.packages.package import Package
    from poetry.core.packages.project_package import ProjectPackage


class SolverResult:
    def __init__(
        self,
        root: ProjectPackage,
        packages: list[Package],
        attempted_solutions: int,
    ) -> None:
        self._root = root
        self._packages = packages
        self._attempted_solutions = attempted_solutions

    @property
    def packages(self) -> list[Package]:
        return self._packages

    @property
    def attempted_solutions(self) -> int:
        return self._attempted_solutions
