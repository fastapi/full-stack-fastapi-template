from __future__ import annotations

import shlex
import subprocess
import sys


WINDOWS = sys.platform == "win32"


def shell_quote(token: str) -> str:
    if WINDOWS:
        return subprocess.list2cmdline([token])

    return shlex.quote(token)
