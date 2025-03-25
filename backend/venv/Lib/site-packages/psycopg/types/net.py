"""
Adapters for network types.
"""

# Copyright (C) 2020 The Psycopg Team

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .. import _oids
from ..pq import Format
from ..abc import AdaptContext
from ..adapt import Buffer, Dumper, Loader
from .._compat import TypeAlias

if TYPE_CHECKING:
    import ipaddress

Address: TypeAlias = "ipaddress.IPv4Address | ipaddress.IPv6Address"
Interface: TypeAlias = "ipaddress.IPv4Interface | ipaddress.IPv6Interface"
Network: TypeAlias = "ipaddress.IPv4Network | ipaddress.IPv6Network"

# These objects will be imported lazily
ip_address: Callable[[str], Address] = None  # type: ignore[assignment]
ip_interface: Callable[[str], Interface] = None  # type: ignore[assignment]
ip_network: Callable[[str], Network] = None  # type: ignore[assignment]
IPv4Address: type[ipaddress.IPv4Address] = None  # type: ignore[assignment]
IPv6Address: type[ipaddress.IPv6Address] = None  # type: ignore[assignment]
IPv4Interface: type[ipaddress.IPv4Interface] = None  # type: ignore[assignment]
IPv6Interface: type[ipaddress.IPv6Interface] = None  # type: ignore[assignment]
IPv4Network: type[ipaddress.IPv4Network] = None  # type: ignore[assignment]
IPv6Network: type[ipaddress.IPv6Network] = None  # type: ignore[assignment]

PGSQL_AF_INET = 2
PGSQL_AF_INET6 = 3
IPV4_PREFIXLEN = 32
IPV6_PREFIXLEN = 128


class _LazyIpaddress:
    def _ensure_module(self) -> None:
        global ip_address, ip_interface, ip_network
        global IPv4Address, IPv6Address, IPv4Interface, IPv6Interface
        global IPv4Network, IPv6Network

        if ip_address is None:
            from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address
            from ipaddress import IPv6Interface, IPv6Network, ip_address, ip_interface
            from ipaddress import ip_network


class InterfaceDumper(Dumper):
    oid = _oids.INET_OID

    def dump(self, obj: Interface) -> Buffer | None:
        return str(obj).encode()


class NetworkDumper(Dumper):
    oid = _oids.CIDR_OID

    def dump(self, obj: Network) -> Buffer | None:
        return str(obj).encode()


class _AIBinaryDumper(Dumper):
    format = Format.BINARY
    oid = _oids.INET_OID


class AddressBinaryDumper(_AIBinaryDumper):
    def dump(self, obj: Address) -> Buffer | None:
        packed = obj.packed
        family = PGSQL_AF_INET if obj.version == 4 else PGSQL_AF_INET6
        head = bytes((family, obj.max_prefixlen, 0, len(packed)))
        return head + packed


class InterfaceBinaryDumper(_AIBinaryDumper):
    def dump(self, obj: Interface) -> Buffer | None:
        packed = obj.packed
        family = PGSQL_AF_INET if obj.version == 4 else PGSQL_AF_INET6
        head = bytes((family, obj.network.prefixlen, 0, len(packed)))
        return head + packed


class InetBinaryDumper(_AIBinaryDumper, _LazyIpaddress):
    """Either an address or an interface to inet

    Used when looking up by oid.
    """

    def __init__(self, cls: type, context: AdaptContext | None = None):
        super().__init__(cls, context)
        self._ensure_module()

    def dump(self, obj: Address | Interface) -> Buffer | None:
        packed = obj.packed
        family = PGSQL_AF_INET if obj.version == 4 else PGSQL_AF_INET6
        if isinstance(obj, (IPv4Interface, IPv6Interface)):
            prefixlen = obj.network.prefixlen
        else:
            prefixlen = obj.max_prefixlen

        head = bytes((family, prefixlen, 0, len(packed)))
        return head + packed


class NetworkBinaryDumper(Dumper):
    format = Format.BINARY
    oid = _oids.CIDR_OID

    def dump(self, obj: Network) -> Buffer | None:
        packed = obj.network_address.packed
        family = PGSQL_AF_INET if obj.version == 4 else PGSQL_AF_INET6
        head = bytes((family, obj.prefixlen, 1, len(packed)))
        return head + packed


class _LazyIpaddressLoader(Loader, _LazyIpaddress):
    def __init__(self, oid: int, context: AdaptContext | None = None):
        super().__init__(oid, context)
        self._ensure_module()


class InetLoader(_LazyIpaddressLoader):
    def load(self, data: Buffer) -> Address | Interface:
        if isinstance(data, memoryview):
            data = bytes(data)

        if b"/" in data:
            return ip_interface(data.decode())
        else:
            return ip_address(data.decode())


class InetBinaryLoader(_LazyIpaddressLoader):
    format = Format.BINARY

    def load(self, data: Buffer) -> Address | Interface:
        if isinstance(data, memoryview):
            data = bytes(data)

        prefix = data[1]
        packed = data[4:]
        if data[0] == PGSQL_AF_INET:
            if prefix == IPV4_PREFIXLEN:
                return IPv4Address(packed)
            else:
                return IPv4Interface((packed, prefix))
        else:
            if prefix == IPV6_PREFIXLEN:
                return IPv6Address(packed)
            else:
                return IPv6Interface((packed, prefix))


class CidrLoader(_LazyIpaddressLoader):
    def load(self, data: Buffer) -> Network:
        if isinstance(data, memoryview):
            data = bytes(data)

        return ip_network(data.decode())


class CidrBinaryLoader(_LazyIpaddressLoader):
    format = Format.BINARY

    def load(self, data: Buffer) -> Network:
        if isinstance(data, memoryview):
            data = bytes(data)

        prefix = data[1]
        packed = data[4:]
        if data[0] == PGSQL_AF_INET:
            return IPv4Network((packed, prefix))
        else:
            return IPv6Network((packed, prefix))

        return ip_network(data.decode())


def register_default_adapters(context: AdaptContext) -> None:
    adapters = context.adapters
    adapters.register_dumper("ipaddress.IPv4Address", InterfaceDumper)
    adapters.register_dumper("ipaddress.IPv6Address", InterfaceDumper)
    adapters.register_dumper("ipaddress.IPv4Interface", InterfaceDumper)
    adapters.register_dumper("ipaddress.IPv6Interface", InterfaceDumper)
    adapters.register_dumper("ipaddress.IPv4Network", NetworkDumper)
    adapters.register_dumper("ipaddress.IPv6Network", NetworkDumper)
    adapters.register_dumper("ipaddress.IPv4Address", AddressBinaryDumper)
    adapters.register_dumper("ipaddress.IPv6Address", AddressBinaryDumper)
    adapters.register_dumper("ipaddress.IPv4Interface", InterfaceBinaryDumper)
    adapters.register_dumper("ipaddress.IPv6Interface", InterfaceBinaryDumper)
    adapters.register_dumper("ipaddress.IPv4Network", NetworkBinaryDumper)
    adapters.register_dumper("ipaddress.IPv6Network", NetworkBinaryDumper)
    adapters.register_dumper(None, InetBinaryDumper)
    adapters.register_loader("inet", InetLoader)
    adapters.register_loader("inet", InetBinaryLoader)
    adapters.register_loader("cidr", CidrLoader)
    adapters.register_loader("cidr", CidrBinaryLoader)
