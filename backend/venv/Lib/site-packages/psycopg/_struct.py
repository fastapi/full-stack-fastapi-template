"""
Utility functions to deal with binary structs.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

import struct
from typing import Callable, Protocol, cast

from . import errors as e
from .abc import Buffer
from ._compat import TypeAlias

PackInt: TypeAlias = Callable[[int], bytes]
UnpackInt: TypeAlias = Callable[[Buffer], "tuple[int]"]
PackFloat: TypeAlias = Callable[[float], bytes]
UnpackFloat: TypeAlias = Callable[[Buffer], "tuple[float]"]


class UnpackLen(Protocol):
    def __call__(self, data: Buffer, start: int | None) -> tuple[int]: ...


pack_int2 = cast(PackInt, struct.Struct("!h").pack)
pack_uint2 = cast(PackInt, struct.Struct("!H").pack)
pack_int4 = cast(PackInt, struct.Struct("!i").pack)
pack_uint4 = cast(PackInt, struct.Struct("!I").pack)
pack_int8 = cast(PackInt, struct.Struct("!q").pack)
pack_float4 = cast(PackFloat, struct.Struct("!f").pack)
pack_float8 = cast(PackFloat, struct.Struct("!d").pack)

unpack_int2 = cast(UnpackInt, struct.Struct("!h").unpack)
unpack_uint2 = cast(UnpackInt, struct.Struct("!H").unpack)
unpack_int4 = cast(UnpackInt, struct.Struct("!i").unpack)
unpack_uint4 = cast(UnpackInt, struct.Struct("!I").unpack)
unpack_int8 = cast(UnpackInt, struct.Struct("!q").unpack)
unpack_float4 = cast(UnpackFloat, struct.Struct("!f").unpack)
unpack_float8 = cast(UnpackFloat, struct.Struct("!d").unpack)

_struct_len = struct.Struct("!i")
pack_len = cast(Callable[[int], bytes], _struct_len.pack)
unpack_len = cast(UnpackLen, _struct_len.unpack_from)


def pack_float4_bug_304(x: float) -> bytes:
    raise e.InterfaceError(
        "cannot dump Float4: Python affected by bug #304. Note that the psycopg-c"
        " and psycopg-binary packages are not affected by this issue."
        " See https://github.com/psycopg/psycopg/issues/304"
    )


# If issue #304 is detected, raise an error instead of dumping wrong data.
if struct.Struct("!f").pack(1.0) != bytes.fromhex("3f800000"):
    pack_float4 = pack_float4_bug_304
