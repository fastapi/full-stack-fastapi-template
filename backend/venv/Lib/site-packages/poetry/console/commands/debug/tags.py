from __future__ import annotations

from poetry.console.commands.env_command import EnvCommand


class DebugTagsCommand(EnvCommand):
    name = "debug tags"
    description = "Shows compatible tags for your project's current active environment."

    def handle(self) -> int:
        for tag in self.env.get_supported_tags():
            self.io.write_line(
                f"<c1>{tag.interpreter}</>"
                f"-<c2>{tag.abi}</>"
                f"-<fg=yellow;options=bold>{tag.platform}</>"
            )
        return 0
