## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for qitoolchain

"""

import os
import functools
import tempfile
import unittest

import mock

import qibuild
import qisys.archive
import qitoolchain

def get_tc_file_contents(tc):
    """ get the contents of the toolchain file of a toolchain

    """
    tc_file_path = tc.toolchain_file
    with open(tc_file_path, "r") as fp:
        contents = fp.read()
    return contents

def fake_get_path(tmpdir, *args):
    prefix = args[0]
    rest = args[1:]
    full_path = os.path.join(tmpdir,
                                os.path.basename(prefix),
                                *rest)
    to_make = os.path.dirname(full_path)
    qisys.sh.mkdir(to_make, recursive=True)
    return full_path

class QiToolchainTestCase(unittest.TestCase):
    def setUp(self):
        """ Small hack: set qitoolchain.CONFIG_PATH global variable
        for test

        """
        self.tmp = tempfile.mkdtemp(prefix="test-qitoolchain")

        self.path_patcher = mock.patch("qisys.sh.get_path", functools.partial(
            fake_get_path, self.tmp))
        self.path_patcher.start()
        self.cfg_patcher = mock.patch('qibuild.config.get_global_cfg_path')
        qibuild_xml = os.path.join(self.tmp, "qibuild.xml")
        with open(qibuild_xml, "w") as fp:
            fp.write("<qibuild />")
        self.get_cfg_path = self.cfg_patcher.start()
        self.get_cfg_path.return_value = os.path.join(self.tmp, "qibuild.xml")

    def tearDown(self):
        qisys.sh.rm(self.tmp)
        self.cfg_patcher.stop()
        self.path_patcher.stop()


    def test_setup(self):
        # Check that we are not modifying normal config
        config_path = qitoolchain.get_tc_config_path()
        expected = os.path.join(self.tmp, ".config", "qi", "toolchains.cfg")
        self.assertEquals(config_path, expected)

        # Check that there are no toolchain yet
        tc_names = qitoolchain.get_tc_names()
        self.assertEquals(tc_names, list())


    def test_create_toolchain(self):
        qitoolchain.Toolchain("foo")
        self.assertEquals(qitoolchain.get_tc_names(), ["foo"])

    def test_remove_toolchain(self):
        tc = qitoolchain.Toolchain("foo")
        self.assertEquals(qitoolchain.get_tc_names(), ["foo"])
        tc.remove()
        self.assertEquals(qitoolchain.get_tc_names(), list())

    def test_add_package(self):
        tc = qitoolchain.Toolchain("test")

        self.assertEquals(tc.packages, list())

        foo_package = qitoolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Check that generated toolchain file is correct
        tc_file = get_tc_file_contents(tc)
        self.assertTrue('list(INSERT CMAKE_FIND_ROOT_PATH 0 "%s")' % "/path/to/foo"
            in tc_file, tc_file)

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

    def test_tc_order(self):
        tc = qitoolchain.Toolchain("test")
        a_path  = "/path/to/a"
        b_path  = "/path/to/b"
        a_cmake = "a-config.cmake"
        b_cmake = "b-config.cmake"

        a_package   = qitoolchain.Package("a", a_path, a_cmake)
        b_package   = qitoolchain.Package("b", b_path, b_cmake)

        tc.add_package(a_package)
        tc.add_package(b_package)

        tc_file = get_tc_file_contents(tc)
        tc_file_lines = tc_file.splitlines()

        a_path_index  = 0
        b_path_index  = 0
        a_cmake_index = 0
        b_cmake_index = 0
        for (i, line) in enumerate(tc_file_lines):
            if a_cmake in line:
                a_cmake_index = i
            if b_cmake in line:
                b_cmake_index = i
            if a_path in line:
                a_path_index = i
            if b_path in line:
                b_path_index = i

        self.assertTrue(a_path_index != 0)
        self.assertTrue(b_path_index != 0)
        self.assertTrue(a_cmake_index != 0)
        self.assertTrue(b_cmake_index != 0)

        # Check that toolchain files are always written before
        # CMAKE_FIND_ROOT_PATH
        self.assertTrue(a_cmake_index < a_path_index)
        self.assertTrue(a_cmake_index < b_path_index)
        self.assertTrue(b_cmake_index < a_path_index)
        self.assertTrue(b_cmake_index < b_path_index)



class FeedTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-feed")
        self.srv = os.path.join(self.tmp, "srv")

    def setup_srv(self):
        this_dir = os.path.dirname(__file__)
        this_dir = qisys.sh.to_native_path(this_dir)
        feeds_dir = os.path.join(this_dir, "feeds")
        contents = os.listdir(feeds_dir)
        for filename in contents:
            if filename.endswith(".xml"):
                self.configure_xml(filename, self.srv)

        packages_dir = os.path.join(this_dir, "feeds", "packages")
        contents = os.listdir(packages_dir)
        for filename in contents:
            if not os.path.isdir(os.path.join(packages_dir, filename)):
                continue
            if filename.endswith(".zip"):
                continue
            package_dir = os.path.join(packages_dir, filename)
            archive = qisys.archive.compress(package_dir, algo="zip")
            qisys.sh.install(archive, self.srv, quiet=True)

    def tearDown(self):
        qisys.sh.rm(self.tmp)

    def configure_xml(self, name, dest):
        """ Copy a xml file from the test dir to a
        dest in self.tmp

        Returns path to the created file
        Replace @srv_url@ by file://path/to/fest/feeds/ while
        doing so

        """
        this_dir = os.path.dirname(__file__)
        this_dir = qisys.sh.to_native_path(this_dir)
        src = os.path.join(this_dir, "feeds", name)
        dest = os.path.join(self.tmp, dest)
        qisys.sh.mkdir(dest, recursive=True)
        dest = os.path.join(dest, name)
        if os.name == 'nt':
            srv_url = "file:///" + self.srv
        else:
            srv_url = "file://" + self.srv
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
        self.assertTrue(qisys.sh.to_posix_path(sdk_path) in tc_file)

    def test_ctc(self):
        # Generate a fake ctc in self.tmp
        ctc_path = os.path.join(self.tmp, "ctc")
        ctc_xml  = self.configure_xml("ctc.xml", ctc_path)

        qibuild_cfg = qibuild.config.QiBuildConfig()
        tc = qitoolchain.Toolchain("ctc")
        qitoolchain.feed.parse_feed(tc, ctc_xml, qibuild_cfg)

        # Check that configuration is correctly set:
        self.assertFalse(qibuild_cfg.configs.get("ctc") is None)
        self.assertEquals(qibuild_cfg.configs["ctc"].cmake.generator, "Unix Makefiles")

        # Check that generated toolchain file is correct:
        tc_file = get_tc_file_contents(tc)
        package_names = [p.name for p in tc.packages]
        self.assertTrue("naoqi-geode-ctc" in package_names)
        cross_tc_path = os.path.join(ctc_path, "toolchain-geode.cmake")
        cross_tc_path = qisys.sh.to_posix_path(cross_tc_path)
        expected  = 'include("%s")' % cross_tc_path

        self.assertTrue(expected in tc_file,
            "Did not find %s\n in\n %s" % (expected, tc_file))

        # Check that the sysroot is correct:
        self.assertEquals(tc.get_sysroot(),
            os.path.join(ctc_path, "sysroot"))


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

        self.assertTrue(os.path.exists(nuance_geode))

        ctc_path = tc.get("naoqi-geode-ctc")
        cross_tc_path = os.path.join(ctc_path, "toolchain-geode.cmake")
        cross_tc_path = qisys.sh.to_posix_path(cross_tc_path)
        self.assertTrue(os.path.exists(cross_tc_path))
        expected  = 'include("%s")' % cross_tc_path

        tc_file = get_tc_file_contents(tc)
        self.assertTrue(expected in tc_file,
            "Did not find %s\n in\n %s" % (expected, tc_file))


    def test_buildfarm(self):
        self.setup_srv()
        buildfarm_xml = os.path.join(self.srv, "buildfarm.xml")

        tc = qitoolchain.Toolchain("buildfarm")
        tc.parse_feed(buildfarm_xml)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("boost" in package_names)
        self.assertTrue("naoqi" in package_names)

    def test_blacklist(self):
        self.setup_srv()
        full_noboost_xml = os.path.join(self.srv, "full-noboost.xml")
        tc = qitoolchain.Toolchain("full-no-boost")
        tc.parse_feed(full_noboost_xml)
        package_names = [p.name for p in tc.packages]
        self.assertFalse("boost" in package_names)

    def test_master_maint(self):
        self.setup_srv()
        master_xml = os.path.join(self.srv, "master.xml")
        maint_xml  = os.path.join(self.srv, "maint.xml")

        tc_master = qitoolchain.Toolchain("master")
        tc_maint  = qitoolchain.Toolchain("maint")

        tc_master.parse_feed(master_xml)
        tc_maint.parse_feed(maint_xml)

        boost_master = tc_master.get("boost")
        boost_maint  = tc_maint.get("boost")

        boost_44 = os.path.join(boost_master, "boost-1.44-linux32")
        boost_42 = os.path.join(boost_maint , "boost-1.42-linux32")

        self.assertTrue(os.path.exists(boost_44))
        self.assertTrue(os.path.exists(boost_42))


    def test_feed_is_stored(self):
        self.setup_srv()
        buildfarm_xml = os.path.join(self.srv, "buildfarm.xml")

        tc = qitoolchain.Toolchain("buildfarm")
        tc.parse_feed(buildfarm_xml)

        self.assertEquals(tc.feed, buildfarm_xml)

        # Create a new object, and check that feed storing
        # is persistent
        tc2 = qitoolchain.Toolchain("buildfarm")
        self.assertEquals(tc2.feed, buildfarm_xml)

    def test_parse_feed_twice(self):
        self.setup_srv()
        tc = qitoolchain.Toolchain("test")
        full = os.path.join(self.srv, "full.xml")
        minimal = os.path.join(self.srv, "minimal.xml")
        tc.parse_feed(full)
        package_names = [p.name for p in tc.packages]
        package_names.sort()
        self.assertEquals(["boost", "python"], package_names)
        self.assertTrue("python" in get_tc_file_contents(tc))

        tc2 = qitoolchain.Toolchain("test")
        tc2.parse_feed(minimal)
        package_names = [p.name for p in tc2.packages]
        package_names.sort()
        self.assertEquals(["boost"], package_names)
        self.assertFalse("python" in get_tc_file_contents(tc2))

    def test_relative_url(self):
        # urrlib.urlopen() only accepts file-urls like
        # file:///C:\path\to\foo on windows, but
        # paths are often POSIX on a server, so don't bother
        # testing that on Windows
        if os.name == 'nt':
            return
        os.mkdir(self.srv)
        feeds = os.path.join(self.srv, "feeds")
        packages = os.path.join(self.srv, "packages")
        os.mkdir(feeds)
        os.mkdir(packages)

        # Create a fake package
        a_package = os.path.join(packages, "a_package")
        os.mkdir(a_package)
        a_file = os.path.join(a_package, "a_file")
        with open(a_file, "w") as fp:
            fp.write("This file is not empty\n")
        archive = qisys.archive.compress(a_package)
        package_name = os.path.basename(archive)

        # Create a fake feed:
        a_feed = os.path.join(feeds, "a_feed.xml")
        to_write = """<toolchain>
  <package name="a_package"
           url="{rel_url}"
  />
</toolchain>
"""
        rel_url = "../packages/" + package_name
        to_write = to_write.format(rel_url=rel_url)

        with open(a_feed, "w") as fp:
            fp.write(to_write)

        tc = qitoolchain.Toolchain("test")
        feed_url = "file://" + qisys.sh.to_posix_path(a_feed)
        tc.parse_feed(feed_url)

    def test_clean_cache(self):
        self.setup_srv()

        # Generate a fake ctc in self.tmp
        ctc_path = os.path.join(self.tmp, "ctc")
        ctc_xml  = self.configure_xml("ctc-nonfree.xml", ctc_path)
        tc = qitoolchain.Toolchain("ctc")
        tc.parse_feed(ctc_xml)

        tc.clean_cache(dry_run=True)
        self.assertTrue(len(os.listdir(tc.cache)) == 3)
        tc.clean_cache(dry_run=False)
        self.assertTrue(len(os.listdir(tc.cache)) == 1)

if __name__ == "__main__":
    unittest.main()
