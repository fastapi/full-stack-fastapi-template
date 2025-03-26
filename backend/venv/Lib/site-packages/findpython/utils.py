from __future__ import annotations

import errno
import hashlib
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Generator, Sequence, TypedDict

VERSION_RE = re.compile(
    r"(?:(?P<implementation>\w+)@)?(?P<major>\d+)(?:\.(?P<minor>\d+)(?:\.(?P<patch>[0-9]+))?)?\.?"
    r"(?:(?P<prerel>[abc]|rc|dev)(?:(?P<prerelversion>\d+(?:\.\d+)*))?)"
    r"?(?P<postdev>(\.post(?P<post>\d+))?(\.dev(?P<dev>\d+))?)?"
    r"(?:-(?P<architecture>32|64))?"
)
WINDOWS = sys.platform == "win32"
MACOS = sys.platform == "darwin"
PYTHON_IMPLEMENTATIONS = (
    "python",
    "ironpython",
    "jython",
    "pypy",
    "anaconda",
    "miniconda",
    "stackless",
    "activepython",
    "pyston",
    "micropython",
)
if WINDOWS:
    KNOWN_EXTS: Sequence[str] = (".exe", "", ".py", ".bat")
else:
    KNOWN_EXTS = ("", ".sh", ".bash", ".csh", ".zsh", ".fish", ".py")
PY_MATCH_STR = (
    r"((?P<implementation>{0})(?:\d(?:\.?\d\d?[cpm]{{0,3}})?)?"
    r"(?:(?<=\d)-[\d\.]+)*(?!w))(?P<suffix>{1})$".format(
        "|".join(PYTHON_IMPLEMENTATIONS),
        "|".join(KNOWN_EXTS),
    )
)
RE_MATCHER = re.compile(PY_MATCH_STR)


def safe_iter_dir(path: Path) -> Generator[Path, None, None]:
    """Iterate over a directory, returning an empty iterator if the path
    is not a directory or is not readable.
    """
    if not os.access(str(path), os.R_OK) or not path.is_dir():
        return
    try:
        yield from path.iterdir()
    except OSError as exc:
        if exc.errno == errno.EACCES:
            return
        raise


@lru_cache(maxsize=1024)
def path_is_known_executable(path: Path) -> bool:
    """
    Returns whether a given path is a known executable from known executable extensions
    or has the executable bit toggled.

    :param path: The path to the target executable.
    :type path: :class:`~Path`
    :return: True if the path has chmod +x, or is a readable, known executable extension.
    :rtype: bool
    """
    try:
        return (
            path.is_file()
            and os.access(str(path), os.R_OK)
            and (path.suffix in KNOWN_EXTS or os.access(str(path), os.X_OK))
        )
    except OSError:
        return False


@lru_cache(maxsize=1024)
def looks_like_python(name: str) -> bool:
    """
    Determine whether the supplied filename looks like a possible name of python.

    :param str name: The name of the provided file.
    :return: Whether the provided name looks like python.
    :rtype: bool
    """
    if not any(name.lower().startswith(py_name) for py_name in PYTHON_IMPLEMENTATIONS):
        return False
    match = RE_MATCHER.match(name)
    return bool(match)


@lru_cache(maxsize=1024)
def path_is_python(path: Path) -> bool:
    """
    Determine whether the supplied path is a executable and looks like
    a possible path to python.

    :param path: The path to an executable.
    :type path: :class:`~Path`
    :return: Whether the provided path is an executable path to python.
    :rtype: bool
    """
    return looks_like_python(path.name) and path_is_known_executable(path)


@lru_cache(maxsize=1024)
def get_binary_hash(path: Path) -> str:
    """Return the MD5 hash of the given file."""
    hasher = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


if TYPE_CHECKING:

    class VersionDict(TypedDict):
        pre: bool
        dev: bool
        major: int | None
        minor: int | None
        patch: int | None
        architecture: str | None
        implementation: str | None


def parse_major(version: str) -> VersionDict | None:
    """Parse the version dict from the version string"""
    match = VERSION_RE.match(version)
    if not match:
        return None
    rv = match.groupdict()
    rv["pre"] = bool(rv.pop("prerel"))
    rv["dev"] = bool(rv.pop("dev"))
    for int_values in ("major", "minor", "patch"):
        if rv[int_values] is not None:
            rv[int_values] = int(rv[int_values])
    if rv["architecture"]:
        rv["architecture"] = f"{rv['architecture']}bit"
    return cast("VersionDict", rv)


def get_suffix_preference(name: str) -> int:
    for i, suffix in enumerate(KNOWN_EXTS):
        if suffix and name.endswith(suffix):
            return i
    return KNOWN_EXTS.index("")
