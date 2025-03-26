from __future__ import annotations

from typing import TYPE_CHECKING

from tomlkit.toml_file import TOMLFile as BaseTOMLFile


if TYPE_CHECKING:
    from pathlib import Path

    from tomlkit.toml_document import TOMLDocument


class TOMLFile(BaseTOMLFile):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.__path = path

    @property
    def path(self) -> Path:
        return self.__path

    def exists(self) -> bool:
        return self.__path.exists()

    def read(self) -> TOMLDocument:
        from tomlkit.exceptions import TOMLKitError

        from poetry.toml import TOMLError

        try:
            return super().read()
        except (ValueError, TOMLKitError) as e:
            raise TOMLError(f"Invalid TOML file {self.path.as_posix()}: {e}")

    def __str__(self) -> str:
        return self.__path.as_posix()
