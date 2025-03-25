from __future__ import annotations

import tarfile
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from _typeshed import StrPath

ARCH_MAPPING = {
    "arm64": "aarch64",
    "amd64": "x86_64",
    "i686": "x86",
}
PLATFORM_MAPPING = {"darwin": "macos"}


class PythonVersion(NamedTuple):
    implementation: str
    major: int
    minor: int
    micro: int

    def __str__(self) -> str:
        return f"{self.implementation}@{self.major}.{self.minor}.{self.micro}"

    def matches(self, request: str, implementation: str) -> bool:
        if implementation != self.implementation:
            return False
        try:
            parts = tuple(int(v) for v in request.rstrip("t").split("."))
        except ValueError:
            raise ValueError(
                f"Invalid version: {request!r}, each part must be an integer"
            ) from None

        if len(parts) < 1:
            raise ValueError("Version must have at least one part")

        if parts[0] != self.major:
            return False
        if len(parts) > 1 and parts[1] != self.minor:
            return False
        if len(parts) > 2 and parts[2] != self.micro:
            return False
        return True


def get_arch_platform() -> tuple[str, str]:
    import platform

    plat = platform.system().lower()
    arch = platform.machine().lower()
    return ARCH_MAPPING.get(arch, arch), PLATFORM_MAPPING.get(plat, plat)


def _unpack_tar(tf: tarfile.TarFile, destination: StrPath) -> None:
    """Unpack the tarfile to the destination, with the first skip_parts parts of the path removed"""
    members: list[tarfile.TarInfo] = []
    for member in tf.getmembers():
        parts = member.name.lstrip("/").split("/")
        member.name = "/".join(parts[1:])
        if member.name:
            members.append(member)
    tf.extractall(destination, members=members)


def unpack_tar(filename: str, destination: StrPath) -> None:
    """Unpack the tarfile to the destination"""
    with tarfile.open(filename) as z:
        _unpack_tar(z, destination)


def unpack_zst(filename: str, destination: StrPath) -> None:
    """Unpack the zstd compressed tarfile to the destination"""
    import tempfile

    try:
        import zstandard as zstd
    except ModuleNotFoundError:
        raise ModuleNotFoundError("zstandard is required to unpack .zst files") from None

    dctx = zstd.ZstdDecompressor()
    with tempfile.TemporaryFile(suffix=".tar") as ofh:
        with open(filename, "rb") as ifh:
            dctx.copy_stream(ifh, ofh)
        ofh.seek(0)
        with tarfile.open(fileobj=ofh) as z:
            _unpack_tar(z, destination)


def unpack_zip(filename: str, destination: StrPath) -> None:
    """Unpack the zip file to the destination"""
    import zipfile

    with zipfile.ZipFile(filename) as z:
        members: list[zipfile.ZipInfo] = []
        for member in z.infolist():
            parts = member.filename.lstrip("/").split("/")
            member.filename = "/".join(parts[1:])
            if member.filename:
                members.append(member)

        z.extractall(destination, members=members)


def get_available_arch_platforms() -> tuple[list[str], list[str]]:
    from ._versions import PYTHON_VERSIONS

    archs: set[str] = set()
    platforms: set[str] = set()
    for items in PYTHON_VERSIONS.values():
        for item in items:
            platforms.add(item[0])
            archs.add(item[1])
    return sorted(archs), sorted(platforms)
