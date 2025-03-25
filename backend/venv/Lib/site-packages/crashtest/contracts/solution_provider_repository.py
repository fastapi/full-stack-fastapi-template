from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from crashtest.contracts.solution import Solution


class SolutionProviderRepository:
    def register_solution_provider(
        self, solution_provider_class: type
    ) -> SolutionProviderRepository:
        raise NotImplementedError()

    def register_solution_providers(
        self, solution_provider_classes: list[type]
    ) -> SolutionProviderRepository:
        raise NotImplementedError()

    def get_solutions_for_exception(self, exception: Exception) -> list[Solution]:
        raise NotImplementedError()
