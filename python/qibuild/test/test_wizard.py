#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Test Wizard.
Test qibuild.wizard.run_config_wizard.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import tempfile
import unittest
import mock

import qibuild.wizard
import qisys
from qisys.test.fake_interact import FakeInteract


class ConfigWizardTestCase(unittest.TestCase):
    """ ConfigWizardTestCase """

    def setUp(self):
        """ SetUp """
        self.orig_platform = sys.platform
        self.tmp = tempfile.mkdtemp(prefix="test-qibuild-config-wizard")
        self.cfg_patcher = mock.patch('qibuild.config.get_global_cfg_path')
        self.get_cfg_path = self.cfg_patcher.start()
        self.get_cfg_path.return_value = os.path.join(self.tmp, "qibuild.xml")

        self.get_config_names = mock.patch('qibuild.config.get_config_names')
        self.get_config_names = self.get_config_names.start()
        self.find_patcher = mock.patch('qisys.command.find_program')
        self.find_program = self.find_patcher.start()
        self.get_generators_patcher = mock.patch(
            'qibuild.cmake.get_known_cmake_generators')
        self.get_generators = self.get_generators_patcher.start()
        self.interact_patcher = None
        worktree = qisys.worktree.WorkTree(self.tmp, sanity_check=False)
        self.build_worktree = qibuild.worktree.BuildWorkTree(worktree)

    @staticmethod
    def setup_platform(platform):
        """ Setup sys.platform """
        sys.platform = platform

    def setup_configs(self, names):
        """ Setup qibuild.config.get_config_names for this test """
        self.get_config_names.return_value = names

    def setup_initial_config(self, xml):
        """
        Setup the contents of the global xml config file for this test.
        If not called, the file won't exist.
        """
        cfg_path = self.get_cfg_path()
        with open(cfg_path, "w") as fp:
            fp.write(xml)

    def setup_find_program(self, programs):
        """ Set the return value of qisys.command.find_program for this test """
        def fake_find(name, raises=True, env=None):
            """ Fake Find """
            return programs.get(name)
        self.find_program.side_effect = fake_find

    def setup_answers(self, answers):
        """ Set the return value of qisys.interact.ask_* for this test """
        fake_interact = FakeInteract()
        fake_interact.answers = answers
        self.interact_patcher = mock.patch('qisys.interact', fake_interact)
        self.interact_patcher.start()

    def setup_generators(self, generators):
        """ Set the return value for qibuild.cmake.get_known_cmake_generators for this test """
        self.get_generators.return_value = generators

    @staticmethod
    def run_wizard(build_worktree=None):
        """ Run the wizard, return the QiBuildConfig object """
        qibuild.wizard.run_config_wizard(build_worktree=build_worktree)
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read()
        return qibuild_cfg

    def test_empty_conf_all_in_path(self):
        """ Test Empty Conf All In Path """
        if sys.platform == "darwin":
            return
        self.setup_platform("linux2")
        self.setup_find_program({
            'cmake': '/usr/local/bin/cmake',
            'qtcreator': '/usr/local/bin/qtcreator'
        })
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "QtCreator",
        })
        self.setup_generators(["Unix Makefiles"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        qtcreator = qibuild_cfg.ides['QtCreator']
        self.assertEqual(qtcreator.name, 'QtCreator')
        self.assertEqual(qtcreator.path, '/usr/local/bin/qtcreator')

    def test_empty_conf_nothing_in_path(self):
        """ Test Empty Conf Nothing In Path """
        if os.name == 'nt':
            return
        if sys.platform == "darwin":
            return
        self.setup_platform("linux3")
        self.setup_find_program(dict())
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "QtCreator",
            "cmake path": "/home/john/.local/cmake/bin/cmake",
            "qtcreator path": "/home/john/QtSDK/bin/qtcreator",
        })
        self.setup_generators(["Unix Makefiles"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        qtcreator = qibuild_cfg.ides['QtCreator']
        self.assertEqual(qtcreator.name, 'QtCreator')
        self.assertEqual(qtcreator.path, '/home/john/QtSDK/bin/qtcreator')
        defaults_env_path = qibuild_cfg.defaults.env.path
        self.assertEqual(defaults_env_path, "/home/john/.local/cmake/bin")

    def test_qtcreator_in_conf(self):
        """ Test QtCreator In Conf """
        if sys.platform == "darwin":
            return
        # QtCreator in config, but now with correct path
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake": "/usr/bin/cmake",
        })
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "QtCreator",
            "qtcreator path": "/home/john/QtSDK/bin/qtcreator"
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_initial_config("""
<qibuild version="1">
    <ide name="QtCreator" path="/home/john/.local/bin/qtcreator"  />
</qibuild>
""")
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        qtcreator = qibuild_cfg.ides['QtCreator']
        self.assertEqual(qtcreator.name, 'QtCreator')
        self.assertEqual(qtcreator.path, '/home/john/QtSDK/bin/qtcreator')

    def test_force_local_qtcreator(self):
        """ Test Force Local QtCreator """
        # /usr/bin/qtcreator exists, but we want to use the one in ~/QtSDK
        if sys.platform == "darwin":
            return
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake": "/usr/bin/cmake",
            "qtcreator": "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "QtCreator",
            "use qtcreator from /usr/bin/qtcreator": False,
            "qtcreator path": "/home/john/QtSDK/bin/qtcreator",
        })
        self.setup_generators(["Unix Makefiles"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        qtcreator = qibuild_cfg.ides['QtCreator']
        self.assertEqual(qtcreator.name, 'QtCreator')
        self.assertEqual(qtcreator.path, '/home/john/QtSDK/bin/qtcreator')

    def test_visual_studio(self):
        """ Test Visual Studio """
        self.setup_platform("win32")
        self.setup_find_program({
            "cmake": r"c:\Progam Files\CMake\bin\cmake.exe"
        })
        self.setup_answers({
            "generator": "Visual Studio 10",
            "ide": "Visual Studio"
        })
        self.setup_generators(["Unix Makefiles", "Visual Studio 10"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        visual = qibuild_cfg.ides['Visual Studio']
        self.assertEqual(visual.name, 'Visual Studio')

    def test_xcode(self):
        """ Test XCode """
        self.setup_platform("darwin")
        self.setup_find_program({
            "cmake": "/Applications/CMake 2.8/Contents/MacOS/cmake",
        })
        self.setup_answers({
            "generator": "Xcode",
            "ide": "Xcode",
        })
        self.setup_generators(["Unix Makefiles", "Xcode"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        xcode = qibuild_cfg.ides['Xcode']
        self.assertEqual(xcode.name, 'Xcode')

    def test_local_settings_no_toolchain(self):
        """ Test Local Settings No Toolchain """
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake": "/usr/bin/cmake",
            "qtcreator": "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "QtCreator",
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_configs(list())
        self.run_wizard(build_worktree=self.build_worktree)

    def test_local_settings_choose_default_config(self):
        """ Test Local Settings Choose Default Config """
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake": "/usr/bin/cmake",
            "qtcreator": "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "QtCreator",
            "config": "linux64",
            "configure settings for this worktree": True,
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_configs(["linux32", "linux64"])
        self.run_wizard(build_worktree=self.build_worktree)
        self.assertEqual(self.build_worktree.qibuild_cfg.local.defaults.config,
                         "linux64")

    def test_local_build_settings(self):
        """ Test Local Build Settings """
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake": "/usr/bin/cmake",
            "qtcreator": "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "Eclipse CDT",
            "unique build dir": True,
            "unique sdk dir": True,
            "configure settings for this worktree": True,
            "path to a build dir": "build",
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_configs(list())
        self.run_wizard(build_worktree=self.build_worktree)
        self.assertEqual(self.build_worktree.qibuild_cfg.local.build.prefix,
                         "build")

    def test_full_wizard(self):
        """ Test Full Wizard """
        self.setup_platform("win32")
        self.setup_find_program({
            "cmake": r"c:\Program Files\CMake\bin\cmake.exe"
        })
        self.setup_answers({
            "generator": "Visual Studio 10",
            "ide": "Visual Studio",
            "use on of these configs by default": True,
            "configure settings for this worktree": True,
            "config to use by default": "win32-vs2010",
        })
        self.setup_generators(["Visual Studio 10"])
        self.setup_configs(["win32-vs2010"])
        self.run_wizard(build_worktree=self.build_worktree)
        self.assertEqual(self.build_worktree.qibuild_cfg.local.defaults.config,
                         "win32-vs2010")
        self.assertEqual(self.build_worktree.qibuild_cfg.defaults.cmake.generator,
                         "Visual Studio 10")

    def test_unsetting_unique_build_dir(self):
        """ Test UnSetting  Unique Build Dir """
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake": "/usr/bin/cmake",
            "qtcreator": "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "Eclipse CDT",
            "unique build dir": True,
            "configure settings for this worktree": True,
            "path to a build dir": "build",
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_configs(list())
        worktree = qisys.worktree.WorkTree(self.tmp, sanity_check=False)
        old_build_worktree = qibuild.worktree.BuildWorkTree(worktree)
        self.run_wizard(build_worktree=old_build_worktree)
        self.assertEqual(old_build_worktree.qibuild_cfg.local.build.prefix,
                         "build")
        self.interact_patcher.stop()
        self.setup_answers({
            "generator": "Unix Makefiles",
            "ide": "Eclipse CDT",
            "unique build dir": False,
            "configure settings for this worktree": True,
            "unique sdk dir": False,
        })
        new_build_worktree = qibuild.worktree.BuildWorkTree(worktree)
        self.run_wizard(build_worktree=new_build_worktree)
        build_dir = new_build_worktree.qibuild_cfg.local.build.prefix
        sdk_dir = new_build_worktree.qibuild_cfg.local.build.sdk_dir
        self.assertFalse(build_dir,
                         "build_dir is '%s', should be None or empty" % build_dir)
        self.assertFalse(sdk_dir,
                         "sdk_dir is '%s', should be None or empty" % sdk_dir)

    def tearDown(self):
        """ TearDown """
        qisys.sh.rm(self.tmp)
        sys.platform = self.orig_platform
        self.get_config_names.stop()
        self.cfg_patcher.stop()
        self.find_patcher.stop()
        if self.interact_patcher:
            self.interact_patcher.stop()
        self.get_generators_patcher.stop()


if __name__ == "__main__":
    unittest.main()
