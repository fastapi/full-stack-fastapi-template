from __future__ import annotations

import hashlib
import io
import logging
import os
import shutil
import stat
import sys
import tarfile
import tempfile
import zipfile

from collections.abc import Mapping
from contextlib import contextmanager
from contextlib import suppress
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import overload

from requests.exceptions import ChunkedEncodingError
from requests.exceptions import ConnectionError
from requests.utils import atomic_open

from poetry.utils.authenticator import get_default_authenticator
from poetry.utils.constants import REQUESTS_TIMEOUT


if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Collection
    from collections.abc import Iterator
    from types import TracebackType

    from poetry.core.packages.package import Package
    from requests import Response
    from requests import Session

    from poetry.utils.authenticator import Authenticator

logger = logging.getLogger(__name__)
prioritised_hash_types: tuple[str, ...] = tuple(
    t
    for t in [
        "sha3_512",
        "sha3_384",
        "sha3_256",
        "sha3_224",
        "sha512",
        "sha384",
        "sha256",
        "sha224",
        "shake_256",
        "shake_128",
        "blake2s",
        "blake2b",
    ]
    if t in hashlib.algorithms_available
)
non_prioritised_available_hash_types: frozenset[str] = frozenset(
    set(hashlib.algorithms_available).difference(prioritised_hash_types)
)


@contextmanager
def directory(path: Path) -> Iterator[Path]:
    cwd = Path.cwd()
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(cwd)


# Correct type signature when used as `shutil.rmtree(..., onexc=_on_rm_error)`.
@overload
def _on_rm_error(
    func: Callable[[str], None], path: str, exc_info: Exception
) -> None: ...


# Correct type signature when used as `shutil.rmtree(..., onerror=_on_rm_error)`.
@overload
def _on_rm_error(
    func: Callable[[str], None],
    path: str,
    exc_info: tuple[type[BaseException], BaseException, TracebackType],
) -> None: ...


def _on_rm_error(func: Callable[[str], None], path: str, exc_info: Any) -> None:
    if not os.path.exists(path):
        return

    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_directory(path: Path, force: bool = False) -> None:
    """
    Helper function handle safe removal, and optionally forces stubborn file removal.
    This is particularly useful when dist files are read-only or git writes read-only
    files on Windows.

    Internally, all arguments are passed to `shutil.rmtree`.
    """
    if path.is_symlink():
        return os.unlink(path)

    kwargs: dict[str, Any] = {}
    if force:
        onexc = "onexc" if sys.version_info >= (3, 12) else "onerror"
        kwargs[onexc] = _on_rm_error

    shutil.rmtree(path, **kwargs)


def merge_dicts(d1: dict[str, Any], d2: dict[str, Any]) -> None:
    for k in d2:
        if k in d1 and isinstance(d1[k], dict) and isinstance(d2[k], Mapping):
            merge_dicts(d1[k], d2[k])
        else:
            d1[k] = d2[k]


class HTTPRangeRequestSupportedError(Exception):
    """Raised when server unexpectedly supports byte ranges."""


def download_file(
    url: str,
    dest: Path,
    *,
    session: Authenticator | Session | None = None,
    chunk_size: int = 1024,
    raise_accepts_ranges: bool = False,
    max_retries: int = 0,
) -> None:
    from poetry.puzzle.provider import Indicator

    downloader = Downloader(url, dest, session, max_retries=max_retries)

    if raise_accepts_ranges and downloader.accepts_ranges:
        raise HTTPRangeRequestSupportedError(f"URL {url} supports range requests.")

    set_indicator = False
    with Indicator.context() as update_context:
        update_context(f"Downloading {url}")

        total_size = downloader.total_size
        if total_size > 0:
            fetched_size = 0
            last_percent = 0

            # if less than 1MB, we simply show that we're downloading
            # but skip the updating
            set_indicator = total_size > 1024 * 1024

        for fetched_size in downloader.download_with_progress(chunk_size):
            if set_indicator:
                percent = (fetched_size * 100) // total_size
                if percent > last_percent:
                    last_percent = percent
                    update_context(f"Downloading {url} {percent:3}%")


