"""
Utilities to ease the differences between async and sync code.

These object offer a similar interface between sync and async versions; the
script async_to_sync.py will replace the async names with the sync names
when generating the sync version.
"""

# Copyright (C) 2023 The Psycopg Team

from __future__ import annotations

import queue
import asyncio
import threading
from typing import TYPE_CHECKING, Any, Callable, Coroutine

from ._compat import TypeAlias, TypeVar

Worker: TypeAlias = threading.Thread
AWorker: TypeAlias = "asyncio.Task[None]"
T = TypeVar("T")

# Hack required on Python 3.8 because subclassing Queue[T] fails at runtime.
# https://stackoverflow.com/questions/45414066/mypy-how-to-define-a-generic-subclass
if TYPE_CHECKING:
    _GQueue: TypeAlias = queue.Queue
    _AGQueue: TypeAlias = asyncio.Queue

else:

    class FakeGenericMeta(type):
        def __getitem__(self, item):
            return self

    class _GQueue(queue.Queue, metaclass=FakeGenericMeta):
        pass

    class _AGQueue(asyncio.Queue, metaclass=FakeGenericMeta):
        pass


class Queue(_GQueue[T]):
    """
    A Queue subclass with an interruptible get() method.
    """

    def get(self, block: bool = True, timeout: float | None = None) -> T:
        # Always specify a timeout to make the wait interruptible.
        if timeout is None:
            timeout = 24.0 * 60.0 * 60.0
        return super().get(block=block, timeout=timeout)


class AQueue(_AGQueue[T]):
    pass


def aspawn(
    f: Callable[..., Coroutine[Any, Any, None]],
    args: tuple[Any, ...] = (),
    name: str | None = None,
) -> asyncio.Task[None]:
    """
    Equivalent to asyncio.create_task.
    """
    return asyncio.create_task(f(*args), name=name)


def spawn(
    f: Callable[..., Any],
    args: tuple[Any, ...] = (),
    name: str | None = None,
) -> threading.Thread:
    """
    Equivalent to creating and running a daemon thread.
    """
    t = threading.Thread(target=f, args=args, name=name, daemon=True)
    t.start()
    return t


async def agather(*tasks: asyncio.Task[Any], timeout: float | None = None) -> None:
    """
    Equivalent to asyncio.gather or Thread.join()
    """
    wait = asyncio.gather(*tasks)
    try:
        if timeout is not None:
            await asyncio.wait_for(asyncio.shield(wait), timeout=timeout)
        else:
            await wait
    except asyncio.TimeoutError:
        pass
    else:
        return


def gather(*tasks: threading.Thread, timeout: float | None = None) -> None:
    """
    Equivalent to asyncio.gather or Thread.join()
    """
    for t in tasks:
        if not t.is_alive():
            continue
        t.join(timeout)
