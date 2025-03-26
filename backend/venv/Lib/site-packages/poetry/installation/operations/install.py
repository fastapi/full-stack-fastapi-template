from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.installation.operations.operation import Operation


if TYPE_CHECKING:
    from poetry.core.packages.package import Package


class Install(Operation):
    def __init__(
        self, package: Package, reason: str | None = None, priority: int = 0
    ) -> None:
        super().__init__(reason, priority=priority)

        self._package = package

    @property
    def package(self) -> Package:
        return self._package

    @property
    def job_type(self) -> str:
        return "install"

    def __str__(self) -> str:
        return (
            "Installing"
            f" {self.package.pretty_name} ({self.format_version(self.package)})"
        )

    def __repr__(self) -> str:
        return (
            "<Install"
            f" {self.package.pretty_name} ({self.format_version(self.package)})>"
        )
