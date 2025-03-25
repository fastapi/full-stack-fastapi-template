from __future__ import annotations

from poetry.core.exceptions import PoetryCoreError
from tomlkit.exceptions import TOMLKitError


class TOMLError(TOMLKitError, PoetryCoreError):
    pass
