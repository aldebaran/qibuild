#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Open """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import io
import unittest
import mock

import qibuild.actions.open


class OpenTestCase(unittest.TestCase):
    """ OpenTestCase """

    def setUp(self):
        """ SetUp """
        self.ask_patcher = mock.patch('qisys.interact.ask_choice')
        self.ask_mock = self.ask_patcher.start()

    def test_no_ide_in_conf(self):
        """ Test No IDE In Config """
        empty_cfg = qibuild.config.QiBuildConfig()
        self.assertEqual(qibuild.actions.open.get_ide(empty_cfg), None)

    def test_qt_creator_in_conf(self):
        """ Test QtCreator In Conf """
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qt_creator = qibuild.config.IDE()
        qt_creator.name = "QtCreator"
        qt_creator.path = "/path/to/qtsdk/bin/qtcreator"
        qibuild_cfg.add_ide(qt_creator)
        ide = qibuild.actions.open.get_ide(qibuild_cfg)
        self.assertEqual(ide.name, "QtCreator")
        self.assertEqual(ide.path, "/path/to/qtsdk/bin/qtcreator")
        self.assertFalse(self.ask_mock.called)

    def test_eclipse_cdt_in_conf(self):
        """ Test Eclips Cdt In Conf """
        qibuild_cfg = qibuild.config.QiBuildConfig()
        eclipse = qibuild.config.IDE()
        eclipse.name = "Eclipse CDT"
        qibuild_cfg.add_ide(eclipse)
        try:
            qibuild.actions.open.get_ide(qibuild_cfg)
        except Exception as e:
            error = e
        self.assertFalse(error is None)
        self.assertFalse("Could not find any IDE in configuration" in
                         error.message)
        self.assertTrue("`qibuild open` only supports" in error.message)

    def test_two_ides(self):
        """ Test Two IDEs """
        qibuild_cfg = qibuild.config.QiBuildConfig()
        vs = qibuild.config.IDE()
        vs.name = "Visual Studio"
        qt_creator = qibuild.config.IDE()
        qt_creator.name = "QtCreator"
        qt_creator.path = r"C:\QtSDK\bin\QtCreator"
        qibuild_cfg.add_ide(qt_creator)
        qibuild_cfg.add_ide(vs)
        self.ask_mock.return_value = "QtCreator"
        ide = qibuild.actions.open.get_ide(qibuild_cfg)
        self.assertEqual(ide.name, "QtCreator")
        self.assertEqual(ide.path, r"C:\QtSDK\bin\QtCreator")
        call_args_list = self.ask_mock.call_args_list
        self.assertEqual(len(call_args_list), 1)
        (choices, _question) = call_args_list[0][0]
        self.assertEqual(choices, ['Visual Studio', 'QtCreator'])

    def test_two_ides_matching_default_conf(self):
        """ Test Two IDEs Matching Default Conf """
        global_cfg = io.StringIO(r"""
<qibuild version="1">
  <config name="win32-vs2010" ide="Visual Studio" />
  <config name="mingw" ide="QtCreator" />
  <ide name="Visual Studio" />
  <ide name="QtCreator" path="C:\QtSDK\bin\QtCreator" />
</qibuild>
""")
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read(global_cfg, create_if_missing=False)
        local_cfg = io.StringIO(r"""
<qibuild version="1">
  <defaults config="mingw" />
</qibuild>
""")
        qibuild_cfg.read_local_config(local_cfg)
        ide = qibuild.actions.open.get_ide(qibuild_cfg)
        self.assertEqual(ide.name, "QtCreator")
        self.assertEqual(ide.path, r"C:\QtSDK\bin\QtCreator")

    def test_two_ides_matching_user_conf(self):
        """ Test Two IDEs Matching User Conf """
        # A default config in local config file,
        # but user used -c
        qibuild_cfg = qibuild.config.QiBuildConfig()
        global_cfg = io.StringIO(r"""
<qibuild version="1">
  <config name="win32-vs2010" ide="Visual Studio" />
  <config name="mingw" ide="QtCreator" />
  <ide name="Visual Studio" />
  <ide name="QtCreator" path="C:\QtSDK\bin\QtCreator" />
</qibuild>
""")
        qibuild_cfg.read(global_cfg, create_if_missing=False)
        qibuild_cfg.set_active_config("win32-vs2010")
        ide = qibuild.actions.open.get_ide(qibuild_cfg)
        self.assertEqual(ide.name, "Visual Studio")
        self.assertFalse(self.ask_mock.called)

    def tearDown(self):
        """ TearDown """
        self.ask_patcher.stop()


if __name__ == "__main__":
    unittest.main()
