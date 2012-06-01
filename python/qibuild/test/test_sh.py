## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import stat
import unittest
import tempfile

import qibuild.sh

class InstallTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-install-test")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_install_ro(self):
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        ro = os.path.join(src, "ro")
        with open(ro, "w") as fp:
            fp.write("ro\n")
        # 200:
        os.chmod(ro, stat.S_IRUSR)
        dest = os.path.join(self.tmp, "dest")
        qibuild.sh.install(src, dest)

def test_is_path_inside():
   assert qibuild.sh.is_path_inside("foo/bar", "foo")
   assert qibuild.sh.is_path_inside("foo", "foo/bar") is False
   assert qibuild.sh.is_path_inside("gui/bar/libfoo", "lib") is False


if __name__ == "__main__":
    unittest.main()

