## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for qitoolchain

"""

import os
import tempfile
import unittest

import qibuild
import qitoolchain


BAD_CMAKE_CONFIG = """
[toolchain]
cmake.flags = FOO
"""

TEST_CONFIG = """
[toolchain]
cmake.flags = FOO=BAR SPAM=EGGS
toolchain_file = /path/to/ctc/toolchain-atom.cmake
"""

EMPTY_CONFIG = """
[toolchain]
"""


class QiToolchainTestCase(unittest.TestCase):
    def setUp(self):
        """ Small hack: set qitoolchain.CONFIG_PATH global variable
        for test

        """
        self.tmp = tempfile.mkdtemp(prefix="test-qitoolchain")
        qitoolchain.toolchain.CONFIG_PATH = os.path.join(self.tmp, "config")
        qitoolchain.toolchain.CACHE_PATH  = os.path.join(self.tmp, "cache")


    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def write_conf(self, name, conf):
        """ Helper function: write a test config file for
        toolchain 'name' with config read from conf

        """
        config_path = os.path.join(self.tmp, "config", "toolchains")
        qibuild.sh.mkdir(config_path, recursive=True)
        config_path = os.path.join(config_path, name + ".cfg")
        with open(config_path, "w") as fp:
            fp.write(conf)


    def test_setup(self):
        # Check that we are not modifying normal config
        config_path = qitoolchain.get_tc_config_path()
        expected = os.path.join(self.tmp, "config", "toolchains.cfg")
        self.assertEquals(config_path, expected)

        # Check that there are no toolchain yet
        tc_names = qitoolchain.get_tc_names()
        self.assertEquals(tc_names, list())


    def test_bad_config(self):
        self.write_conf("foo", BAD_CMAKE_CONFIG)
        error = None

        try:
            qitoolchain.Toolchain("foo")
        except Exception, e:
            error = e

        self.assertFalse(error is None)
        self.assertTrue("Invalid cmake.flags setting" in str(error))

    def test_load_config(self):
        self.write_conf("foo", TEST_CONFIG)
        foo = qitoolchain.Toolchain("foo")

        self.assertEquals(qitoolchain.get_tc_names(), ["foo"])

        tc_file_path = foo.toolchain_file
        with open(tc_file_path, "r") as fp:
            tc_file = fp.read()

        self.assertTrue('set(FOO "BAR" CACHE INTERNAL "" FORCE)' in tc_file)
        self.assertTrue('include("/path/to/ctc/toolchain-atom.cmake")' in tc_file)

    def test_add_package(self):
        self.write_conf("test", EMPTY_CONFIG)
        tc = qitoolchain.Toolchain("test")

        self.assertEquals(tc.packages, list())

        foo_package = qitoolchain.toolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Check that generated toolchain file is correct
        tc_file_path = tc.toolchain_file
        with open(tc_file_path, "r") as fp:
            tc_file = fp.read()

        self.assertTrue('list(APPEND CMAKE_PREFIX_PATH "%s")' % "/path/to/foo"
            in tc_file)

        # Check that adding the package twice does nothing
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Create a new toolchain object and check that toolchain
        # file contents did not change
        other_tc = qitoolchain.Toolchain("test")
        other_tc_file_path = other_tc.toolchain_file
        with open(other_tc_file_path, "r") as fp:
            other_tc_file = fp.read()

        self.assertEquals(other_tc_file, tc_file)

    def test_remove_package(self):
        self.write_conf("test", EMPTY_CONFIG)
        tc = qitoolchain.Toolchain("test")

        error = None

        try:
            tc.remove_package("foo")
        except Exception, e:
            error = e

        self.assertFalse(error is None)
        self.assertTrue("No such package" in str(error))

        foo_package = qitoolchain.toolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)

        tc.remove_package("foo")

        tc_file_path = tc.toolchain_file
        with open(tc_file_path, "r") as fp:
            tc_file = fp.read()

        self.assertFalse("/path/to/foo" in tc_file)

    def test_no_config(self):
        """ Check that you do not need a config file to
        test a toolchain

        """
        tc = qitoolchain.Toolchain("foo")
        self.assertEquals(qitoolchain.get_tc_names(), ["foo"])


if __name__ == "__main__":
    unittest.main()

