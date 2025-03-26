"""
Internal objects to support the UUID adapters.
"""

# Copyright (C) 2025 The Psycopg Team

import uuid

# Re-exports
UUID = uuid.UUID
SafeUUID_unknown = uuid.SafeUUID.unknown


class _WritableUUID(UUID):
    """Temporary class, with the same memory layout of UUID, but writable.

    This class must have the same memory layout of the UUID class, so we can
    create one, setting the `int` attribute, and changing the `__class__`,
    which should be faster than calling the complex UUID.__init__ machinery.

        u = _WritableUUID()
        u.is_safe = ...
        u.int = ...
        u.__class__ = UUID
    """

    __slots__ = ()  # Give the class the same memory layout of the base clasee
    __setattr__ = object.__setattr__  # make the class writable
