## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for handling qibuild configurations

"""

import os
import unittest

import qibuild
import tempfile


class ConfigStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-configstore-test")
        self.cfg_path = os.path.join(self.tmp, "conf.cfg")
        with open(self.cfg_path, "w") as fp:
            fp.write("""
[foo]
bar = 42
""")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_get_set(self):
        confistore = qibuild.configstore.ConfigStore()
        confistore.read(self.cfg_path)
        self.assertEquals(confistore.get('foo.bar'), '42')

        # Update existing section:
        qibuild.configstore.update_config(self.cfg_path, 'foo', 'bar', '43')

        # Re-init configstore:
        confistore = qibuild.configstore.ConfigStore()
        confistore.read(self.cfg_path)
        self.assertEquals(confistore.get('foo.bar'), '43')

    def test_create_section(self):
        confistore = qibuild.configstore.ConfigStore()
        confistore.read(self.cfg_path)
        self.assertEquals(confistore.get('foo.bar'), '42')

        # Update existing section:
        qibuild.configstore.update_config(self.cfg_path, 'spam', 'eggs', '43')

        # Re-init configstore:
        confistore = qibuild.configstore.ConfigStore()
        confistore.read(self.cfg_path)
        self.assertEquals(confistore.get('spam.eggs'), '43')


    def test_dot_in_subsection(self):
        with open(self.cfg_path, "a") as fp:
            fp.write("""
[config "linux32"]
foo = bar

[config "linux32-1.12"]
spam = eggs
""")

        confistore = qibuild.configstore.ConfigStore()
        confistore.read(self.cfg_path)

        self.assertEquals(confistore.get('config.linux32-1.12.spam'), 'eggs')

        configs = confistore.get('config')
        actual = configs.keys()
        actual.sort()

        expected = ['linux32', 'linux32-1.12']
        self.assertEquals(actual, expected)

    def test_merge_conf_files(self):
        global_cfg = os.path.join(self.tmp, "global.cfg")
        with open(global_cfg, "w") as fp:
            fp.write(r"""
[general]
env.path = c:\path\to\swig
""")
        user_cfg = os.path.join(self.tmp, "user.cfg")
        with open(user_cfg, "w") as fp:
            fp.write(r"""
[general]
config = win32-vs2008
""")

        configstore = qibuild.configstore.ConfigStore()
        configstore.read(global_cfg)
        configstore.read(user_cfg)

        self.assertEquals(configstore.get('general.env.path'), r"c:\path\to\swig")
        self.assertEquals(configstore.get('general.config'), "win32-vs2008")

    def test_merge_conf_files_different_syntax(self):
        global_cfg = os.path.join(self.tmp, "global.cfg")
        with open(global_cfg, "w") as fp:
            fp.write(r"""
[general "build"]
config = win32-vs2008
toolchain = win32-vs2008
cmake_generator = Visual Studio 9 2008

[general "env"]
""")
        user_cfg = os.path.join(self.tmp, "user.cfg")
        with open(user_cfg, "w") as fp:
            fp.write(r"""
[general]
build.sdk_dir = /path/to/foo
""")

        configstore = qibuild.configstore.ConfigStore()
        configstore.read(global_cfg)
        configstore.read(user_cfg)

        self.assertEquals(configstore.get('general.build.sdk_dir'), r"/path/to/foo")


class QiConfigTestCase(unittest.TestCase):
    def setUp(self):
        """ An (almost) realistic exemple ...

        """
        config = r"""
[general]
cmake.generator = 'Unix Makefiles'
config = 'mingw32'

[config 'mingw32']
cmake.generator = 'MinGW Makefiles'
env.path = C:\MinGW\bin

[config 'win32-vs2010']
cmake.generator = 'Visual Studio 10'

"""

        # Create a temp dir to use as a toc worktree:
        self.tmp = tempfile.mkdtemp(prefix="tmp-qibuild-test")
        os.makedirs(os.path.join(self.tmp, ".qi"))
        qibuild_cfg = os.path.join(self.tmp, ".qi", "qibuild.cfg")

        # Create custom cmake flags so that toc won't complain
        # about unknown configs
        with open(qibuild_cfg, "w") as fp:
            fp.write(config)

        with open(os.path.join(self.tmp, ".qi", "mingw32.cmake"), "w") as fp:
            fp.write("\n")

        with open(os.path.join(self.tmp, ".qi", "win32-vs2010.cmake"), "w") as fp:
            fp.write("\n")

    def _check_config(self, toc, expected, key):
        """ Check that toc configuration matches the
        expected value

        """
        actual = toc.configstore.get(key)
        mess  = "Wrong config for %s\n" % key
        mess += "Actual   : %s\n" % actual
        mess += "Expected : %s\n" % expected
        self.assertEquals(actual, expected, mess)

    def test_default_config(self):
        toc =  qibuild.toc.Toc(self.tmp)
        self._check_config(toc, "MinGW Makefiles", "cmake.generator")
        self._check_config(toc, r"C:\MinGW\bin", "env.path")


    def test_setting_config(self):
        toc =  qibuild.toc.Toc(self.tmp, config='win32-vs2010')
        self._check_config(toc, "Visual Studio 10", "cmake.generator")

    def test_general_only(self):
        config = """
[general]
build.sdk_dir = /path/to/foo
"""
        qibuild_cfg = os.path.join(self.tmp, ".qi", "qibuild.cfg")
        with open(qibuild_cfg, "w") as fp:
            fp.write(config)
        toc = qibuild.toc.Toc(self.tmp, config="win32-vs2010")
        self._check_config(toc, "/path/to/foo", "build.sdk_dir")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)


class TocCMakeFlagsTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-qibuild-test")
        qibuild.run_action('qibuild.actions.init', ['--work-tree', self.tmp])
        foo_path = os.path.join(self.tmp, "foo")
        qibuild.run_action('qibuild.actions.create',
            ['--work-tree', self.tmp,
             'foo'])
        self.foo_project = qibuild.project.Project("foo", foo_path)

    def test_no_toc(self):
        self.assertEquals(self.foo_project.cmake_flags, list())

    def test_default_is_debug(self):
        toc = qibuild.toc.Toc(self.tmp)
        qibuild.project.update_project(self.foo_project, toc)
        self.assertEquals(self.foo_project.cmake_flags, ["CMAKE_BUILD_TYPE=DEBUG"])

    def test_release(self):
        toc = qibuild.toc.Toc(self.tmp, build_type="release")
        qibuild.project.update_project(self.foo_project, toc)
        self.assertEquals(self.foo_project.cmake_flags, ["CMAKE_BUILD_TYPE=RELEASE"])


    def test_custom_flags(self):
        custom_cmake = os.path.join(self.tmp, ".qi", "myconf.cmake")
        to_write = 'message(STATUS "Using my config!")\n'
        with open(custom_cmake, "w") as fp:
            fp.write(to_write)
        toc = qibuild.toc.Toc(self.tmp, config="myconf")
        qibuild.project.update_project(self.foo_project, toc)
        qibuild.project.bootstrap_project(self.foo_project, toc)
        build_dir = self.foo_project.build_directory
        dep_cmake = os.path.join(build_dir, "dependencies.cmake")
        contents = ""
        with open(dep_cmake, "r") as fp:
            contents = fp.read()

        to_search = 'include("%s")' % qibuild.sh.to_posix_path(custom_cmake)
        self.assertTrue(to_search in contents, "Failed to find %s in %s" % (to_search, contents))


    def tearDown(self):
        qibuild.sh.rm(self.tmp)


if __name__ == "__main__":
    unittest.main()
