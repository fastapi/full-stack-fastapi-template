from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from poetry.core.packages.package import Package
    from typing_extensions import Self


class Operation(ABC):
    def __init__(self, reason: str | None = None, priority: float = 0) -> None:
        self._reason = reason

        self._skipped = False
        self._skip_reason: str | None = None
        self._priority = priority

    @property
    @abstractmethod
    def job_type(self) -> str: ...

    @property
    def reason(self) -> str | None:
        return self._reason

    @property
    def skipped(self) -> bool:
        return self._skipped

    @property
    def skip_reason(self) -> str | None:
        return self._skip_reason

    @property
    def priority(self) -> float:
        return self._priority

    @property
    @abstractmethod
    def package(self) -> Package: ...

    def format_version(self, package: Package) -> str:
        version: str = package.full_pretty_version
        return version

    def skip(self, reason: str) -> Self:
        self._skipped = True
        self._skip_reason = reason

        return self
