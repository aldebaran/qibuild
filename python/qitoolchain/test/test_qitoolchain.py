## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for qitoolchain

"""

import os
import tempfile
import unittest

import qibuild
import qitoolchain

def get_tc_file_contents(tc):
    """ get the contents of the toolchain file of a toolchain

    """
    tc_file_path = tc.toolchain_file
    with open(tc_file_path, "r") as fp:
        contents = fp.read()
    return contents


class QiToolchainTestCase(unittest.TestCase):
    def setUp(self):
        """ Small hack: set qitoolchain.CONFIG_PATH global variable
        for test

        """
        self.tmp = tempfile.mkdtemp(prefix="test-qitoolchain")
        qitoolchain.toolchain.CONFIG_PATH = os.path.join(self.tmp, "config")
        qitoolchain.toolchain.CACHE_PATH  = os.path.join(self.tmp, "cache")
        qitoolchain.toolchain.SHARE_PATH  = os.path.join(self.tmp, "share")


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

        foo_package = qitoolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Check that generated toolchain file is correct
        tc_file = get_tc_file_contents(tc)
        self.assertTrue('list(APPEND CMAKE_PREFIX_PATH "%s")' % "/path/to/foo"
            in tc_file)

        # Check that adding the package twice does nothing
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Create a new toolchain object and check that toolchain
        # file contents did not change
        other_tc = qitoolchain.Toolchain("test")
        other_tc_file = get_tc_file_contents(other_tc)
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

        foo_package = qitoolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)

        tc.remove_package("foo")

        tc_file = get_tc_file_contents(tc)

        self.assertFalse("/path/to/foo" in tc_file)

    def test_add_package_with_tc_file(self):
        tc = qitoolchain.Toolchain("test")
        naoqi_ctc = qitoolchain.Package("naoqi-ctc", "/path/to/ctc", "toolchain-geode.cmake")
        tc.add_package(naoqi_ctc)

        tc_file = get_tc_file_contents(tc)
        self.assertTrue('include("toolchain-geode.cmake")' in tc_file, tc_file)

    def test_remove_package_with_tc_file(self):
        tc = qitoolchain.Toolchain("test")
        naoqi_ctc = qitoolchain.Package("naoqi-ctc", "/path/to/ctc", "toolchain-geode.cmake")
        tc.add_package(naoqi_ctc)
        tc.remove_package("naoqi-ctc")

        tc_file = get_tc_file_contents(tc)
        self.assertFalse("toolchain-geode.cmake" in tc_file)



class FeedTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-feed")
        self.srv = os.path.join(self.tmp, "srv")
        qitoolchain.toolchain.CONFIG_PATH = os.path.join(self.tmp, "config")
        qitoolchain.toolchain.CACHE_PATH  = os.path.join(self.tmp, "cache")
        qitoolchain.toolchain.SHARE_PATH  = os.path.join(self.tmp, "share")

    def setup_srv(self):
        this_dir = os.path.dirname(__file__)
        this_dir = qibuild.sh.to_native_path(this_dir)
        feeds_dir = os.path.join(this_dir, "feeds")
        contents = os.listdir(feeds_dir)
        for filename in contents:
            if filename.endswith(".xml"):
                self.configure_xml(filename, self.srv)

        packages_dir = os.path.join(this_dir, "packages")
        contents = os.listdir(packages_dir)
        for filename in contents:
            if filename.endswith(".tar.gz"):
                continue
            if filename.endswith(".zip"):
                continue
            package_dir = os.path.join(packages_dir, filename)
            archive = qibuild.archive.zip(package_dir)
            qibuild.sh.install(archive, self.srv, quiet=True)


    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def configure_xml(self, name, dest):
        """ Copy a xml file from the test dir to a
        dest in self.tmp

        Returns path to the created file
        Replace @srv_url@ by file://path/to/fest/feeds/ while
        doing so

        """
        this_dir = os.path.dirname(__file__)
        this_dir = qibuild.sh.to_native_path(this_dir)
        src = os.path.join(this_dir, "feeds", name)
        dest = os.path.join(self.tmp, dest)
        qibuild.sh.mkdir(dest, recursive=True)
        dest = os.path.join(dest, name)
        srv_path = qibuild.sh.to_posix_path(self.srv)
        srv_url = "file://" + srv_path
        with open(src, "r") as fp:
            lines = fp.readlines()
        lines = [l.replace("@srv_url@", srv_url) for l in lines]
        with open(dest, "w") as fp:
            fp.writelines(lines)
        return dest

    def test_sdk(self):
        # Generate a fake SDK in self.tmp
        sdk_path = os.path.join(self.tmp, "sdk")
        sdk_xml = self.configure_xml("sdk.xml", sdk_path)

        tc = qitoolchain.Toolchain("sdk")
        tc.parse_feed(sdk_xml)
        tc_file = get_tc_file_contents(tc)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("naoqi-sdk" in package_names)
        self.assertTrue(qibuild.sh.to_posix_path(sdk_path) in tc_file)

    def test_ctc(self):
        # Generate a fake ctc in self.tmp
        ctc_path = os.path.join(self.tmp, "ctc")
        ctc_xml  = self.configure_xml("ctc.xml", ctc_path)

        tc = qitoolchain.Toolchain("ctc")
        tc.parse_feed(ctc_xml)
        tc_file = get_tc_file_contents(tc)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("naoqi-geode-ctc" in package_names)
        cross_tc_path = os.path.join(ctc_path, "toolchain-geode.cmake")
        cross_tc_path = qibuild.sh.to_posix_path(cross_tc_path)
        expected  = 'include("%s")' % cross_tc_path

        self.assertTrue(expected in tc_file,
            "Did not find %s\n in\n %s" % (expected, tc_file))

    def test_ctc_nonfree(self):
        self.setup_srv()

        # Generate a fake ctc in self.tmp
        ctc_path = os.path.join(self.tmp, "ctc")
        ctc_xml  = self.configure_xml("ctc-nonfree.xml", ctc_path)

        tc = qitoolchain.Toolchain("ctc")
        tc.parse_feed(ctc_xml)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("nuance" in package_names)
        self.assertTrue("naoqi-geode-ctc" in package_names)

        nuance_path = tc.get("nuance")
        nuance_geode = os.path.join(nuance_path, "nuance-42-geode")
        nuance_atom  = os.path.join(nuance_path, "nuance-42-atom")

        self.assertTrue(os.path.exists(nuance_geode))
        self.assertFalse(os.path.exists(nuance_atom))


    def test_buildfarm(self):
        self.setup_srv()
        buildfarm_xml = os.path.join(self.srv, "buildfarm.xml")

        tc = qitoolchain.Toolchain("buildfarm")
        tc.parse_feed(buildfarm_xml)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("boost" in package_names)
        self.assertTrue("naoqi" in package_names)



if __name__ == "__main__":
    unittest.main()

