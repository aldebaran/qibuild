## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for qitoolchain

"""

import os
import tempfile
import unittest

import qibuild
import qitoolchain


class QiToolchainTestCase(unittest.TestCase):
    def setUp(self):
        """ Small hack: set qitoolchain.CONFIG_PATH global variable
        for test

        """
        self.tmp = tempfile.mkdtemp(prefix="test-qitoolchain")
        qitoolchain.toolchain.CONFIG_PATH = os.path.join(self.tmp, "config")
        qitoolchain.toolchain.CACHE_PATH  = os.path.join(self.tmp, "cache")


    def get_tc_file_contents(self, tc):
        """ get the contents of the toolchain file of a toolchain

        """
        tc_file_path = tc.toolchain_file
        with open(tc_file_path, "r") as fp:
            contents = fp.read()
        return contents

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_setup(self):
        # Check that we are not modifying normal config
        config_path = qitoolchain.get_tc_config_path()
        expected = os.path.join(self.tmp, "config", "toolchains.cfg")
        self.assertEquals(config_path, expected)

        # Check that there are no toolchain yet
        tc_names = qitoolchain.get_tc_names()
        self.assertEquals(tc_names, list())


    def test_create_toolchain(self):
        qitoolchain.Toolchain("foo")
        self.assertEquals(qitoolchain.get_tc_names(), ["foo"])

    def test_add_package(self):
        tc = qitoolchain.Toolchain("test")

        self.assertEquals(tc.packages, list())

        foo_package = qitoolchain.toolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Check that generated toolchain file is correct
        tc_file = self.get_tc_file_contents(tc)
        self.assertTrue('list(APPEND CMAKE_PREFIX_PATH "%s")' % "/path/to/foo"
            in tc_file)

        # Check that adding the package twice does nothing
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Create a new toolchain object and check that toolchain
        # file contents did not change
        other_tc = qitoolchain.Toolchain("test")
        other_tc_file = self.get_tc_file_contents(other_tc)
        self.assertEquals(other_tc_file, tc_file)

    def test_remove_package(self):
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

        tc_file = self.get_tc_file_contents(tc)

        self.assertFalse("/path/to/foo" in tc_file)

    def test_add_package_with_tc_file(self):
        tc = qitoolchain.Toolchain("test")
        naoqi_ctc = qitoolchain.toolchain.Package("naoqi-ctc", "/path/to/ctc", "toolchain-geode.cmake")
        tc.add_package(naoqi_ctc)

        tc_file = self.get_tc_file_contents(tc)
        self.assertTrue('include("/path/to/ctc/toolchain-geode.cmake")' in tc_file, tc_file)

    def test_remove_package_with_tc_file(self):
        tc = qitoolchain.Toolchain("test")
        naoqi_ctc = qitoolchain.toolchain.Package("naoqi-ctc", "/path/to/ctc", "toolchain-geode.cmake")
        tc.add_package(naoqi_ctc)
        tc.remove_package("naoqi-ctc")

        tc_file = self.get_tc_file_contents(tc)
        self.assertFalse("toolchain-geode.cmake" in tc_file)


if __name__ == "__main__":
    unittest.main()

