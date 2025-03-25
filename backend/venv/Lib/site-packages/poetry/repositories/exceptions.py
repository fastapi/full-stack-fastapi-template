from __future__ import annotations


class RepositoryError(Exception):
    pass


class PackageNotFoundError(Exception):
    pass


class InvalidSourceError(Exception):
    pass
