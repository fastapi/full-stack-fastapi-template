# lru_cache.py -- Simple LRU cache for dulwich
# Copyright (C) 2006, 2008 Canonical Ltd
# Copyright (C) 2022 Jelmer Vernooĳ <jelmer@jelmer.uk>
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
# Dulwich is dual-licensed under the Apache License, Version 2.0 and the GNU
# General Public License as public by the Free Software Foundation; version 2.0
# or (at your option) any later version. You can redistribute it and/or
# modify it under the terms of either of these two licenses.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You should have received a copy of the licenses; if not, see
# <http://www.gnu.org/licenses/> for a copy of the GNU General Public License
# and <http://www.apache.org/licenses/LICENSE-2.0> for a copy of the Apache
# License, Version 2.0.
#

"""A simple least-recently-used (LRU) cache."""

from collections.abc import Iterable, Iterator
from typing import Callable, Generic, Optional, TypeVar

_null_key = object()


K = TypeVar("K")
V = TypeVar("V")


class _LRUNode(Generic[K, V]):
    """This maintains the linked-list which is the lru internals."""

    __slots__ = ("cleanup", "key", "next_key", "prev", "size", "value")

    prev: Optional["_LRUNode[K, V]"]
    next_key: K
    size: Optional[int]

    def __init__(self, key: K, value: V, cleanup=None) -> None:
        self.prev = None
        self.next_key = _null_key  # type: ignore
        self.key = key
        self.value = value
        self.cleanup = cleanup
        # TODO: We could compute this 'on-the-fly' like we used to, and remove
        #       one pointer from this object, we just need to decide if it
        #       actually costs us much of anything in normal usage
        self.size = None

    def __repr__(self) -> str:
        if self.prev is None:
            prev_key = None
        else:
            prev_key = self.prev.key
        return f"{self.__class__.__name__}({self.key!r} n:{self.next_key!r} p:{prev_key!r})"

    def run_cleanup(self) -> None:
        if self.cleanup is not None:
            self.cleanup(self.key, self.value)
        self.cleanup = None
        # Just make sure to break any refcycles, etc
        del self.value


