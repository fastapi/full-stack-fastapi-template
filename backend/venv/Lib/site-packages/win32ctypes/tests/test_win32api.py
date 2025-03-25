#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import os
import sys
import unittest
import contextlib
import tempfile
import shutil
import faulthandler

import win32api


from win32ctypes import pywin32
from win32ctypes.pywin32.pywintypes import error


skip_on_wine = 'SKIP_WINE_KNOWN_FAILURES' in os.environ


class TestWin32API(unittest.TestCase):

    # the pywin32ctypes implementation
    module = pywin32.win32api

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        shutil.copy(sys.executable, self.tempdir)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @contextlib.contextmanager
    def load_library(self, module, library=sys.executable, flags=0x2):
        handle = module.LoadLibraryEx(library, 0, flags)
        try:
            yield handle
        finally:
            module.FreeLibrary(handle)

    @contextlib.contextmanager
    def resource_update(self, module, library=sys.executable):
        handle = module.BeginUpdateResource(library, False)
        try:
            yield handle
        finally:
            module.EndUpdateResource(handle, False)

    @contextlib.contextmanager
    def nofaulthandler(self):
        """ Disable the faulthander

            Use this function to avoid poluting the output with errors
            When it is known that an access violation is expected.

        """
        enabled = faulthandler.is_enabled()
        faulthandler.disable()
        try:
            yield
        finally:
            if enabled:
                faulthandler.enable()

    def test_load_library_ex(self):
        with self.load_library(win32api) as expected:
            with self.load_library(self.module) as handle:
                self.assertEqual(handle, expected)

        with self.assertRaises(error):
            self.module.LoadLibraryEx(u'ttt.dll', 0, 0x2)

    def test_free_library(self):
        with self.load_library(win32api) as handle:
            self.assertTrue(win32api.FreeLibrary(handle) is None)
            self.assertNotEqual(self.module.FreeLibrary(handle), 0)

        with self.assertRaises(error):
            with self.nofaulthandler():
                self.module.FreeLibrary(-3)

    def test_enum_resource_types(self):
        with self.load_library(win32api, u'shell32.dll') as handle:
            expected = win32api.EnumResourceTypes(handle)

        with self.load_library(pywin32.win32api, u'shell32.dll') as handle:
            resource_types = self.module.EnumResourceTypes(handle)

        self.assertEqual(resource_types, expected)

        with self.assertRaises(error):
            with self.nofaulthandler():
                self.module.EnumResourceTypes(-3)

    def test_enum_resource_names(self):
        with self.load_library(win32api, u'shell32.dll') as handle:
            resource_types = win32api.EnumResourceTypes(handle)
            for resource_type in resource_types:
                expected = win32api.EnumResourceNames(handle, resource_type)
                resource_names = self.module.EnumResourceNames(
                    handle, resource_type)
                self.assertEqual(resource_names, expected)
                # check that the #<index> format works
                resource_names = self.module.EnumResourceNames(
                    handle, self._id2str(resource_type))
                self.assertEqual(resource_names, expected)

        with self.assertRaises(error):
            self.module.EnumResourceNames(2, 3)

    def test_enum_resource_languages(self):
        with self.load_library(win32api, u'shell32.dll') as handle:
            resource_types = win32api.EnumResourceTypes(handle)
            for resource_type in resource_types:
                resource_names = win32api.EnumResourceNames(
                    handle, resource_type)
                for resource_name in resource_names:
                    expected = win32api.EnumResourceLanguages(
                        handle, resource_type, resource_name)
                    resource_languages = self.module.EnumResourceLanguages(
                        handle, resource_type, resource_name)
                    self.assertEqual(resource_languages, expected)
                    # check that the #<index> format works
                    resource_languages = self.module.EnumResourceLanguages(
                        handle, self._id2str(resource_type),
                        self._id2str(resource_name))
                    self.assertEqual(resource_languages, expected)

        with self.assertRaises(error):
            self.module.EnumResourceLanguages(handle, resource_type, 2235)

    def test_load_resource(self):
        with self.load_library(win32api, u'explorer.exe') as handle:
            resource_types = win32api.EnumResourceTypes(handle)
            for resource_type in resource_types:
                resource_names = win32api.EnumResourceNames(
                    handle, resource_type)
                for resource_name in resource_names:
                    resource_languages = win32api.EnumResourceLanguages(
                        handle, resource_type, resource_name)
                    for resource_language in resource_languages:
                        expected = win32api.LoadResource(
                            handle, resource_type, resource_name,
                            resource_language)
                        resource = self.module.LoadResource(
                            handle, resource_type, resource_name,
                            resource_language)
                        # check that the #<index> format works
                        resource = self.module.LoadResource(
                            handle, self._id2str(resource_type),
                            self._id2str(resource_name),
                            resource_language)
                        self.assertEqual(resource, expected)

        with self.assertRaises(error):
            with self.nofaulthandler():
                self.module.LoadResource(
                    handle, resource_type, resource_name, 12435)

    def test_get_tick_count(self):
        self.assertGreater(self.module.GetTickCount(), 0.0)

    def test_begin_and_end_update_resource(self):
        # given
        module = self.module
        filename = os.path.join(self.tempdir, 'python.exe')
        with self.load_library(module, filename) as handle:
            count = len(module.EnumResourceTypes(handle))

        # when
        handle = module.BeginUpdateResource(filename, False)
        module.EndUpdateResource(handle, False)

        # then
        with self.load_library(module, filename) as handle:
            self.assertEqual(len(module.EnumResourceTypes(handle)), count)

        # when
        handle = module.BeginUpdateResource(filename, True)
        module.EndUpdateResource(handle, True)

        # then
        with self.load_library(module, filename) as handle:
            self.assertEqual(len(module.EnumResourceTypes(handle)), count)

    def test_begin_removing_all_resources(self):
        if skip_on_wine:
            self.skipTest('EnumResourceTypes known failure on wine, see #59')

        # given
        module = self.module
        filename = os.path.join(self.tempdir, 'python.exe')

        # when
        handle = module.BeginUpdateResource(filename, True)
        module.EndUpdateResource(handle, False)

        # then
        with self.load_library(module, filename) as handle:
            self.assertEqual(len(module.EnumResourceTypes(handle)), 0)

    def test_begin_update_resource_with_invalid(self):
        if skip_on_wine:
            self.skipTest('BeginUpdateResource known failure on wine, see #59')

            # when/then
        with self.assertRaises(error) as context:
            self.module.BeginUpdateResource('invalid', False)
        # the errno cannot be 0 (i.e. success)
        self.assertNotEqual(context.exception.winerror, 0)

    def test_end_update_resource_with_invalid(self):
        if skip_on_wine:
            self.skipTest('EndUpdateResource known failure on wine, see #59')

        # when/then
        with self.assertRaises(error) as context:
            self.module.EndUpdateResource(-3, False)
        # the errno cannot be 0 (i.e. success)
        self.assertNotEqual(context.exception.winerror, 0)

    def test_update_resource(self):
        # given
        module = self.module
        filename = os.path.join(self.tempdir, 'python.exe')
        with self.load_library(self.module, filename) as handle:
            resource_type = module.EnumResourceTypes(handle)[-1]
            resource_name = module.EnumResourceNames(handle, resource_type)[-1]
            resource_language = module.EnumResourceLanguages(
                handle, resource_type, resource_name)[-1]
            resource = module.LoadResource(
                handle, resource_type, resource_name, resource_language)

        # when
        with self.resource_update(self.module, filename) as handle:
            module.UpdateResource(
                handle, resource_type, resource_name, resource[:-2],
                resource_language)

        # then
        with self.load_library(self.module, filename) as handle:
            updated = module.LoadResource(
                handle, resource_type, resource_name, resource_language)
        self.assertEqual(len(updated), len(resource) - 2)
        self.assertEqual(updated, resource[:-2])

    def test_update_resource_with_unicode(self):
        # given
        module = self.module
        filename = os.path.join(self.tempdir, 'python.exe')
        with self.load_library(module, filename) as handle:
            resource_type = module.EnumResourceTypes(handle)[-1]
            resource_name = module.EnumResourceNames(handle, resource_type)[-1]
            resource_language = module.EnumResourceLanguages(
                handle, resource_type, resource_name)[-1]
        resource = u"\N{GREEK CAPITAL LETTER DELTA}"

        # when
        with self.resource_update(module, filename) as handle:
            with self.assertRaises(TypeError):
                module.UpdateResource(
                    handle, resource_type, resource_name, resource,
                    resource_language)

    def test_get_windows_directory(self):
        # given
        expected = win32api.GetWindowsDirectory()

        # when
        result = self.module.GetWindowsDirectory()

        # then
        # note: pywin32 returns str on py27, unicode (which is str) on py3
        self.assertIsInstance(result, str)
        self.assertEqual(result.lower(), r"c:\windows")
        self.assertEqual(result, expected)

    def test_get_system_directory(self):
        # given
        expected = win32api.GetSystemDirectory()

        # when
        result = self.module.GetSystemDirectory()

        # then
        # note: pywin32 returns str on py27, unicode (which is str) on py3
        self.assertIsInstance(result, str)
        self.assertEqual(result.lower(), r"c:\windows\system32")
        self.assertEqual(result, expected)

    def _id2str(self, type_id):
        if hasattr(type_id, 'index'):
            return type_id
        else:
            return u'#{0}'.format(type_id)


if __name__ == '__main__':
    unittest.main()
