from __future__ import annotations

from typing import Any

from poetry.config.config_source import ConfigSource
from poetry.config.config_source import PropertyNotFoundError


class DictConfigSource(ConfigSource):
    def __init__(self) -> None:
        self._config: dict[str, Any] = {}

    @property
    def config(self) -> dict[str, Any]:
        return self._config

    def get_property(self, key: str) -> Any:
        keys = key.split(".")
        config = self._config

        for i, key in enumerate(keys):
            if key not in config:
                raise PropertyNotFoundError(f"Key {'.'.join(keys)} not in config")

            if i == len(keys) - 1:
                return config[key]

            config = config[key]

    def add_property(self, key: str, value: Any) -> None:
        keys = key.split(".")
        config = self._config

        for i, key in enumerate(keys):
            if key not in config and i < len(keys) - 1:
                config[key] = {}

            if i == len(keys) - 1:
                config[key] = value
                break

            config = config[key]

    def remove_property(self, key: str) -> None:
        keys = key.split(".")

        config = self._config
        for i, key in enumerate(keys):
            if key not in config:
                return

            if i == len(keys) - 1:
                del config[key]

                break

            config = config[key]