class LRUCache(Generic[K, V]):
    """A class which manages a cache of entries, removing unused ones."""

    _least_recently_used: Optional[_LRUNode[K, V]]
    _most_recently_used: Optional[_LRUNode[K, V]]

    def __init__(
        self, max_cache: int = 100, after_cleanup_count: Optional[int] = None
    ) -> None:
        self._cache: dict[K, _LRUNode[K, V]] = {}
        # The "HEAD" of the lru linked list
        self._most_recently_used = None
        # The "TAIL" of the lru linked list
        self._least_recently_used = None
        self._update_max_cache(max_cache, after_cleanup_count)

    def __contains__(self, key: K) -> bool:
        return key in self._cache

    def __getitem__(self, key: K) -> V:
        cache = self._cache
        node = cache[key]
        # Inlined from _record_access to decrease the overhead of __getitem__
        # We also have more knowledge about structure if __getitem__ is
        # succeeding, then we know that self._most_recently_used must not be
        # None, etc.
        mru = self._most_recently_used
        if node is mru:
            # Nothing to do, this node is already at the head of the queue
            return node.value
        # Remove this node from the old location
        node_prev = node.prev
        next_key = node.next_key
        # benchmarking shows that the lookup of _null_key in globals is faster
        # than the attribute lookup for (node is self._least_recently_used)
        if next_key is _null_key:
            # 'node' is the _least_recently_used, because it doesn't have a
            # 'next' item. So move the current lru to the previous node.
            self._least_recently_used = node_prev
        else:
            node_next = cache[next_key]
            node_next.prev = node_prev
        assert node_prev
        assert mru
        node_prev.next_key = next_key
        # Insert this node at the front of the list
        node.next_key = mru.key
        mru.prev = node
        self._most_recently_used = node
        node.prev = None
        return node.value

    def __len__(self) -> int:
        return len(self._cache)

    def _walk_lru(self) -> Iterator[_LRUNode[K, V]]:
        """Walk the LRU list, only meant to be used in tests."""
        node = self._most_recently_used
        if node is not None:
            if node.prev is not None:
                raise AssertionError(
                    "the _most_recently_used entry is not"
                    " supposed to have a previous entry"
                    f" {node}"
                )
        while node is not None:
            if node.next_key is _null_key:
                if node is not self._least_recently_used:
                    raise AssertionError(
                        f"only the last node should have no next value: {node}"
                    )
                node_next = None
            else:
                node_next = self._cache[node.next_key]
                if node_next.prev is not node:
                    raise AssertionError(
                        f"inconsistency found, node.next.prev != node: {node}"
                    )
            if node.prev is None:
                if node is not self._most_recently_used:
                    raise AssertionError(
                        "only the _most_recently_used should"
                        f" not have a previous node: {node}"
                    )
            else:
                if node.prev.next_key != node.key:
                    raise AssertionError(
                        f"inconsistency found, node.prev.next != node: {node}"
                    )
            yield node
            node = node_next

    def add(
        self, key: K, value: V, cleanup: Optional[Callable[[K, V], None]] = None
    ) -> None:
        """Add a new value to the cache.

        Also, if the entry is ever removed from the cache, call
        cleanup(key, value).

        Args:
          key: The key to store it under
          value: The object to store
          cleanup: None or a function taking (key, value) to indicate
                        'value' should be cleaned up.
        """
        if key is _null_key:
            raise ValueError("cannot use _null_key as a key")
        if key in self._cache:
            node = self._cache[key]
            node.run_cleanup()
            node.value = value
            node.cleanup = cleanup
        else:
            node = _LRUNode(key, value, cleanup=cleanup)
            self._cache[key] = node
        self._record_access(node)

        if len(self._cache) > self._max_cache:
            # Trigger the cleanup
            self.cleanup()

    def cache_size(self) -> int:
        """Get the number of entries we will cache."""
        return self._max_cache

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        node = self._cache.get(key, None)
        if node is None:
            return default
        self._record_access(node)
        return node.value

    def keys(self) -> Iterable[K]:
        """Get the list of keys currently cached.

        Note that values returned here may not be available by the time you
        request them later. This is simply meant as a peak into the current
        state.

        Returns: An unordered list of keys that are currently cached.
        """
        return self._cache.keys()

    def items(self) -> dict[K, V]:
        """Get the key:value pairs as a dict."""
        return {k: n.value for k, n in self._cache.items()}

    def cleanup(self) -> None:
        """Clear the cache until it shrinks to the requested size.

        This does not completely wipe the cache, just makes sure it is under
        the after_cleanup_count.
        """
        # Make sure the cache is shrunk to the correct size
        while len(self._cache) > self._after_cleanup_count:
            self._remove_lru()

    def __setitem__(self, key: K, value: V) -> None:
        """Add a value to the cache, there will be no cleanup function."""
        self.add(key, value, cleanup=None)

    def _record_access(self, node: _LRUNode[K, V]) -> None:
        """Record that key was accessed."""
        # Move 'node' to the front of the queue
        if self._most_recently_used is None:
            self._most_recently_used = node
            self._least_recently_used = node
            return
        elif node is self._most_recently_used:
            # Nothing to do, this node is already at the head of the queue
            return
        # We've taken care of the tail pointer, remove the node, and insert it
        # at the front
        # REMOVE
        if node is self._least_recently_used:
            self._least_recently_used = node.prev
        if node.prev is not None:
            node.prev.next_key = node.next_key
        if node.next_key is not _null_key:
            node_next = self._cache[node.next_key]
            node_next.prev = node.prev
        # INSERT
        node.next_key = self._most_recently_used.key
        self._most_recently_used.prev = node
        self._most_recently_used = node
        node.prev = None

    def _remove_node(self, node: _LRUNode[K, V]) -> None:
        if node is self._least_recently_used:
            self._least_recently_used = node.prev
        self._cache.pop(node.key)
        # If we have removed all entries, remove the head pointer as well
        if self._least_recently_used is None:
            self._most_recently_used = None
        node.run_cleanup()
        # Now remove this node from the linked list
        if node.prev is not None:
            node.prev.next_key = node.next_key
        if node.next_key is not _null_key:
            node_next = self._cache[node.next_key]
            node_next.prev = node.prev
        # And remove this node's pointers
        node.prev = None
        node.next_key = _null_key  # type: ignore

    def _remove_lru(self) -> None:
        """Remove one entry from the lru, and handle consequences.

        If there are no more references to the lru, then this entry should be
        removed from the cache.
        """
        assert self._least_recently_used
        self._remove_node(self._least_recently_used)

    def clear(self) -> None:
        """Clear out all of the cache."""
        # Clean up in LRU order
        while self._cache:
            self._remove_lru()

    def resize(self, max_cache: int, after_cleanup_count: Optional[int] = None) -> None:
        """Change the number of entries that will be cached."""
        self._update_max_cache(max_cache, after_cleanup_count=after_cleanup_count)

    def _update_max_cache(self, max_cache, after_cleanup_count=None) -> None:
        self._max_cache = max_cache
        if after_cleanup_count is None:
            self._after_cleanup_count = self._max_cache * 8 / 10
        else:
            self._after_cleanup_count = min(after_cleanup_count, self._max_cache)
        self.cleanup()