class Downloader:
    def __init__(
        self,
        url: str,
        dest: Path,
        session: Authenticator | Session | None = None,
        max_retries: int = 0,
    ):
        self._dest = dest
        self._max_retries = max_retries
        self._session = session or get_default_authenticator()
        self._url = url
        self._response = self._get()

    @cached_property
    def accepts_ranges(self) -> bool:
        return self._response.headers.get("Accept-Ranges") == "bytes"

    @cached_property
    def total_size(self) -> int:
        total_size = 0
        if "Content-Length" in self._response.headers:
            with suppress(ValueError):
                total_size = int(self._response.headers["Content-Length"])
        return total_size

    def _get(self, start: int = 0) -> Response:
        headers = {"Accept-Encoding": "Identity"}
        if start > 0:
            headers["Range"] = f"bytes={start}-"

        response = self._session.get(
            self._url, stream=True, headers=headers, timeout=REQUESTS_TIMEOUT
        )
        try:
            response.raise_for_status()
            return response
        except BaseException:
            response.close()
            raise

    def _iter_content_with_resume(self, chunk_size: int) -> Iterator[bytes]:
        fetched_size = 0
        retries = 0
        while True:
            try:
                with self._response:
                    for chunk in self._response.iter_content(chunk_size=chunk_size):
                        yield chunk
                        fetched_size += len(chunk)
            except (ChunkedEncodingError, ConnectionError):
                if (
                    retries < self._max_retries
                    and self.accepts_ranges
                    and fetched_size > 0
                ):
                    # only retry if server supports byte ranges
                    # and we have fetched at least one chunk
                    # otherwise, we should just fail
                    retries += 1
                    self._response = self._get(fetched_size)
                    continue
                raise
            else:
                break

    def download_with_progress(self, chunk_size: int = 1024) -> Iterator[int]:
        fetched_size = 0
        with atomic_open(self._dest) as f:
            for chunk in self._iter_content_with_resume(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    fetched_size += len(chunk)
                    yield fetched_size


def get_package_version_display_string(
    package: Package, root: Path | None = None
) -> str:
    if package.source_type in ["file", "directory"] and root:
        assert package.source_url is not None
        path = Path(os.path.relpath(package.source_url, root)).as_posix()
        return f"{package.version} {path}"

    pretty_version: str = package.full_pretty_version
    return pretty_version


def paths_csv(paths: list[Path]) -> str:
    return ", ".join(f'"{c!s}"' for c in paths)


def ensure_path(path: str | Path, is_directory: bool = False) -> Path:
    if isinstance(path, str):
        path = Path(path)

    if path.exists() and path.is_dir() == is_directory:
        return path

    raise ValueError(
        f"Specified path '{path}' is not a valid {'directory' if is_directory else 'file'}."
    )


def is_dir_writable(path: Path, create: bool = False) -> bool:
    try:
        if not path.exists():
            if not create:
                return False
            path.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryFile(dir=str(path)):
            pass
    except OSError:
        return False
    else:
        return True


def pluralize(count: int, word: str = "") -> str:
    if count == 1:
        return word
    return word + "s"


def _get_win_folder_from_registry(csidl_name: str) -> str:
    if sys.platform != "win32":
        raise RuntimeError("Method can only be called on Windows.")

    import winreg as _winreg

    shell_folder_name = {
        "CSIDL_APPDATA": "AppData",
        "CSIDL_COMMON_APPDATA": "Common AppData",
        "CSIDL_LOCAL_APPDATA": "Local AppData",
        "CSIDL_PROGRAM_FILES": "Program Files",
    }[csidl_name]

    key = _winreg.OpenKey(
        _winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
    )
    dir, type = _winreg.QueryValueEx(key, shell_folder_name)

    assert isinstance(dir, str)
    return dir


def _get_win_folder_with_ctypes(csidl_name: str) -> str:
    if sys.platform != "win32":
        raise RuntimeError("Method can only be called on Windows.")

    import ctypes

    csidl_const = {
        "CSIDL_APPDATA": 26,
        "CSIDL_COMMON_APPDATA": 35,
        "CSIDL_LOCAL_APPDATA": 28,
        "CSIDL_PROGRAM_FILES": 38,
    }[csidl_name]

    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

    # Downgrade to short path name if have highbit chars. See
    # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
    has_high_char = False
    for c in buf:
        if ord(c) > 255:
            has_high_char = True
            break
    if has_high_char:
        buf2 = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
            buf = buf2

    return buf.value


def get_win_folder(csidl_name: str) -> Path:
    if sys.platform == "win32":
        try:
            from ctypes import windll  # noqa: F401

            _get_win_folder = _get_win_folder_with_ctypes
        except ImportError:
            _get_win_folder = _get_win_folder_from_registry

        return Path(_get_win_folder(csidl_name))

    raise RuntimeError("Method can only be called on Windows.")


def get_real_windows_path(path: Path) -> Path:
    program_files = get_win_folder("CSIDL_PROGRAM_FILES")
    local_appdata = get_win_folder("CSIDL_LOCAL_APPDATA")

    path = Path(
        str(path).replace(
            str(program_files / "WindowsApps"),
            str(local_appdata / "Microsoft/WindowsApps"),
        )
    )

    if path.as_posix().startswith(local_appdata.as_posix()):
        path = path.resolve()

    return path


def get_file_hash(path: Path, hash_name: str = "sha256") -> str:
    h = hashlib.new(hash_name)
    with path.open("rb") as fp:
        for content in iter(lambda: fp.read(io.DEFAULT_BUFFER_SIZE), b""):
            h.update(content)

    return h.hexdigest()


def get_highest_priority_hash_type(
    hash_types: Collection[str], archive_name: str
) -> str | None:
    if not hash_types:
        return None

    for prioritised_hash_type in prioritised_hash_types:
        if prioritised_hash_type in hash_types:
            return prioritised_hash_type

    logger.debug(
        f"There are no known hash types for {archive_name} that are prioritised (known"
        f" hash types: {hash_types!s})"
    )

    for available_hash_type in non_prioritised_available_hash_types:
        if available_hash_type in hash_types:
            return available_hash_type

    return None


def extractall(source: Path, dest: Path, zip: bool) -> None:
    """Extract all members from either a zip or tar archive."""
    if zip:
        with zipfile.ZipFile(source) as archive:
            archive.extractall(dest)
    else:
        # These versions of python shipped with a broken tarfile data_filter, per
        # https://github.com/python/cpython/issues/107845.
        broken_tarfile_filter = {(3, 9, 17), (3, 10, 12), (3, 11, 4)}
        with tarfile.open(source) as archive:
            if (
                hasattr(tarfile, "data_filter")
                and sys.version_info[:3] not in broken_tarfile_filter
            ):
                archive.extractall(dest, filter="data")
            else:
                archive.extractall(dest)
