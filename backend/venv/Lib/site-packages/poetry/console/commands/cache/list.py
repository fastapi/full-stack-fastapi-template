from __future__ import annotations

from poetry.config.config import Config
from poetry.console.commands.command import Command


class CacheListCommand(Command):
    name = "cache list"
    description = "List Poetry's caches."

    def handle(self) -> int:
        config = Config.create()
        if config.repository_cache_directory.exists():
            caches = sorted(config.repository_cache_directory.iterdir())
            if caches:
                for cache in caches:
                    self.line(f"<info>{cache.name}</>")
                return 0

        self.line_error("<warning>No caches found</>")
        return 0
