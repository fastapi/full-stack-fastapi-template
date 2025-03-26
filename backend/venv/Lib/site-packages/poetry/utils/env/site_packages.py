from __future__ import annotations

import contextlib
import itertools

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import overload

from poetry.utils._compat import metadata
from poetry.utils.helpers import is_dir_writable
from poetry.utils.helpers import paths_csv
from poetry.utils.helpers import remove_directory


if TYPE_CHECKING:
    from collections.abc import Iterable


class SitePackages:
    def __init__(
        self,
        purelib: Path,
        platlib: Path | None = None,
        fallbacks: list[Path] | None = None,
    ) -> None:
        self._purelib = purelib
        self._platlib = platlib or purelib

        if platlib and platlib.resolve() == purelib.resolve():
            self._platlib = purelib

        self._fallbacks = fallbacks or []

        self._candidates: list[Path] = []
        for path in itertools.chain([self._purelib, self._platlib], self._fallbacks):
            if path not in self._candidates:
                self._candidates.append(path)

        self._writable_candidates: list[Path] | None = None

    @property
    def path(self) -> Path:
        return self._purelib

    @property
    def purelib(self) -> Path:
        return self._purelib

    @property
    def platlib(self) -> Path:
        return self._platlib

    @property
    def candidates(self) -> list[Path]:
        return self._candidates

    @property
    def writable_candidates(self) -> list[Path]:
        if self._writable_candidates is not None:
            return self._writable_candidates

        self._writable_candidates = []
        for candidate in self._candidates:
            if not is_dir_writable(path=candidate, create=True):
                continue
            self._writable_candidates.append(candidate)

        return self._writable_candidates

    def make_candidates(
        self, path: Path, writable_only: bool = False, strict: bool = False
    ) -> list[Path]:
        candidates = self._candidates if not writable_only else self.writable_candidates
        if path.is_absolute():
            for candidate in candidates:
                with contextlib.suppress(ValueError):
                    path.relative_to(candidate)
                    return [path]
            site_type = "writable " if writable_only else ""
            raise ValueError(
                f"{path} is not relative to any discovered {site_type}sites"
            )

        results = [candidate / path for candidate in candidates]

        if not results and strict:
            raise RuntimeError(
                f'Unable to find a suitable destination for "{path}" in'
                f" {paths_csv(self._candidates)}"
            )

        return results

    def distributions(
        self, name: str | None = None, writable_only: bool = False
    ) -> Iterable[metadata.Distribution]:
        path = list(
            map(
                str, self._candidates if not writable_only else self.writable_candidates
            )
        )

        yield from metadata.PathDistribution.discover(name=name, path=path)

    def find_distribution(
        self, name: str, writable_only: bool = False
    ) -> metadata.Distribution | None:
        for distribution in self.distributions(name=name, writable_only=writable_only):
            return distribution
        return None

    def find_distribution_files_with_name(
        self, distribution_name: str, name: str, writable_only: bool = False
    ) -> Iterable[Path]:
        for distribution in self.distributions(
            name=distribution_name, writable_only=writable_only
        ):
            files = [] if distribution.files is None else distribution.files
            for file in files:
                if file.name == name:
                    path = distribution.locate_file(file)
                    assert isinstance(path, Path)
                    yield path

    def find_distribution_direct_url_json_files(
        self, distribution_name: str, writable_only: bool = False
    ) -> Iterable[Path]:
        return self.find_distribution_files_with_name(
            distribution_name=distribution_name,
            name="direct_url.json",
            writable_only=writable_only,
        )

    def remove_distribution_files(self, distribution_name: str) -> list[Path]:
        paths = []

        for distribution in self.distributions(
            name=distribution_name, writable_only=True
        ):
            files = [] if distribution.files is None else distribution.files
            for file in files:
                path = distribution.locate_file(file)
                assert isinstance(path, Path)
                path.unlink(missing_ok=True)

            distribution_path: Path = distribution._path  # type: ignore[attr-defined]
            if distribution_path.exists():
                remove_directory(distribution_path, force=True)

            paths.append(distribution_path)

        return paths

    @overload
    def _path_method_wrapper(
        self,
        path: Path,
        method: str,
        *args: Any,
        return_first: Literal[False],
        writable_only: bool = False,
        **kwargs: Any,
    ) -> list[tuple[Path, Any]]: ...

    @overload
    def _path_method_wrapper(
        self,
        path: Path,
        method: str,
        *args: Any,
        return_first: bool = True,
        writable_only: bool = False,
        **kwargs: Any,
    ) -> tuple[Path, Any]: ...

    def _path_method_wrapper(
        self,
        path: Path,
        method: str,
        *args: Any,
        return_first: bool = True,
        writable_only: bool = False,
        **kwargs: Any,
    ) -> tuple[Path, Any] | list[tuple[Path, Any]]:
        candidates = self.make_candidates(
            path, writable_only=writable_only, strict=True
        )

        results = []

        for candidate in candidates:
            with contextlib.suppress(OSError):
                result = candidate, getattr(candidate, method)(*args, **kwargs)
                if return_first:
                    return result
                results.append(result)

        if results:
            return results

        raise OSError(f"Unable to access any of {paths_csv(candidates)}")

    def write_text(self, path: Path, *args: Any, **kwargs: Any) -> Path:
        paths: tuple[Path, Any] = self._path_method_wrapper(
            path, "write_text", *args, **kwargs
        )
        return paths[0]

    def mkdir(self, path: Path, *args: Any, **kwargs: Any) -> Path:
        paths: tuple[Path, Any] = self._path_method_wrapper(
            path, "mkdir", *args, **kwargs
        )
        return paths[0]

    def exists(self, path: Path) -> bool:
        return any(
            value[-1]
            for value in self._path_method_wrapper(path, "exists", return_first=False)
        )

    def find(
        self,
        path: Path,
        writable_only: bool = False,
    ) -> list[Path]:
        return [
            value[0]
            for value in self._path_method_wrapper(
                path, "exists", return_first=False, writable_only=writable_only
            )
            if value[-1] is True
        ]
