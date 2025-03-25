"""
PostgreSQL type modifiers.

The type modifiers parse catalog information to obtain the type modifier
of a column - the numeric part of varchar(10) or decimal(6,2).
"""

# Copyright (C) 2024 The Psycopg Team

from __future__ import annotations


class TypeModifier:
    """Type modifier that doesn't know any modifier.

    Useful to describe types with no type modifier.
    """

    def __init__(self, oid: int):
        self.oid = oid

    def get_modifier(self, typemod: int) -> tuple[int, ...] | None:
        return None

    def get_display_size(self, typemod: int) -> int | None:
        return None

    def get_precision(self, typemod: int) -> int | None:
        return None

    def get_scale(self, typemod: int) -> int | None:
        return None


class NumericTypeModifier(TypeModifier):
    """Handle numeric type modifier."""

    def get_modifier(self, typemod: int) -> tuple[int, ...] | None:
        precision = self.get_precision(typemod)
        scale = self.get_scale(typemod)
        return None if precision is None or scale is None else (precision, scale)

    def get_precision(self, typemod: int) -> int | None:
        return typemod >> 16 if typemod >= 0 else None

    def get_scale(self, typemod: int) -> int | None:
        if typemod < 0:
            return None

        scale = (typemod - 4) & 0xFFFF
        if scale >= 0x400:
            scale = scale - 0x800
        return scale


class CharTypeModifier(TypeModifier):
    """Handle char/varchar type modifier."""

    def get_modifier(self, typemod: int) -> tuple[int, ...] | None:
        dsize = self.get_display_size(typemod)
        return (dsize,) if dsize else None

    def get_display_size(self, typemod: int) -> int | None:
        return typemod - 4 if typemod >= 0 else None


class BitTypeModifier(TypeModifier):
    """Handle bit/varbit type modifier."""

    def get_modifier(self, typemod: int) -> tuple[int, ...] | None:
        dsize = self.get_display_size(typemod)
        return (dsize,) if dsize else None

    def get_display_size(self, typemod: int) -> int | None:
        return typemod if typemod >= 0 else None


class TimeTypeModifier(TypeModifier):
    """Handle time-related types modifier."""

    def get_modifier(self, typemod: int) -> tuple[int, ...] | None:
        prec = self.get_precision(typemod)
        return (prec,) if prec is not None else None

    def get_precision(self, typemod: int) -> int | None:
        return typemod & 0xFFFF if typemod >= 0 else None
