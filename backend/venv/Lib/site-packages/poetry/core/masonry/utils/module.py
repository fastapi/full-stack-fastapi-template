from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

    from poetry.core.masonry.utils.include import Include


class ModuleOrPackageNotFoundError(ValueError):
    pass


class Module:
    def __init__(
        self,
        name: str,
        directory: str = ".",
        packages: Sequence[Mapping[str, Any]] = (),
        includes: Sequence[Mapping[str, Any]] = (),
    ) -> None:
        from poetry.core.masonry.utils.include import Include
        from poetry.core.masonry.utils.package_include import PackageInclude
        from poetry.core.utils.helpers import module_name

        self._name = module_name(name)
        self._in_src = False
        self._is_package = False
        self._path = Path(directory)
        self._package_includes: list[PackageInclude] = []
        self._explicit_includes: list[Include] = []

        if not packages:
            # It must exist either as a .py file or a directory, but not both
            pkg_dir = Path(directory, self._name)
            py_file = Path(directory, self._name + ".py")
            default_package: dict[str, Any]
            if pkg_dir.is_dir() and py_file.is_file():
                raise ValueError(f"Both {pkg_dir} and {py_file} exist")
            elif pkg_dir.is_dir():
                default_package = {"include": str(pkg_dir.relative_to(self._path))}
            elif py_file.is_file():
                default_package = {"include": str(py_file.relative_to(self._path))}
            else:
                # Searching for a src module
                src = Path(directory, "src")
                src_pkg_dir = src / self._name
                src_py_file = src / (self._name + ".py")

                if src_pkg_dir.is_dir() and src_py_file.is_file():
                    raise ValueError(f"Both {pkg_dir} and {py_file} exist")
                elif src_pkg_dir.is_dir():
                    default_package = {
                        "include": str(src_pkg_dir.relative_to(src)),
                        "from": str(src.relative_to(self._path)),
                    }
                elif src_py_file.is_file():
                    default_package = {
                        "include": str(src_py_file.relative_to(src)),
                        "from": str(src.relative_to(self._path)),
                    }
                else:
                    raise ModuleOrPackageNotFoundError(
                        f"No file/folder found for package {name}"
                    )
            default_package["format"] = ["sdist", "wheel"]
            packages = [default_package]

        for package in packages:
            self._package_includes.append(
                PackageInclude(
                    self._path,
                    package["include"],
                    formats=package["format"],
                    source=package.get("from"),
                    target=package.get("to"),
                )
            )

        for include in includes:
            self._explicit_includes.append(
                Include(self._path, include["path"], formats=include["format"])
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def file(self) -> Path:
        if self._is_package:
            return self._path / "__init__.py"
        else:
            return self._path

    @property
    def includes(self) -> list[Include]:
        return [*self._package_includes, *self._explicit_includes]

    @property
    def explicit_includes(self) -> list[Include]:
        return self._explicit_includes

    def is_package(self) -> bool:
        return self._is_package

    def is_in_src(self) -> bool:
        return self._in_src
