## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for handling qibuidl configurations

"""
import os
import unittest

import qibuild
import tempfile



class QiConfigTestCase(unittest.TestCase):
    def setUp(self):
        """ An (almost) realistic exemple ...

        """
        config = r"""
[general]
cmake.generator = 'Unix Makefiles'
config = 'mingw32'

[config mingw32]
cmake.generator = 'MinGW Makefiles'
env.path = C:\MinGW\bin

[config win32-vs2010]
cmake.generator = 'Visual Studio 10'

        """

        # Create a temp dir to use as a toc worktree:
        self.tmp = tempfile.mkdtemp(prefix="tmp-qibuild-test")
        os.makedirs(os.path.join(self.tmp, ".qi"))
        qibuild_cfg = os.path.join(self.tmp, ".qi", "qibuild.cfg")
        fp = open(qibuild_cfg, "w")
        fp.write(config)
        fp.close()

    def _check_config(self, toc, expected, *keys):
        """ Check that toc configuration matches the
        expected value

        """
        actual = toc.configstore.get(*keys)
        mess  = "Wrong config for %s\n" % ".".join(keys)
        mess += "Actual   : %s\n" % actual
        mess += "Expected : %s\n" % expected
        self.assertEquals(actual, expected, mess)

    def test_default_config(self):
        toc =  qibuild.toc.Toc(self.tmp)
        self._check_config(toc, "MinGW Makefiles", "cmake", "generator")
        self._check_config(toc, r"C:\MinGW\bin", "env", "path")


    def test_setting_config(self):
        toc =  qibuild.toc.Toc(self.tmp, config='win32-vs2010')
        self._check_config(toc, "Visual Studio 10", "cmake", "generator")

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
