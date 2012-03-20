## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" testing for qibuild.wizard.run_config_wizard

"""

import os
import tempfile

import unittest
import mock

import qibuild.wizard

class FakeInteract:
    """ A class to control qibuild.interact behavior

    Answers must be a dict: message -> answer
    message must be a part of the message
    answer can be a boolean (for ask_yes_no), and string
    (for ask_path or ask_string), or a string that must
    match one of the choices, for (ask_choice)

    Note that if you do not specify an answer for
    ask_yes_no, the default will be used.

    Any other non specifed answer will raise an exception
    """
    def __init__(self, answers):
        self.answers = answers

    def find_answer(self, message, choices=None, default=None):
        keys = self.answers.keys()
        for key in keys:
            if key in message.lower():
                if not choices:
                    return self.answers[key]
                answer = self.answers[key]
                if answer in choices:
                    return answer
                else:
                    mess  = "Would answer %s\n" % answer
                    mess += "But choices are: %s\n" % choices
                    raise Exception(mess)
        if default is not None:
            return default
        mess  = "Could not find answer for\n  :: %s\n" % message
        mess += "Known keys are: %s" % ", ".join(keys)
        raise Exception(mess)

    def ask_choice(self, choices, message):
        return self.find_answer(message, choices)

    def ask_yes_no(self, message, default=False):
        return self.find_answer(message, default=default)

    def ask_path(self, message):
        return self.find_answer(message)

    def ask_string(self, message):
        return self.find_answer(message)

    def ask_program(self, message):
        return self.find_answer(message)


class ConfigWizardTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-qibuild-config-wizard")
        self.cfg_patcher = mock.patch('qibuild.config.get_global_cfg_path')
        self.get_cfg_path = self.cfg_patcher.start()
        self.get_cfg_path.return_value = os.path.join(self.tmp, "qibuild.xml")

        self.get_platform_patcher = mock.patch('qibuild.get_platform')
        self.get_platform = self.get_platform_patcher.start()
        self.get_tc_names_patcher = mock.patch('qitoolchain.get_tc_names')
        self.get_tc_names = self.get_tc_names_patcher.start()
        self.find_patcher = mock.patch('qibuild.command.find_program')
        self.find_program = self.find_patcher.start()
        self.get_generators_patcher = mock.patch('qibuild.cmake.get_known_cmake_generators')
        self.get_generators = self.get_generators_patcher.start()
        self.interact_patcher = None

    def setup_platform(self, platform):
        """ Setup qibuild.get_platform

        """
        self.get_platform.return_value = platform

    def setup_tc_names(self, tc_names):
        """ Setup qitoolchain.get_tc_names for this test

        """
        self.get_tc_names.return_value = tc_names

    def setup_initial_config(self, xml):
        """ Setup the contents of the global xml config file
        for this test.

        If not called, the file won't exist

        """
        cfg_path = self.get_cfg_path()
        with open(cfg_path, "w") as fp:
            fp.write(xml)

    def setup_find_program(self, programs):
        """ Set the return value of qibuild.command.find_program
        for this test

        """
        def fake_find(name, env=None):
            return programs.get(name)
        self.find_program.side_effect = fake_find

    def setup_answers(self, answers):
        """ Set the return value of qibuild.interact.ask_*
        for this test

        """
        fake_interact = FakeInteract(answers)
        self.interact_patcher = mock.patch('qibuild.interact', fake_interact)
        self.interact_patcher.start()

    def setup_generators(self, generators):
        """ Set the return value for qibuild.cmake.get_known_cmake_generators
        for this test

        """
        self.get_generators.return_value = generators

    def run_wizard(self, toc=None):
        """ Run the wizard, return the QiBuildConfig object

        """
        qibuild.wizard.run_config_wizard(toc)
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read()
        return qibuild_cfg

    def test_empty_conf_all_in_path(self):
        self.setup_platform("linux")
        self.setup_find_program({
            'cmake'  : '/usr/local/bin/cmake',
            'qtcreator' : '/usr/local/bin/qtcreator'
        })
        self.setup_answers({
            "generator" : "Unix Makefiles",
            "ide"       : "QtCreator",
        })

        self.setup_generators(["Unix Makefiles"])

        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        qtcreator = qibuild_cfg.ides['QtCreator']
        self.assertEqual(qtcreator.name, 'QtCreator')
        self.assertEqual(qtcreator.path, '/usr/local/bin/qtcreator')

    def test_empty_conf_nothing_in_path(self):
        self.setup_platform("linux")
        self.setup_find_program(dict())
        self.setup_answers({
            "generator"  : "Unix Makefiles",
            "ide"        : "QtCreator",
            "cmake path" : "/home/john/.local/cmake/bin/cmake",
            "qtcreator path" : "/home/john/QtSDK/bin/qtcreator",
        })
        self.setup_generators(["Unix Makefiles"])

        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        qtcreator = qibuild_cfg.ides['QtCreator']
        self.assertEqual(qtcreator.name, 'QtCreator')
        self.assertEqual(qtcreator.path, '/home/john/QtSDK/bin/qtcreator')
        defaults_env_path = qibuild_cfg.defaults.env.path
        self.assertEqual(defaults_env_path,  "/home/john/.local/cmake/bin")

    def test_qtcreator_in_conf(self):
        # QtCreator in config, but now with correct path
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake" : "/usr/bin/cmake",
        })
        self.setup_answers({
            "generator"  : "Unix Makefiles",
            "ide"        : "QtCreator",
            "qtcreator path" : "/home/john/QtSDK/bin/qtcreator"
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
        # /usr/bin/qtcreator exists, but we want to use the one
        # in ~/QtSDK
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake" : "/usr/bin/cmake",
            "qtcreator" : "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator"  : "Unix Makefiles",
            "ide"        : "QtCreator",
            "use qtcreator from /usr/bin/qtcreator" : False,
            "qtcreator path" : "/home/john/QtSDK/bin/qtcreator",
        })
        self.setup_generators(["Unix Makefiles"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        qtcreator = qibuild_cfg.ides['QtCreator']
        self.assertEqual(qtcreator.name, 'QtCreator')
        self.assertEqual(qtcreator.path, '/home/john/QtSDK/bin/qtcreator')

    def test_visual_studio(self):
        self.setup_platform("windows")
        self.setup_find_program({
            "cmake" : r"c:\Progam Files\CMake\bin\cmake.exe"
        })
        self.setup_answers({
            "generator" : "Visual Studio 10",
            "ide"       : "Visual Studio"
        })
        self.setup_generators(["Unix Makefiles", "Visual Studio 10"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        visual = qibuild_cfg.ides['Visual Studio']
        self.assertEqual(visual.name, 'Visual Studio')

    def test_xcode(self):
        self.setup_platform("mac")
        self.setup_find_program({
            "cmake" : "/Applications/CMake 2.8/Contents/MacOS/cmake",
        })
        self.setup_answers({
            "generator" : "Xcode",
            "ide" : "Xcode",
        })
        self.setup_generators(["Unix Makefiles", "Xcode"])
        qibuild_cfg = self.run_wizard()
        self.assertEqual(len(qibuild_cfg.ides), 1)
        xcode = qibuild_cfg.ides['Xcode']
        self.assertEqual(xcode.name, 'Xcode')


    def test_local_settings_no_toolchain(self):
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake" : "/usr/bin/cmake",
            "qtcreator" : "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator" : "Unix Makefiles",
            "ide" : "QtCreator",
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_tc_names(list())
        work_tree = os.path.join(self.tmp, "work_tree")
        toc = qibuild.toc.Toc(work_tree=work_tree)
        self.run_wizard(toc=toc)

    def test_local_settings_choose_default_toolchain(self):
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake" : "/usr/bin/cmake",
            "qtcreator" : "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator" : "Unix Makefiles",
            "ide" : "QtCreator",
            "toolchain" : "linux64",
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_tc_names(["linux32", "linux64"])
        work_tree = os.path.join(self.tmp, "work_tree")
        toc = qibuild.toc.Toc(work_tree=work_tree)
        self.run_wizard(toc=toc)
        self.assertEqual(toc.config.local.defaults.config, "linux64")

    def test_local_build_settings(self):
        self.setup_platform("linux")
        self.setup_find_program({
            "cmake" : "/usr/bin/cmake",
            "qtcreator" : "/usr/bin/qtcreator",
        })
        self.setup_answers({
            "generator" : "Unix Makefiles",
            "ide" : "Eclipse CDT",
            "unique build dir" : True,
            "unique sdk dir"   : True,
            "path to a build dir" : "build",
            "path to a sdk dir"   : "sdk",
        })
        self.setup_generators(["Unix Makefiles"])
        self.setup_tc_names(list())
        work_tree = os.path.join(self.tmp, "work_tree")
        toc = qibuild.toc.Toc(work_tree=work_tree)
        self.run_wizard(toc=toc)
        self.assertEqual(toc.config.local.build.build_dir, "build")
        self.assertEqual(toc.config.local.build.sdk_dir,   "sdk")

    def test_full_wizard(self):
        self.setup_platform("windows")
        self.setup_find_program({
            "cmake"  : r"c:\Program Files\CMake\bin\cmake.exe"
        })
        self.setup_answers({
            "generator" : "Visual Studio 10",
            "ide" : "Visual Studio",
            "use on of these toolchains by default" : True,
            "toolchain to use by default": "win32-vs2010",
        })
        self.setup_generators(["Visual Studio 10"])
        self.setup_tc_names(["win32-vs2010"])
        work_tree = os.path.join(self.tmp, "work_tree")
        toc = qibuild.toc.Toc(work_tree=work_tree)

        self.run_wizard(toc=toc)
        self.assertEqual(toc.config.local.defaults.config, "win32-vs2010")
        self.assertEqual(toc.config.defaults.cmake.generator, "Visual Studio 10")


    def test_incredibuild(self):
        self.setup_platform("windows")
        self.setup_find_program({
            "cmake"  : r"c:\Program Files\CMake\bin\cmake.exe",
        })
        self.setup_answers({
            "generator" : "Visual Studio 10",
            "ide" : "Visual Studio",
            "use incredibuild" : True,
            "buildconsole.exe path" : "/c/Program Files/Xoreax/BuildConsole.exe"
        })
        self.setup_generators(["Visual Studio 10"])
        cfg = self.run_wizard()
        self.assertEqual(cfg.build.incredibuild, True)
        self.assertEqual(cfg.defaults.env.path, r"/c/Program Files/Xoreax")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)
        # pylint: disable-msg=E1103
        self.get_platform.stop()
        self.get_tc_names_patcher.stop()
        self.cfg_patcher.stop()
        self.find_patcher.stop()
        if self.interact_patcher:
            self.interact_patcher.stop()
        self.get_generators_patcher.stop()

if __name__ == "__main__":
    unittest.main()
