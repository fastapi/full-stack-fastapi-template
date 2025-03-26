from __future__ import annotations

import re

from poetry.console.logging.formatters.formatter import Formatter


class BuilderLogFormatter(Formatter):
    def format(self, msg: str) -> str:
        if msg.startswith("Building "):
            msg = re.sub("Building (.+)", "  - Building <info>\\1</info>", msg)
        elif msg.startswith("Built "):
            msg = re.sub("Built (.+)", "  - Built <success>\\1</success>", msg)
        elif msg.startswith("Adding: "):
            msg = re.sub("Adding: (.+)", "  - Adding: <b>\\1</b>", msg)
        elif msg.startswith("Executing build script: "):
            msg = re.sub(
                "Executing build script: (.+)",
                "  - Executing build script: <b>\\1</b>",
                msg,
            )

        return msg
