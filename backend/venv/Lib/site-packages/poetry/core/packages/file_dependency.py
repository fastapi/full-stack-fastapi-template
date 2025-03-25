from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.core.packages.path_dependency import PathDependency


if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class FileDependency(PathDependency):
    def __init__(
        self,
        name: str,
        path: Path,
        *,
        directory: str | None = None,
        groups: Iterable[str] | None = None,
        optional: bool = False,
        base: Path | None = None,
        extras: Iterable[str] | None = None,
    ) -> None:
        super().__init__(
            name,
            path,
            source_type="file",
            groups=groups,
            optional=optional,
            base=base,
            subdirectory=directory,
            extras=extras,
        )
        # Attributes must be immutable for clone() to be safe!
        # (For performance reasons, clone only creates a copy instead of a deep copy).

    @property
    def directory(self) -> str | None:
        return self.source_subdirectory

    @property
    def base_pep_508_name(self) -> str:
        requirement = super().base_pep_508_name

        if self.directory:
            requirement += f"#subdirectory={self.directory}"

        return requirement

    def _validate(self) -> str:
        message = super()._validate()
        if message:
            return message

        if self._full_path.is_dir():
            return (
                f"{self._full_path} for {self.pretty_name} is a directory,"
                " expected a file"
            )
        return ""
