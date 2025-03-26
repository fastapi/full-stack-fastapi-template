from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING
from typing import Any

from poetry.core.pyproject.tables import BuildSystem
from poetry.core.utils._compat import tomllib


if TYPE_CHECKING:
    from pathlib import Path


class PyProjectTOML:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, Any] | None = None
        self._build_system: BuildSystem | None = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def data(self) -> dict[str, Any]:
        if self._data is None:
            if not self.path.exists():
                self._data = {}
            else:
                try:
                    with self.path.open("rb") as f:
                        self._data = tomllib.load(f)
                except tomllib.TOMLDecodeError as e:
                    from poetry.core.pyproject.exceptions import PyProjectError

                    msg = (
                        f"{self._path.as_posix()} is not a valid TOML file.\n"
                        f"{e.__class__.__name__}: {e}"
                    )

                    if str(e).startswith("Cannot overwrite a value"):
                        msg += "\nThis is often caused by a duplicate entry."

                    raise PyProjectError(msg) from e

        return self._data

    @property
    def build_system(self) -> BuildSystem:
        if self._build_system is None:
            build_backend = None
            requires = None

            if not self.path.exists():
                build_backend = "poetry.core.masonry.api"
                requires = ["poetry-core"]

            container = self.data.get("build-system", {})
            self._build_system = BuildSystem(
                build_backend=container.get("build-backend", build_backend),
                requires=container.get("requires", requires),
            )

        return self._build_system

    @property
    def poetry_config(self) -> dict[str, Any]:
        try:
            tool = self.data["tool"]
            assert isinstance(tool, dict)
            config = tool["poetry"]
            assert isinstance(config, dict)
            return config
        except KeyError as e:
            from poetry.core.pyproject.exceptions import PyProjectError

            raise PyProjectError(
                f"[tool.poetry] section not found in {self._path.as_posix()}"
            ) from e

    def is_poetry_project(self) -> bool:
        from poetry.core.pyproject.exceptions import PyProjectError

        if self.path.exists():
            with suppress(PyProjectError):
                _ = self.poetry_config
                return True

            # Even if there is no [tool.poetry] section, a project can still be a
            # valid Poetry project if there is a name and a version in [project]
            # and there are no dynamic fields.
            with suppress(KeyError):
                project = self.data["project"]
                if (
                    project["name"]
                    and project["version"]
                    and not project.get("dynamic")
                ):
                    return True

        return False
