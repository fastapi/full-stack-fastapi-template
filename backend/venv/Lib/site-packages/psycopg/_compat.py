"""
compatibility functions for different Python versions
"""

# Copyright (C) 2021 The Psycopg Team

import sys
from typing import Any
from functools import partial

if sys.version_info >= (3, 9):
    from asyncio import to_thread
    from zoneinfo import ZoneInfo
    from functools import cache
    from collections import Counter
    from collections import deque as Deque
    from collections.abc import Callable
else:
    import asyncio
    from typing import Callable, Counter, Deque, TypeVar
    from functools import lru_cache

    from backports.zoneinfo import ZoneInfo

    cache = lru_cache(maxsize=None)

    R = TypeVar("R")

    async def to_thread(func: Callable[..., R], /, *args: Any, **kwargs: Any) -> R:
        loop = asyncio.get_running_loop()
        func_call = partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, func_call)


if sys.version_info >= (3, 10):
    from typing import TypeAlias, TypeGuard
else:
    from typing_extensions import TypeAlias, TypeGuard

if sys.version_info >= (3, 11):
    from typing import LiteralString, Self
else:
    from typing_extensions import LiteralString, Self

if sys.version_info >= (3, 13):
    from typing import TypeVar
else:
    from typing_extensions import TypeVar

__all__ = [
    "Counter",
    "Deque",
    "LiteralString",
    "Self",
    "TypeAlias",
    "TypeGuard",
    "TypeVar",
    "ZoneInfo",
    "cache",
    "to_thread",
]
