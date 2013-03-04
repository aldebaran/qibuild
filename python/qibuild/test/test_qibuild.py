## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for qibuild."""


import argparse
import os

import pytest
import unittest

import qisys
import qisys.script
import qisys.worktree
import qibuild
import qibuild.cmdparse
import qibuild.cmake
import qibuild.parsers
import qibuild.toc


# pylint: disable-msg=E1101
@pytest.mark.slow
class QiBuildTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath(os.path.dirname(__file__))
        self.parser = argparse.ArgumentParser()
        qibuild.parsers.toc_parser(self.parser)
        qibuild.parsers.build_parser(self.parser)
        self.args = self.parser.parse_args([])
        if os.environ.get("DEBUG"):
            self.args.verbose = True
        if os.environ.get("PDB"):
            self.args.pdb = True
        self.args.worktree = self.test_dir
        # Run qibuild clean
        self._run_action('clean', '--force', '--all')

    def _run_action(self, action, *args):
        qisys.script.run_action("qibuild.actions.%s" % action, args,
            forward_args=self.args)

    def get_build_dir(self, project_name):
        """Get the build dir of a project."""
        toc = qibuild.toc.toc_open(self.test_dir, args=self.args)
        project = toc.get_project(project_name)
        return project.build_directory

    def get_cmake_cache(self, project_name):
        """Get the CMake cache path of the given project."""
        build_dir = self.get_build_dir(project_name)
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        return cmake_cache

    def test_configure(self):
        self._run_action("configure", "world")

    def test_configure_all(self):
        self._run_action("configure", "--all")

    def test_make(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")

    def test_make_without_configure(self):
        self.assertRaises(Exception, self._run_action, "make", "hello")

    def test_install(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")
        self._run_action("install", "hello", "/tmp")

    def test_ctest(self):
        self._run_action("configure", "hello")
        self._run_action("make", "hello")
        self._run_action("test", "hello")

    def test_qi_use_lib(self):
        self._run_action("configure", "uselib")
        # Read cache and check that DEPENDS value are here
        cmake_cache = self.get_cmake_cache("uselib")
        cache = qibuild.cmake.read_cmake_cache(cmake_cache)
        self.assertEquals(cache["D_DEPENDS"], "A;B")
        self.assertEquals(cache["E_DEPENDS"], "D;A;B;CC")
        self._run_action("make", "uselib")

        self.assertRaises(Exception,
                self._run_action, "configure", "uselib", "-DSHOULD_FAIL=ON")

    def test_qi_stage_lib_simple(self):
        self._run_action("configure", "stagelib")

    def test_qi_stage_lib_but_really_bin(self):
        error = None
        try:
            self._run_action("configure", "stagelib",
                "-DSHOULD_FAIL_STAGE_LIB_BUT_REALLY_BIN=ON")
        except Exception, e:
            error = e
        self.assertFalse(error is None)

    def test_qi_stage_lib_but_no_such_target(self):
        error = None
        try:
            self._run_action("configure", "stagelib",
                "-DSHOULD_FAIL_STAGE_NO_SUCH_TARGET=ON")
        except qibuild.toc.ConfigureFailed, e:
            error = e
        self.assertFalse(error is None)

    def test_package(self):
        self._run_action("package", "world")

    def test_using_tool_for_install(self):
        self._run_action("configure", "bar")
        self._run_action("make", "bar")
        with qisys.sh.TempDir() as tmp:
            self._run_action("install", "bar", tmp)
            foo_out = os.path.join(tmp, "share", "foo", "foo.out")
            self.assertTrue(os.path.exists(foo_out))

    def test_preserve_cache(self):
        # If cache changes when runnning cmake .. after
        # qibuild configure, then you have two problems:
        #     * every target will alway be seen has out of date
        #     * chances are some list vars contains more element,
        #       so perf will decrease each time you run cmake ..
        # Since some IDE automatically run cmake .. (qtcreator,
        # visual studio, for instance), this will lead to
        # performance issues
        self._run_action("status")
        self._run_action("configure", "foo")
        cmake_cache = self.get_cmake_cache("foo")
        build_dir = self.get_build_dir("foo")

        # Read cache and check that DEPENDS value are here
        cache_before = qibuild.cmake.read_cmake_cache(cmake_cache)

        assert cache_before["EGGS_DEPENDS"] == "SPAM"
        assert cache_before["BAR_DEPENDS"] == "EGGS;SPAM"

        # run cmake .. and check the cache did not change
        qisys.command.call(["cmake", ".."], cwd=build_dir)
        cache_after = qibuild.cmake.read_cmake_cache(cmake_cache)

        assert cache_before == cache_after


if __name__ == "__main__":
    unittest.main()
