from __future__ import annotations

import functools
import threading

from typing import TYPE_CHECKING
from typing import TypeVar
from typing import overload
from weakref import WeakKeyDictionary


if TYPE_CHECKING:
    from typing import Any
    from typing import Callable


T = TypeVar("T")
C = TypeVar("C", bound=object)


class AtomicCachedProperty(functools.cached_property[T]):
    def __init__(self, func: Callable[[C], T]) -> None:
        super().__init__(func)
        self._semaphore = threading.BoundedSemaphore()
        self._locks: WeakKeyDictionary[object, threading.Lock] = WeakKeyDictionary()

    @overload
    def __get__(
        self, instance: None, owner: type[Any] | None = ...
    ) -> AtomicCachedProperty[T]: ...
    @overload
    def __get__(self, instance: object, owner: type[Any] | None = ...) -> T: ...

    def __get__(
        self, instance: C | None, owner: type[Any] | None = None
    ) -> AtomicCachedProperty[T] | T:
        # If there's no instance, return the descriptor itself
        if instance is None:
            return self

        if instance not in self._locks:
            with self._semaphore:
                # we double-check the lock has not been created by another thread
                if instance not in self._locks:
                    self._locks[instance] = threading.Lock()

        # Use a thread-safe lock to ensure the property is computed only once
        with self._locks[instance]:
            return super().__get__(instance, owner)


def atomic_cached_property(func: Callable[[C], T]) -> AtomicCachedProperty[T]:
    """
    A thread-safe implementation of functools.cached_property that ensures lazily-computed
    properties are calculated only once, even in multithreaded environments.

    This property decorator works similar to functools.cached_property but employs
    thread locks and a bounded semaphore to handle concurrent access safely.

    The computed value is cached on the instance itself and is reused for subsequent
    accesses unless explicitly invalidated. The added thread-safety makes it ideal for
    situations where multiple threads might access and compute the property simultaneously.

    Note:
    - The cache is stored in the instance dictionary just like `functools.cached_property`.

    :param func: The function to be turned into a thread-safe cached property.
    """
    return AtomicCachedProperty(func)
