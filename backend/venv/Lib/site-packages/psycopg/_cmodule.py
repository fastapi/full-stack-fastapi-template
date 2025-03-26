# mypy: disable-error-code="import-not-found, attr-defined"
"""
Simplify access to the _psycopg module
"""

# Copyright (C) 2021 The Psycopg Team

from __future__ import annotations

from types import ModuleType

from . import pq

__version__: str | None = None
_psycopg: ModuleType

# Note: "c" must the first attempt so that mypy associates the variable the
# right module interface. It will not result Optional, but hey.
if pq.__impl__ == "c":
    import psycopg_c._psycopg

    _psycopg = psycopg_c._psycopg
    __version__ = psycopg_c.__version__

elif pq.__impl__ == "binary":
    import psycopg_binary._psycopg

    _psycopg = psycopg_binary._psycopg
    __version__ = psycopg_binary.__version__

elif pq.__impl__ == "python":

    _psycopg = None  # type: ignore[assignment]

else:
    raise ImportError(f"can't find _psycopg optimised module in {pq.__impl__!r}")
