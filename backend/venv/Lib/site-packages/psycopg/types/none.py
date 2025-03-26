"""
Adapters for None.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from ..abc import AdaptContext, Buffer, NoneType
from ..adapt import Dumper


class NoneDumper(Dumper):
    """
    Not a complete dumper as it doesn't implement dump(), but it implements
    quote(), so it can be used in sql composition.
    """

    def dump(self, obj: None) -> Buffer | None:
        raise NotImplementedError("NULL is passed to Postgres in other ways")

    def quote(self, obj: None) -> Buffer:
        return b"NULL"


def register_default_adapters(context: AdaptContext) -> None:
    context.adapters.register_dumper(NoneType, NoneDumper)
