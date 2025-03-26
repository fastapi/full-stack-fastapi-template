from __future__ import annotations

import hashlib
import io

from contextlib import suppress
from typing import TYPE_CHECKING
from typing import NamedTuple


if TYPE_CHECKING:
    from pathlib import Path


class Hexdigest(NamedTuple):
    md5: str | None
    sha256: str | None
    blake2_256: str | None


class HashManager:
    def __init__(self) -> None:
        self._sha2_hasher = hashlib.sha256()

        self._md5_hasher = None
        with suppress(ValueError):
            # FIPS mode disables MD5
            self._md5_hasher = hashlib.md5()

        self._blake_hasher = None
        with suppress(ValueError, TypeError):
            # FIPS mode disables blake2
            self._blake_hasher = hashlib.blake2b(digest_size=256 // 8)

    def _md5_update(self, content: bytes) -> None:
        if self._md5_hasher is not None:
            self._md5_hasher.update(content)

    def _md5_hexdigest(self) -> str | None:
        if self._md5_hasher is not None:
            return self._md5_hasher.hexdigest()
        return None

    def _blake_update(self, content: bytes) -> None:
        if self._blake_hasher is not None:
            self._blake_hasher.update(content)

    def _blake_hexdigest(self) -> str | None:
        if self._blake_hasher is not None:
            return self._blake_hasher.hexdigest()
        return None

    def hash(self, file: Path) -> None:
        with file.open("rb") as fp:
            for content in iter(lambda: fp.read(io.DEFAULT_BUFFER_SIZE), b""):
                self._md5_update(content)
                self._sha2_hasher.update(content)
                self._blake_update(content)

    def hexdigest(self) -> Hexdigest:
        return Hexdigest(
            self._md5_hexdigest(),
            self._sha2_hasher.hexdigest(),
            self._blake_hexdigest(),
        )
