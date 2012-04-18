## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for qibuild convert

"""

import os
import unittest
import pytest
import tempfile

import qisrc
import qibuild
import qibuild.actions.convert


# pylint: disable-msg=E1101
@pytest.mark.slow
class QiBuildConvertTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-convert-test")
        this_dir = os.path.dirname(__file__)
        self.test_dir = os.path.join(this_dir, "convert")

    def fix_cmake_from_string(self, input):
        """ Helper for qibuild.actions.convert.fix_root_cmake

        """
        input_path = os.path.join(self.tmp, "input")
        with open(input_path, "w") as fp:
            fp.write(input)
        qibuild.actions.convert.fix_root_cmake(input_path,
            "foo", dry_run=False)
        with open(input_path, "r") as fp:
            return fp.read()

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_convert_1_10(self):
        src_1_10 = os.path.join(self.tmp, "src", "1.10")
        qibuild.sh.install(
            os.path.join(self.test_dir, "src", "1.10"),
            src_1_10,
            quiet=True)
        worktree = qisrc.worktree.create(self.tmp)
        worktree.add_project(src_1_10)
        qibuild.run_action("qibuild.actions.convert",
            [src_1_10, "--go"])
        qibuild.run_action("qibuild.actions.init",
            ["--work-tree", self.tmp])
        qibuild.run_action("qibuild.actions.configure",
            ["--work-tree", self.tmp, "foo_1_10"])
        qibuild.run_action("qibuild.actions.make",
            ["--work-tree", self.tmp, "foo_1_10"])

    def test_convert_1_12(self):
        src_1_12 = os.path.join(self.tmp, "src", "1.12")
        qibuild.sh.install(
            os.path.join(self.test_dir, "src", "1.12"),
            src_1_12,
            quiet=True)
        worktree = qisrc.worktree.create(self.tmp)
        worktree.add_project(src_1_12)
        qibuild.run_action("qibuild.actions.convert",
            [src_1_12, "--go"])
        qibuild.run_action("qibuild.actions.init",
            ["--work-tree", self.tmp])
        qibuild.run_action("qibuild.actions.configure",
            ["--work-tree", self.tmp, "foo_1_12"])
        qibuild.run_action("qibuild.actions.make",
            ["--work-tree", self.tmp, "foo_1_12"])

    def test_convert_pure_cmake(self):
        src_pure_cmake = os.path.join(self.tmp, "src", "pure_cmake")
        qibuild.sh.install(
            os.path.join(self.test_dir, "src", "pure_cmake"),
            src_pure_cmake,
            quiet=True)
        worktree = qisrc.worktree.create(self.tmp)
        worktree.add_project(src_pure_cmake)
        qibuild.run_action("qibuild.actions.convert",
            [src_pure_cmake, "--go"])
        qibuild.run_action("qibuild.actions.init",
            ["--work-tree", self.tmp])
        qibuild.run_action("qibuild.actions.configure",
            ["--work-tree", self.tmp, "pure_cmake"])
        qibuild.run_action("qibuild.actions.make",
            ["--work-tree", self.tmp, "pure_cmake"])

    def test_convert_no_cmake(self):
        src_no_cmake = os.path.join(self.tmp, "src", "no_cmake")
        qibuild.sh.install(
            os.path.join(self.test_dir, "src", "no_cmake"),
            src_no_cmake,
            quiet=True)
        worktree = qisrc.worktree.create(self.tmp)
        worktree.add_project(src_no_cmake)
        qibuild.run_action("qibuild.actions.convert",
            [src_no_cmake, "--go"])
        qibuild.run_action("qibuild.actions.init",
            ["--work-tree", self.tmp])
        qibuild.run_action("qibuild.actions.configure",
            ["--work-tree", self.tmp, "no_cmake"])
        qibuild.run_action("qibuild.actions.make",
            ["--work-tree", self.tmp, "no_cmake"])


    def test_fix_cmake_pure_1_10(self):
        input = """cmake_minimum_required(VERSION 2.6)
project(foobar)
include("${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.cmake")

create_lib(foo foo.cpp)
"""
        output = self.fix_cmake_from_string(input)
        self.assertEquals("""cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)
include(qibuild/compat/compat)

create_lib(foo foo.cpp)
""", output)

    def test_fix_cmake_pure_1_12(self):
        input = """cmake_minimum_required(VERSION 2.6)
project(foobar)
include("qibuild.cmake")

qi_create_lib(foo foo.cpp)
"""
        output = self.fix_cmake_from_string(input)
        self.assertEquals("""cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)

qi_create_lib(foo foo.cpp)
""", output)

    def test_fix_cmake_1_12_with_compat_layer(self):
        input = """cmake_minimum_required(VERSION 2.6)
project(foobar)
include("qibuild.cmake")
include(qibuild/compat/compat)

create_lib(foo foo.cpp)
"""
        output = self.fix_cmake_from_string(input)
        self.assertEquals("""cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)
include(qibuild/compat/compat)

create_lib(foo foo.cpp)
""", output)

    def test_fix_cmake_1_12_1(self):
        input = """cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)

qi_create_lib(foo foo.cpp)
"""
        output = self.fix_cmake_from_string(input)
        self.assertEquals("""cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)

qi_create_lib(foo foo.cpp)
""", output)

    def test_fix_cmake_1_12_1_with_compat_layer(self):
        input = """cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)
incude(qibuild/compat/compat)

create_lib(foo foo.cpp)
"""
        output = self.fix_cmake_from_string(input)
        self.assertEquals("""cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)
incude(qibuild/compat/compat)

create_lib(foo foo.cpp)
""", output)

    def test_fix_cmake_1_12_1_with_1_12_stuff(self):
        input = """cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)
include(${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)

qi_create_lib(foo foo.cpp)
"""
        output = self.fix_cmake_from_string(input)
        self.assertEquals("""cmake_minimum_required(VERSION 2.6)
project(foobar)
find_package(qibuild)

qi_create_lib(foo foo.cpp)
""", output)



if __name__ == "__main__":
    unittest.main()
