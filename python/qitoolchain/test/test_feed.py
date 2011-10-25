## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for qitoolchain feeds.

"""

import os
import tempfile
import unittest

import qibuild
import qitoolchain




class FeedTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-feed")
        qitoolchain.toolchain.CONFIG_PATH = os.path.join(self.tmp, "config")
        qitoolchain.toolchain.CACHE_PATH  = os.path.join(self.tmp, "cache")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def configure_xml(self, name, dest):
        """ Copy a xml file from the test dir to a
        dest in self.tmp

        Returns path to the created file

        """
        this_dir = os.path.dirname(__file__)
        this_dir = qibuild.sh.to_native_path(this_dir)
        src = os.path.join(this_dir, "feeds", name)
        dest = os.path.join(self.tmp, dest, name)
        qibuild.sh.install(src, dest)
        return dest

    def test_sdk_parse(self):
        # Generate a fake SDK in self.tmp
        sdk = os.path.join(self.tmp, "sdk")
        sdk_xml = self.configure_xml("sdk.xml", sdk)

        tc = qitoolchain.Toolchain("sdk")
        tc.parse_feed(sdk_xml)

        print tc.toolchain_file



if __name__ == "__main__":
    unittest.main()

