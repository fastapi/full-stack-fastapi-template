from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path


class Include:
    """
    Represents an "include" entry.

    It can be a glob string, a single file or a directory.

    This class will then detect the type of this include:

        - a package
        - a module
        - a file
        - a directory
    """

    def __init__(self, base: Path, include: str, formats: list[str]) -> None:
        self._base = base
        self._include = str(include)
        self._formats = formats

        self._elements: list[Path] = sorted(self._base.glob(str(self._include)))

    @property
    def base(self) -> Path:
        return self._base

    @property
    def elements(self) -> list[Path]:
        return self._elements

    @property
    def formats(self) -> list[str]:
        return self._formats

    def is_empty(self) -> bool:
        return len(self._elements) == 0

    def refresh(self) -> Include:
        self._elements = sorted(self._base.glob(self._include))

        return self
