"""
Mapping from types/oids to Dumpers/Loaders
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from . import errors as e
from . import pq
from .abc import Dumper, Loader
from ._enums import PyFormat as PyFormat
from ._compat import TypeVar
from ._cmodule import _psycopg
from ._typeinfo import TypesRegistry

if TYPE_CHECKING:
    from ._connection_base import BaseConnection

RV = TypeVar("RV")


class AdaptersMap:
    r"""
    Establish how types should be converted between Python and PostgreSQL in
    an `~psycopg.abc.AdaptContext`.

    `!AdaptersMap` maps Python types to `~psycopg.adapt.Dumper` classes to
    define how Python types are converted to PostgreSQL, and maps OIDs to
    `~psycopg.adapt.Loader` classes to establish how query results are
    converted to Python.

    Every `!AdaptContext` object has an underlying `!AdaptersMap` defining how
    types are converted in that context, exposed as the
    `~psycopg.abc.AdaptContext.adapters` attribute: changing such map allows
    to customise adaptation in a context without changing separated contexts.

    When a context is created from another context (for instance when a
    `~psycopg.Cursor` is created from a `~psycopg.Connection`), the parent's
    `!adapters` are used as template for the child's `!adapters`, so that every
    cursor created from the same connection use the connection's types
    configuration, but separate connections have independent mappings.

    Once created, `!AdaptersMap` are independent. This means that objects
    already created are not affected if a wider scope (e.g. the global one) is
    changed.

    The connections adapters are initialised using a global `!AdptersMap`
    template, exposed as `psycopg.adapters`: changing such mapping allows to
    customise the type mapping for every connections created afterwards.

    The object can start empty or copy from another object of the same class.
    Copies are copy-on-write: if the maps are updated make a copy. This way
    extending e.g. global map by a connection or a connection map from a cursor
    is cheap: a copy is only made on customisation.
    """

    __module__ = "psycopg.adapt"

    types: TypesRegistry

    _dumpers: dict[PyFormat, dict[type | str, type[Dumper]]]
    _dumpers_by_oid: list[dict[int, type[Dumper]]]
    _loaders: list[dict[int, type[Loader]]]

    # Record if a dumper or loader has an optimised version.
    _optimised: dict[type, type] = {}

    def __init__(
        self,
        template: AdaptersMap | None = None,
        types: TypesRegistry | None = None,
    ):
        if template:
            self._dumpers = template._dumpers.copy()
            self._own_dumpers = _dumpers_shared.copy()
            template._own_dumpers = _dumpers_shared.copy()

            self._dumpers_by_oid = template._dumpers_by_oid[:]
            self._own_dumpers_by_oid = [False, False]
            template._own_dumpers_by_oid = [False, False]

            self._loaders = template._loaders[:]
            self._own_loaders = [False, False]
            template._own_loaders = [False, False]

            self.types = TypesRegistry(template.types)

        else:
            self._dumpers = {fmt: {} for fmt in PyFormat}
            self._own_dumpers = _dumpers_owned.copy()

            self._dumpers_by_oid = [{}, {}]
            self._own_dumpers_by_oid = [True, True]

            self._loaders = [{}, {}]
            self._own_loaders = [True, True]

            self.types = types or TypesRegistry()

    # implement the AdaptContext protocol too
    @property
    def adapters(self) -> AdaptersMap:
        return self

    @property
    def connection(self) -> BaseConnection[Any] | None:
        return None

    def register_dumper(self, cls: type | str | None, dumper: type[Dumper]) -> None:
        """
        Configure the context to use `!dumper` to convert objects of type `!cls`.

        If two dumpers with different `~Dumper.format` are registered for the
        same type, the last one registered will be chosen when the query
        doesn't specify a format (i.e. when the value is used with a ``%s``
        "`~PyFormat.AUTO`" placeholder).

        :param cls: The type to manage.
        :param dumper: The dumper to register for `!cls`.

        If `!cls` is specified as string it will be lazy-loaded, so that it
        will be possible to register it without importing it before. In this
        case it should be the fully qualified name of the object (e.g.
        ``"uuid.UUID"``).

        If `!cls` is None, only use the dumper when looking up using
        `get_dumper_by_oid()`, which happens when we know the Postgres type to
        adapt to, but not the Python type that will be adapted (e.g. in COPY
        after using `~psycopg.Copy.set_types()`).

        """
        if not (cls is None or isinstance(cls, (str, type))):
            raise TypeError(
                f"dumpers should be registered on classes, got {cls} instead"
            )

        if _psycopg:
            dumper = self._get_optimised(dumper)

        # Register the dumper both as its format and as auto
        # so that the last dumper registered is used in auto (%s) format
        if cls:
            for fmt in (PyFormat.from_pq(dumper.format), PyFormat.AUTO):
                if not self._own_dumpers[fmt]:
                    self._dumpers[fmt] = self._dumpers[fmt].copy()
                    self._own_dumpers[fmt] = True

                self._dumpers[fmt][cls] = dumper

        # Register the dumper by oid, if the oid of the dumper is fixed
        if dumper.oid:
            if not self._own_dumpers_by_oid[dumper.format]:
                self._dumpers_by_oid[dumper.format] = self._dumpers_by_oid[
                    dumper.format
                ].copy()
                self._own_dumpers_by_oid[dumper.format] = True

            self._dumpers_by_oid[dumper.format][dumper.oid] = dumper

    def register_loader(self, oid: int | str, loader: type[Loader]) -> None:
        """
        Configure the context to use `!loader` to convert data of oid `!oid`.

        :param oid: The PostgreSQL OID or type name to manage.
        :param loader: The loar to register for `!oid`.

        If `oid` is specified as string, it refers to a type name, which is
        looked up in the `types` registry.

        """
        if isinstance(oid, str):
            oid = self.types[oid].oid
        if not isinstance(oid, int):
            raise TypeError(f"loaders should be registered on oid, got {oid} instead")

        if _psycopg:
            loader = self._get_optimised(loader)

        fmt = loader.format
        if not self._own_loaders[fmt]:
            self._loaders[fmt] = self._loaders[fmt].copy()
            self._own_loaders[fmt] = True

        self._loaders[fmt][oid] = loader

    def get_dumper(self, cls: type, format: PyFormat) -> type[Dumper]:
        """
        Return the dumper class for the given type and format.

        Raise `~psycopg.ProgrammingError` if a class is not available.

        :param cls: The class to adapt.
        :param format: The format to dump to. If `~psycopg.adapt.PyFormat.AUTO`,
            use the last one of the dumpers registered on `!cls`.
        """
        try:
            # Fast path: the class has a known dumper.
            return self._dumpers[format][cls]
        except KeyError:
            if format not in self._dumpers:
                raise ValueError(f"bad dumper format: {format}")

            # If the KeyError was caused by cls missing from dmap, let's
            # look for different cases.
            dmap = self._dumpers[format]

        # Look for the right class, including looking at superclasses
        for scls in cls.__mro__:
            if scls in dmap:
                return dmap[scls]

            # If the adapter is not found, look for its name as a string
            fqn = scls.__module__ + "." + scls.__qualname__
            if fqn in dmap:
                # Replace the class name with the class itself
                d = dmap[scls] = dmap.pop(fqn)
                return d

        format = PyFormat(format)
        raise e.ProgrammingError(
            f"cannot adapt type {cls.__name__!r} using placeholder '%{format.value}'"
            f" (format: {format.name})"
        )

    def get_dumper_by_oid(self, oid: int, format: pq.Format) -> type[Dumper]:
        """
        Return the dumper class for the given oid and format.

        Raise `~psycopg.ProgrammingError` if a class is not available.

        :param oid: The oid of the type to dump to.
        :param format: The format to dump to.
        """
        try:
            dmap = self._dumpers_by_oid[format]
        except KeyError:
            raise ValueError(f"bad dumper format: {format}")

        try:
            return dmap[oid]
        except KeyError:
            info = self.types.get(oid)
            if info:
                msg = (
                    f"cannot find a dumper for type {info.name} (oid {oid})"
                    f" format {pq.Format(format).name}"
                )
            else:
                msg = (
                    f"cannot find a dumper for unknown type with oid {oid}"
                    f" format {pq.Format(format).name}"
                )
            raise e.ProgrammingError(msg)

    def get_loader(self, oid: int, format: pq.Format) -> type[Loader] | None:
        """
        Return the loader class for the given oid and format.

        Return `!None` if not found.

        :param oid: The oid of the type to load.
        :param format: The format to load from.
        """
        return self._loaders[format].get(oid)

    @classmethod
    def _get_optimised(self, cls: type[RV]) -> type[RV]:
        """Return the optimised version of a Dumper or Loader class.

        Return the input class itself if there is no optimised version.
        """
        try:
            return self._optimised[cls]
        except KeyError:
            pass

        # Check if the class comes from psycopg.types and there is a class
        # with the same name in psycopg_c._psycopg.
        from psycopg import types

        if cls.__module__.startswith(types.__name__):
            new = cast("type[RV]", getattr(_psycopg, cls.__name__, None))
            if new:
                self._optimised[cls] = new
                return new

        self._optimised[cls] = cls
        return cls


# Micro-optimization: copying these objects is faster than creating new dicts
_dumpers_owned = dict.fromkeys(PyFormat, True)
_dumpers_shared = dict.fromkeys(PyFormat, False)
