from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.mixology.version_solver import VersionSolver


if TYPE_CHECKING:
    from poetry.core.packages.project_package import ProjectPackage

    from poetry.mixology.result import SolverResult
    from poetry.puzzle.provider import Provider


def resolve_version(root: ProjectPackage, provider: Provider) -> SolverResult:
    solver = VersionSolver(root, provider)

    return solver.solve()
