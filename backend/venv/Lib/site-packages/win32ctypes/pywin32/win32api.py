#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
""" A module, encapsulating the Windows Win32 API. """
from win32ctypes.core import (
    _common, _dll, _resource, _system_information, _backend, _time)
from win32ctypes.pywin32.pywintypes import pywin32error as _pywin32error

LOAD_LIBRARY_AS_DATAFILE = 0x2
LANG_NEUTRAL = 0x00


def LoadLibraryEx(fileName, handle, flags):
    """ Loads the specified DLL, and returns the handle.

    Parameters
    ----------
    fileName : unicode
        The filename of the module to load.

    handle : int
        Reserved, always zero.

    flags : int
        The action to be taken when loading the module.

    Returns
    -------
    handle : hModule
        The handle of the loaded module

    """
    if not handle == 0:
        raise ValueError("handle != 0 not supported")
    with _pywin32error():
        return _dll._LoadLibraryEx(fileName, 0, flags)


def EnumResourceTypes(hModule):
    """ Enumerates resource types within a module.

    Parameters
    ----------
    hModule : handle
        The handle to the module.

    Returns
    -------
    resource_types : list
       The list of resource types in the module.

    """
    resource_types = []

    def callback(hModule, type_, param):
        resource_types.append(type_)
        return True

    with _pywin32error():
        _resource._EnumResourceTypes(
            hModule, _resource.ENUMRESTYPEPROC(callback), 0)
    return resource_types


def EnumResourceNames(hModule, resType):
    """ Enumerates all the resources of the specified type within a module.

    Parameters
    ----------
    hModule : handle
        The handle to the module.
    resType : str : int
        The type or id of resource to enumerate.

    Returns
    -------
    resource_names : list
       The list of resource names (unicode strings) of the specific
       resource type in the module.

    """
    resource_names = []

    def callback(hModule, type_, type_name, param):
        resource_names.append(type_name)
        return True

    with _pywin32error():
        _resource._EnumResourceNames(
            hModule, resType, _resource.ENUMRESNAMEPROC(callback), 0)
    return resource_names


def EnumResourceLanguages(hModule, lpType, lpName):
    """ List languages of a resource module.

    Parameters
    ----------
    hModule : handle
        Handle to the resource module.

    lpType : str : int
        The type or id of resource to enumerate.

    lpName : str : int
        The type or id of resource to enumerate.

    Returns
    -------
    resource_languages : list
        List of the resource language ids.

    """
    resource_languages = []

    def callback(hModule, type_name, res_name, language_id, param):
        resource_languages.append(language_id)
        return True

    with _pywin32error():
        _resource._EnumResourceLanguages(
            hModule, lpType, lpName, _resource.ENUMRESLANGPROC(callback), 0)
    return resource_languages


def LoadResource(hModule, type, name, language=LANG_NEUTRAL):
    """ Find and Load a resource component.

    Parameters
    ----------
    handle : hModule
        The handle of the module containing the resource.
        Use None for current process executable.

    type : str : int
        The type of resource to load.

    name : str : int
        The name or Id of the resource to load.

    language : int
        Language to use, default is LANG_NEUTRAL.

    Returns
    -------
    resource : bytes
        The byte string blob of the resource

    """
    with _pywin32error():
        hrsrc = _resource._FindResourceEx(hModule, type, name, language)
        size = _resource._SizeofResource(hModule, hrsrc)
        hglob = _resource._LoadResource(hModule, hrsrc)
        if _backend == 'ctypes':
            pointer = _common.cast(
                _resource._LockResource(hglob), _common.c_char_p)
        else:
            pointer = _resource._LockResource(hglob)
        return _common._PyBytes_FromStringAndSize(pointer, size)


def FreeLibrary(hModule):
    """ Free the loaded dynamic-link library (DLL) module.

    If necessary, decrements its reference count.

    Parameters
    ----------
    handle : hModule
        The handle to the library as returned by the LoadLibrary function.

    """
    with _pywin32error():
        return _dll._FreeLibrary(hModule)


def GetTickCount():
    """ The number of milliseconds that have elapsed since startup

    Returns
    -------
    counts : int
        The millisecond counts since system startup.
    """
    return _time._GetTickCount()


def BeginUpdateResource(filename, delete):
    """ Get a handle that can be used by the :func:`UpdateResource`.

    Parameters
    ----------
    fileName : unicode
        The filename of the module to load.
    delete : bool
        When true all existing resources are deleted

    Returns
    -------
    result : hModule
        Handle of the resource.

    """
    with _pywin32error():
        return _resource._BeginUpdateResource(filename, delete)


def EndUpdateResource(handle, discard):
    """ End the update resource of the handle.

    Parameters
    ----------
    handle : hModule
        The handle of the resource as it is returned
        by :func:`BeginUpdateResource`

    discard : bool
        When True all writes are discarded.

    """
    with _pywin32error():
        _resource._EndUpdateResource(handle, discard)


def UpdateResource(handle, type, name, data, language=LANG_NEUTRAL):
    """ Update a resource.

    Parameters
    ----------
    handle : hModule
        The handle of the resource file as returned by
        :func:`BeginUpdateResource`.

    type : str : int
        The type of resource to update.

    name : str : int
        The name or Id of the resource to update.

    data : bytes
        A bytes like object is expected.

        .. note::
          PyWin32 version 219, on Python 2.7, can handle unicode inputs.
          However, the data are stored as bytes and it is not really
          possible to convert the information back into the original
          unicode string. To be consistent with the Python 3 behaviour
          of PyWin32, we raise an error if the input cannot be
          converted to `bytes`.

    language : int
        Language to use, default is LANG_NEUTRAL.

    """
    with _pywin32error():
        try:
            lp_data = bytes(data)
        except UnicodeEncodeError:
            raise TypeError(
                "a bytes-like object is required, not a 'unicode'")
        _resource._UpdateResource(
            handle, type, name, language, lp_data, len(lp_data))


def GetWindowsDirectory():
    """ Get the ``Windows`` directory.

    Returns
    -------
    result : str
        The path to the ``Windows`` directory.

    """
    with _pywin32error():
        # Note: pywin32 returns str on py27, unicode (which is str) on py3
        return str(_system_information._GetWindowsDirectory())


def GetSystemDirectory():
    """ Get the ``System`` directory.

    Returns
    -------
    result : str
        The path to the ``System`` directory.

    """
    with _pywin32error():
        # Note: pywin32 returns str on py27, unicode (which is str) on py3
        return str(_system_information._GetSystemDirectory())
