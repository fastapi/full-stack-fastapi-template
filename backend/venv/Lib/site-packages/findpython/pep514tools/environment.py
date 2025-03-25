# -------------------------------------------------------------------------
# Copyright (c) Steve Dower
# All rights reserved.
#
# Distributed under the terms of the MIT License
# -------------------------------------------------------------------------

__all__ = ["Environment", "findall", "find", "findone"]

import sys

from findpython.pep514tools._registry import (
    REGISTRY_SOURCE_CU,
    REGISTRY_SOURCE_LM,
    REGISTRY_SOURCE_LM_WOW6432,
    open_source,
)

# These tags are treated specially when the Company is 'PythonCore'
_PYTHONCORE_COMPATIBILITY_TAGS = {
    "2.0",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.0",
    "3.1",
    "3.2",
    "3.3",
    "3.4",
}

_IS_64BIT_OS = None


def _is_64bit_os():
    global _IS_64BIT_OS
    if _IS_64BIT_OS is None:
        if sys.maxsize > 2**32:
            import platform

            _IS_64BIT_OS = platform.machine() == "AMD64"
        else:
            _IS_64BIT_OS = False
    return _IS_64BIT_OS


class Environment(object):
    def __init__(self, source, company, tag, guessed_arch=None):
        self._source = source
        self.company = company
        self.tag = tag
        self._guessed_arch = guessed_arch
        self._orig_info = company, tag
        self.info = {}

    def load(self):
        if not self._source:
            raise ValueError("Environment not initialized with a source")
        self.info = info = self._source[self.company][self.tag].get_all_values()
        if self.company == "PythonCore":
            info._setdefault("DisplayName", "Python " + self.tag)
            info._setdefault("SupportUrl", "http://www.python.org/")
            info._setdefault("Version", self.tag[:3])
            info._setdefault("SysVersion", self.tag[:3])
            if self._guessed_arch:
                info._setdefault("SysArchitecture", self._guessed_arch)

    def save(self, copy=False):
        if not self._source:
            raise ValueError("Environment not initialized with a source")
        if (self.company, self.tag) != self._orig_info:
            if not copy:
                self._source[self._orig_info[0]][self._orig_info[1]].delete()
            self._orig_info = self.company, self.tag

        src = self._source[self.company][self.tag]
        src.set_all_values(self.info)

        self.info = src.get_all_values()

    def delete(self):
        if (self.company, self.tag) != self._orig_info:
            raise ValueError(
                "cannot delete Environment when company/tag have been modified"
            )

        if not self._source:
            raise ValueError("Environment not initialized with a source")
        self._source.delete()

    def __repr__(self):
        return "<environment {}\\{}>".format(self.company, self.tag)


def _get_sources(include_per_machine=True, include_per_user=True):
    if _is_64bit_os():
        if include_per_user:
            yield open_source(REGISTRY_SOURCE_CU), None
        if include_per_machine:
            yield open_source(REGISTRY_SOURCE_LM), "64bit"
            yield open_source(REGISTRY_SOURCE_LM_WOW6432), "32bit"
    else:
        if include_per_user:
            yield open_source(REGISTRY_SOURCE_CU), "32bit"
        if include_per_machine:
            yield open_source(REGISTRY_SOURCE_LM), "32bit"


def findall(include_per_machine=True, include_per_user=True):
    for src, arch in _get_sources(
        include_per_machine=include_per_machine, include_per_user=include_per_user
    ):
        for company in src:
            for tag in company:
                try:
                    env = Environment(src, company.name, tag.name, arch)
                    env.load()
                except OSError:
                    pass
                else:
                    yield env


def find(
    company_or_tag,
    tag=None,
    include_per_machine=True,
    include_per_user=True,
    maxcount=None,
):
    if not tag:
        env = Environment(None, "PythonCore", company_or_tag)
    else:
        env = Environment(None, company_or_tag, tag)

    results = []
    for src, arch in _get_sources(
        include_per_machine=include_per_machine, include_per_user=include_per_user
    ):
        try:
            env._source = src
            env._guessed_arch = arch
            env.load()
        except OSError:
            pass
        else:
            results.append(env)
    return results


def findone(company_or_tag, tag=None, include_per_machine=True, include_per_user=True):
    found = find(company_or_tag, tag, include_per_machine, include_per_user, maxcount=1)
    if found:
        return found[0]
