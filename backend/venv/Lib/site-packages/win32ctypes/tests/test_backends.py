#
# (C) Copyright 2023 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import importlib
import unittest

from win32ctypes.core import _backend

_modules = [
    '_dll', '_authentication', '_time', '_common',
    '_resource',  '_nl_support', '_system_information']


class TestBackends(unittest.TestCase):

    @unittest.skipIf(_backend != 'cffi', 'cffi backend not enabled')
    def test_backend_cffi_load(self):
        # when/then
        for name in _modules:
            module = importlib.import_module(f'win32ctypes.core.{name}')
            self.assertEqual(
                module.__spec__.name, f'win32ctypes.core.{name}')
            self.assertTrue(module.__file__.endswith(f'cffi\\{name}.py'))

    @unittest.skipIf(_backend != 'ctypes', 'ctypes backend not enabled')
    def test_backend_ctypes_load(self):
        # when/then
        for name in _modules:
            module = importlib.import_module(f'win32ctypes.core.{name}')
            self.assertEqual(
                module.__spec__.name, f'win32ctypes.core.{name}')
            self.assertTrue(module.__file__.endswith(f'ctypes\\{name}.py'))
