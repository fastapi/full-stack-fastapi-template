# -------------------------------------------------------------------------
# Copyright (c) Steve Dower
# All rights reserved.
#
# Distributed under the terms of the MIT License
# -------------------------------------------------------------------------

__all__ = [
    "open_source",
    "REGISTRY_SOURCE_LM",
    "REGISTRY_SOURCE_LM_WOW6432",
    "REGISTRY_SOURCE_CU",
]

import re
from itertools import count

try:
    import winreg
except ImportError:
    import _winreg as winreg

REGISTRY_SOURCE_LM = 1
REGISTRY_SOURCE_LM_WOW6432 = 2
REGISTRY_SOURCE_CU = 3

_REG_KEY_INFO = {
    REGISTRY_SOURCE_LM: (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Python",
        winreg.KEY_WOW64_64KEY,
    ),
    REGISTRY_SOURCE_LM_WOW6432: (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Python",
        winreg.KEY_WOW64_32KEY,
    ),
    REGISTRY_SOURCE_CU: (winreg.HKEY_CURRENT_USER, r"Software\Python", 0),
}


def get_value_from_tuple(value, vtype):
    if vtype == winreg.REG_SZ:
        if "\0" in value:
            return value[: value.index("\0")]
        return value
    return None


def join(x, y):
    return x + "\\" + y


_VALID_ATTR = re.compile("^[a-z_]+$")
_VALID_KEY = re.compile("^[A-Za-z]+$")
_KEY_TO_ATTR = re.compile("([A-Z]+[a-z]+)")


class PythonWrappedDict(object):
    @staticmethod
    def _attr_to_key(attr):
        if not attr:
            return ""
        if not _VALID_ATTR.match(attr):
            return attr
        return "".join(c.capitalize() for c in attr.split("_"))

    @staticmethod
    def _key_to_attr(key):
        if not key:
            return ""
        if not _VALID_KEY.match(key):
            return key
        return "_".join(k for k in _KEY_TO_ATTR.split(key) if k).lower()

    def __init__(self, d):
        self._d = d

    def __getattr__(self, attr):
        if attr.startswith("_"):
            return object.__getattribute__(self, attr)

        if attr == "value":
            attr = ""

        key = self._attr_to_key(attr)
        try:
            return self._d[key]
        except Exception:
            pass
        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            return object.__setattr__(self, attr, value)

        if attr == "value":
            attr = ""
        self._d[self._attr_to_key(attr)] = value

    def __dir__(self):
        k2a = self._key_to_attr
        return list(map(k2a, self._d))

    def _setdefault(self, key, value):
        self._d.setdefault(key, value)

    def _items(self):
        return self._d.items()

    def __repr__(self):
        k2a = self._key_to_attr
        return (
            "info("
            + ", ".join("{}={!r}".format(k2a(k), v) for k, v in self._d.items())
            + ")"
        )


class RegistryAccessor(object):
    def __init__(self, root, subkey, flags):
        self._root = root
        self.subkey = subkey
        _, _, self.name = subkey.rpartition("\\")
        self._flags = flags

    def __iter__(self):
        subkey_names = []
        try:
            with winreg.OpenKeyEx(
                self._root, self.subkey, 0, winreg.KEY_READ | self._flags
            ) as key:
                for i in count():
                    subkey_names.append(winreg.EnumKey(key, i))
        except OSError:
            pass
        return iter(self[k] for k in subkey_names)

    def __getitem__(self, key):
        return RegistryAccessor(self._root, join(self.subkey, key), self._flags)

    def get_value(self, value_name):
        try:
            with winreg.OpenKeyEx(
                self._root, self.subkey, 0, winreg.KEY_READ | self._flags
            ) as key:
                return get_value_from_tuple(*winreg.QueryValueEx(key, value_name))
        except OSError:
            return None

    def get_all_values(self):
        schema = {}
        for subkey in self:
            schema[subkey.name] = subkey.get_all_values()

        key = winreg.OpenKeyEx(self._root, self.subkey, 0, winreg.KEY_READ | self._flags)
        try:
            with key:
                for i in count():
                    vname, value, vtype = winreg.EnumValue(key, i)
                    value = get_value_from_tuple(value, vtype)
                    if value:
                        schema[vname or ""] = value
        except OSError:
            pass

        return PythonWrappedDict(schema)

    def set_value(self, value_name, value):
        with winreg.CreateKeyEx(
            self._root, self.subkey, 0, winreg.KEY_WRITE | self._flags
        ) as key:
            if value is None:
                winreg.DeleteValue(key, value_name)
            elif isinstance(value, str):
                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
            else:
                raise TypeError("cannot write {} to registry".format(type(value)))

    def _set_all_values(self, rootkey, name, info, errors):
        with winreg.CreateKeyEx(rootkey, name, 0, winreg.KEY_WRITE | self._flags) as key:
            for k, v in info:
                if isinstance(v, PythonWrappedDict):
                    self._set_all_values(key, k, v._items(), errors)
                elif isinstance(v, dict):
                    self._set_all_values(key, k, v.items(), errors)
                elif v is None:
                    winreg.DeleteValue(key, k)
                elif isinstance(v, str):
                    winreg.SetValueEx(key, k, 0, winreg.REG_SZ, v)
                else:
                    errors.append("cannot write {} to registry".format(type(v)))

    def set_all_values(self, info):
        errors = []
        if isinstance(info, PythonWrappedDict):
            items = info._items()
        elif isinstance(info, dict):
            items = info.items()
        else:
            raise TypeError("info must be a dictionary")

        self._set_all_values(self._root, self.subkey, items, errors)
        if len(errors) == 1:
            raise ValueError(errors[0])
        elif errors:
            raise ValueError(errors)

    def delete(self):
        for k in self:
            k.delete()
        try:
            key = winreg.OpenKeyEx(self._root, None, 0, winreg.KEY_READ | self._flags)
        except OSError:
            return
        with key:
            winreg.DeleteKeyEx(key, self.subkey)


def open_source(registry_source):
    info = _REG_KEY_INFO.get(registry_source)
    if not info:
        raise ValueError("unsupported registry source")
    root, subkey, flags = info
    return RegistryAccessor(root, subkey, flags)