class LRUSizeCache(LRUCache[K, V]):
    """An LRUCache that removes things based on the size of the values.

    This differs in that it doesn't care how many actual items there are,
    it just restricts the cache to be cleaned up after so much data is stored.

    The size of items added will be computed using compute_size(value), which
    defaults to len() if not supplied.
    """

    _compute_size: Callable[[V], int]

    def __init__(
        self,
        max_size: int = 1024 * 1024,
        after_cleanup_size: Optional[int] = None,
        compute_size: Optional[Callable[[V], int]] = None,
    ) -> None:
        """Create a new LRUSizeCache.

        Args:
          max_size: The max number of bytes to store before we start
            clearing out entries.
          after_cleanup_size: After cleaning up, shrink everything to this
            size.
          compute_size: A function to compute the size of the values. We
            use a function here, so that you can pass 'len' if you are just
            using simple strings, or a more complex function if you are using
            something like a list of strings, or even a custom object.
            The function should take the form "compute_size(value) => integer".
            If not supplied, it defaults to 'len()'
        """
        self._value_size = 0
        if compute_size is None:
            self._compute_size = len  # type: ignore
        else:
            self._compute_size = compute_size
        self._update_max_size(max_size, after_cleanup_size=after_cleanup_size)
        LRUCache.__init__(self, max_cache=max(int(max_size / 512), 1))

    def add(
        self, key: K, value: V, cleanup: Optional[Callable[[K, V], None]] = None
    ) -> None:
        """Add a new value to the cache.

        Also, if the entry is ever removed from the cache, call
        cleanup(key, value).

        Args:
          key: The key to store it under
          value: The object to store
          cleanup: None or a function taking (key, value) to indicate
                        'value' should be cleaned up.
        """
        if key is _null_key:
            raise ValueError("cannot use _null_key as a key")
        node = self._cache.get(key, None)
        value_len = self._compute_size(value)
        if value_len >= self._after_cleanup_size:
            # The new value is 'too big to fit', as it would fill up/overflow
            # the cache all by itself
            if node is not None:
                # We won't be replacing the old node, so just remove it
                self._remove_node(node)
            if cleanup is not None:
                cleanup(key, value)
            return
        if node is None:
            node = _LRUNode(key, value, cleanup=cleanup)
            self._cache[key] = node
        else:
            assert node.size is not None
            self._value_size -= node.size
        node.size = value_len
        self._value_size += value_len
        self._record_access(node)

        if self._value_size > self._max_size:
            # Time to cleanup
            self.cleanup()

    def cleanup(self) -> None:
        """Clear the cache until it shrinks to the requested size.

        This does not completely wipe the cache, just makes sure it is under
        the after_cleanup_size.
        """
        # Make sure the cache is shrunk to the correct size
        while self._value_size > self._after_cleanup_size:
            self._remove_lru()

    def _remove_node(self, node: _LRUNode[K, V]) -> None:
        assert node.size is not None
        self._value_size -= node.size
        LRUCache._remove_node(self, node)

    def resize(self, max_size: int, after_cleanup_size: Optional[int] = None) -> None:
        """Change the number of bytes that will be cached."""
        self._update_max_size(max_size, after_cleanup_size=after_cleanup_size)
        max_cache = max(int(max_size / 512), 1)
        self._update_max_cache(max_cache)

    def _update_max_size(
        self, max_size: int, after_cleanup_size: Optional[int] = None
    ) -> None:
        self._max_size = max_size
        if after_cleanup_size is None:
            self._after_cleanup_size = self._max_size * 8 // 10
        else:
            self._after_cleanup_size = min(after_cleanup_size, self._max_size)
