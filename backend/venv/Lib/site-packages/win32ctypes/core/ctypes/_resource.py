#
# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import ctypes
from ctypes.wintypes import (
    BOOL, DWORD, HANDLE, HMODULE, LPCWSTR, WORD, HRSRC,
    HGLOBAL, LPVOID)

from ._common import LONG_PTR, IS_INTRESOURCE
from ._util import check_null, check_zero, check_false, function_factory, dlls

_ENUMRESTYPEPROC = ctypes.WINFUNCTYPE(BOOL, HMODULE, LPVOID, LONG_PTR)
_ENUMRESNAMEPROC = ctypes.WINFUNCTYPE(BOOL, HMODULE, LPVOID, LPVOID, LONG_PTR)
_ENUMRESLANGPROC = ctypes.WINFUNCTYPE(
    BOOL, HMODULE, LPVOID, LPVOID, WORD, LONG_PTR)


def ENUMRESTYPEPROC(callback):
    def wrapped(handle, type_, param):
        if IS_INTRESOURCE(type_):
            type_ = int(type_)
        else:
            type_ = ctypes.cast(type_, LPCWSTR).value
        return callback(handle, type_, param)

    return _ENUMRESTYPEPROC(wrapped)


def ENUMRESNAMEPROC(callback):
    def wrapped(handle, type_, name, param):
        if IS_INTRESOURCE(type_):
            type_ = int(type_)
        else:
            type_ = ctypes.cast(type_, LPCWSTR).value
        if name is None:
            return False
        elif IS_INTRESOURCE(name):
            name = int(name)
        else:
            name = ctypes.cast(name, LPCWSTR).value
        return callback(handle, type_, name, param)

    return _ENUMRESNAMEPROC(wrapped)


def ENUMRESLANGPROC(callback):
    def wrapped(handle, type_, name, language, param):
        if IS_INTRESOURCE(type_):
            type_ = int(type_)
        else:
            type_ = ctypes.cast(type_, LPCWSTR).value
        if IS_INTRESOURCE(name):
            name = int(name)
        else:
            name = ctypes.cast(name, LPCWSTR).value
        return callback(handle, type_, name, language, param)

    return _ENUMRESLANGPROC(wrapped)


def _UpdateResource(hUpdate, lpType, lpName, wLanguage, lpData, cbData):
    lp_type = LPCWSTR(lpType)
    lp_name = LPCWSTR(lpName)
    _BaseUpdateResource(hUpdate, lp_type, lp_name, wLanguage, lpData, cbData)


def _EnumResourceNames(hModule, lpszType, lpEnumFunc, lParam):
    resource_type = LPCWSTR(lpszType)
    _BaseEnumResourceNames(hModule, resource_type, lpEnumFunc, lParam)


def _EnumResourceLanguages(hModule, lpType, lpName, lpEnumFunc, lParam):
    resource_type = LPCWSTR(lpType)
    resource_name = LPCWSTR(lpName)
    _BaseEnumResourceLanguages(
        hModule, resource_type, resource_name, lpEnumFunc, lParam)


def _FindResourceEx(hModule, lpType, lpName, wLanguage):
    resource_type = LPCWSTR(lpType)
    resource_name = LPCWSTR(lpName)
    return _BaseFindResourceEx(
        hModule, resource_type, resource_name, wLanguage)


_EnumResourceTypes = function_factory(
    dlls.kernel32.EnumResourceTypesW,
    [HMODULE, _ENUMRESTYPEPROC, LONG_PTR],
    BOOL,
    check_false)

_LoadResource = function_factory(
    dlls.kernel32.LoadResource,
    [HMODULE, HRSRC],
    HGLOBAL,
    check_null)

_LockResource = function_factory(
    dlls.kernel32.LockResource,
    [HGLOBAL],
    LPVOID,
    check_null)

_SizeofResource = function_factory(
    dlls.kernel32.SizeofResource,
    [HMODULE, HRSRC],
    DWORD,
    check_zero)

_BeginUpdateResource = function_factory(
    dlls.kernel32.BeginUpdateResourceW,
    [LPCWSTR, BOOL],
    HANDLE,
    check_null)

_EndUpdateResource = function_factory(
    dlls.kernel32.EndUpdateResourceW,
    [HANDLE, BOOL],
    BOOL,
    check_false)

_BaseEnumResourceNames = function_factory(
    dlls.kernel32.EnumResourceNamesW,
    [HMODULE, LPCWSTR, _ENUMRESNAMEPROC, LONG_PTR],
    BOOL,
    check_false)

_BaseEnumResourceLanguages = function_factory(
    dlls.kernel32.EnumResourceLanguagesW,
    [HMODULE, LPCWSTR, LPCWSTR, _ENUMRESLANGPROC, LONG_PTR],
    BOOL,
    check_false)

_BaseFindResourceEx = function_factory(
    dlls.kernel32.FindResourceExW,
    [HMODULE, LPCWSTR, LPCWSTR, WORD],
    HRSRC,
    check_null)

_BaseUpdateResource = function_factory(
    dlls.kernel32.UpdateResourceW,
    [HANDLE, LPCWSTR, LPCWSTR, WORD, LPVOID, DWORD],
    BOOL,
    check_false)
