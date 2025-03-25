from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.installation.operations.operation import Operation


if TYPE_CHECKING:
    from poetry.core.packages.package import Package


class Update(Operation):
    def __init__(
        self,
        initial: Package,
        target: Package,
        reason: str | None = None,
        priority: int = 0,
    ) -> None:
        self._initial_package = initial
        self._target_package = target

        super().__init__(reason, priority=priority)

    @property
    def initial_package(self) -> Package:
        return self._initial_package

    @property
    def target_package(self) -> Package:
        return self._target_package

    @property
    def package(self) -> Package:
        return self._target_package

    @property
    def job_type(self) -> str:
        return "update"

    def __str__(self) -> str:
        init_version = self.format_version(self.initial_package)
        target_version = self.format_version(self.target_package)
        return (
            f"Updating {self.initial_package.pretty_name} ({init_version}) "
            f"to {self.target_package.pretty_name} ({target_version})"
        )

    def __repr__(self) -> str:
        init_version = self.format_version(self.initial_package)
        target_version = self.format_version(self.target_package)
        return (
            f"<Update {self.initial_package.pretty_name} ({init_version}) "
            f"to {self.target_package.pretty_name} ({target_version})>"
        )
