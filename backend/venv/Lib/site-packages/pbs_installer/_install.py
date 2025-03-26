from __future__ import annotations

import hashlib
import logging
import os
import tempfile
from typing import TYPE_CHECKING, Optional, Tuple, cast
from urllib.parse import unquote

from ._utils import PythonVersion, get_arch_platform

if TYPE_CHECKING:
    from typing import Literal

    import httpx
    from _typeshed import StrPath

    PythonImplementation = Literal["cpython", "pypy"]

logger = logging.getLogger(__name__)
THIS_ARCH, THIS_PLATFORM = get_arch_platform()
PythonFile = Tuple[str, Optional[str]]


def _get_headers() -> dict[str, str] | None:
    TOKEN = os.getenv("GITHUB_TOKEN")
    if TOKEN is None:
        return None
    return {
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {TOKEN}",
    }


def get_download_link(
    request: str,
    arch: str = THIS_ARCH,
    platform: str = THIS_PLATFORM,
    implementation: PythonImplementation = "cpython",
    build_dir: bool = False,
    free_threaded: bool = False,
) -> tuple[PythonVersion, PythonFile]:
    """Get the download URL matching the given requested version.

    Parameters:
        request: The version of Python to install, e.g. 3.8,3.10.4
        arch: The architecture to install, e.g. x86_64, arm64
        platform: The platform to install, e.g. linux, macos
        implementation: The implementation of Python to install, allowed values are 'cpython' and 'pypy'
        build_dir: Whether to include the `build/` directory from indygreg builds
        free_threaded: Whether to install the freethreaded version of Python

    Returns:
        A tuple of the PythonVersion and the download URL

    Examples:
        >>> get_download_link("3.10", "x86_64", "linux")
        (PythonVersion(kind='cpython', major=3, minor=10, micro=13),
        'https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.10.13%2B20240224-x86_64-unknown-linux-gnu-pgo%2Blto-full.tar.zst')
    """
    from ._versions import PYTHON_VERSIONS

    for py_ver, urls in PYTHON_VERSIONS.items():
        if not py_ver.matches(request, implementation):
            continue

        if request.endswith("t"):
            free_threaded = True

        matched = urls.get((platform, arch, not build_dir, free_threaded))
        if matched is not None:
            return py_ver, matched
        if (
            not build_dir
            and (matched := urls.get((platform, arch, False, free_threaded))) is not None
        ):
            return py_ver, matched
    raise ValueError(
        f"Could not find a version matching version={request!r}, implementation={implementation}"
    )


def download(
    python_file: PythonFile, destination: StrPath, client: httpx.Client | None = None
) -> str:
    """Download the given url to the destination.

    Note: Extras required
        `pbs-installer[download]` must be installed to use this function.

    Parameters:
        python_file: The (url, checksum) tuple to download
        destination: The file path to download to
        client: A http.Client to use for downloading, or None to create a new one

    Returns:
        The original filename of the downloaded file
    """
    url, checksum = python_file
    logger.debug("Downloading url %s to %s", url, destination)
    try:
        import httpx
    except ModuleNotFoundError:
        raise RuntimeError("You must install httpx to use this function") from None

    if client is None:
        client = httpx.Client(trust_env=True, follow_redirects=True)

    filename = unquote(url.rsplit("/")[-1])
    hasher = hashlib.sha256()
    if not checksum:
        logger.warning("No checksum found for %s, this would be insecure", url)

    with open(destination, "wb") as f:
        with client.stream("GET", url, headers=_get_headers()) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_bytes(chunk_size=8192):
                if checksum:
                    hasher.update(chunk)
                f.write(chunk)

    if checksum and hasher.hexdigest() != checksum:
        raise RuntimeError(f"Checksum mismatch. Expected {checksum}, got {hasher.hexdigest()}")
    return filename


def install_file(
    filename: StrPath,
    destination: StrPath,
    original_filename: str | None = None,
    build_dir: bool = False,
) -> None:
    """Unpack the downloaded file to the destination.

    Note: Extras required
        `pbs-installer[install]` must be installed to use this function.

    Parameters:
        filename: The file to unpack
        destination: The directory to unpack to
        original_filename: The original filename of the file, if it was renamed
        build_dir: Whether to include the `build/` directory from indygreg builds
    """

    from ._utils import unpack_tar, unpack_zip, unpack_zst

    if original_filename is None:
        original_filename = str(filename)
    logger.debug(
        "Extracting file %s to %s with original filename %s",
        filename,
        destination,
        original_filename,
    )
    filename = cast(str, filename)
    if original_filename.endswith(".zst"):
        unpack_zst(filename, destination)
    elif original_filename.endswith(".zip"):
        unpack_zip(filename, destination)
    else:
        unpack_tar(filename, destination)


def install(
    request: str,
    destination: StrPath,
    version_dir: bool = False,
    client: httpx.Client | None = None,
    arch: str | None = None,
    platform: str | None = None,
    implementation: PythonImplementation = "cpython",
    build_dir: bool = False,
    free_threaded: bool = False,
) -> None:
    """Download and install the requested python version.

    Note: Extras required
        `pbs-installer[all]` must be installed to use this function.

    Parameters:
        request: The version of Python to install, e.g. 3.8,3.10.4
        destination: The directory to install to
        version_dir: Whether to install to a subdirectory named with the python version
        client: A httpx.Client to use for downloading
        arch: The architecture to install, e.g. x86_64, arm64
        platform: The platform to install, e.g. linux, macos
        implementation: The implementation of Python to install, allowed values are 'cpython' and 'pypy'
        build_dir: Whether to include the `build/` directory from indygreg builds
        free_threaded: Whether to install the freethreaded version of Python
    Examples:
        >>> install("3.10", "./python")
        Installing cpython@3.10.4 to ./python
        >>> install("3.10", "./python", version_dir=True)
        Installing cpython@3.10.4 to ./python/cpython@3.10.4
    """
    if platform is None:
        platform = THIS_PLATFORM
    if arch is None:
        arch = THIS_ARCH

    ver, python_file = get_download_link(
        request,
        arch=arch,
        platform=platform,
        implementation=implementation,
        build_dir=build_dir,
        free_threaded=free_threaded,
    )
    if version_dir:
        destination = os.path.join(destination, str(ver))
    logger.debug("Installing %s to %s", ver, destination)
    os.makedirs(destination, exist_ok=True)
    with tempfile.NamedTemporaryFile() as tf:
        tf.close()
        original_filename = download(python_file, tf.name, client)
        install_file(tf.name, destination, original_filename, build_dir)
