## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for handling archives

"""

import os
import stat
import errno
import unittest
import tempfile

import qibuild

class ArchiveTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-archive-test")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_zip_extract(self):
        # Create some files in the temp dir:
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        # Create a empty dir called a, and two files named
        # b and c
        a = os.path.join(src, "a")
        os.mkdir(a)
        b = os.path.join(a, "b")
        with open(b, "w") as fp:
            fp.write("b\n")
        c = os.path.join(a, "c")
        with open(c, "w") as fp:
            fp.write("c\n")
        archive = qibuild.archive.zip(a)
        dest = os.path.join(self.tmp, "dest")
        os.mkdir(dest)
        qibuild.archive.extract(archive, dest)
        ls_r = qibuild.sh.ls_r(dest)
        self.assertEquals(ls_r, ["a/b", "a/c"])

    def test_zip_extract_ro(self):
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        # Create a empty dir called a, and two files named
        # b and c
        a = os.path.join(src, "a")
        os.mkdir(a)
        ro = os.path.join(a, "ro")
        with open(ro, "w") as fp:
            fp.write("ro\n")
        # 200:
        os.chmod(ro, stat.S_IRUSR)
        archive = qibuild.archive.zip(a)
        dest = os.path.join(self.tmp, "dest")
        os.mkdir(dest)
        qibuild.archive.extract(archive, dest)
        ls_r = qibuild.sh.ls_r(dest)
        self.assertEquals(ls_r, ["a/ro"])
        dest_ro = os.path.join(dest, "a", "ro")
        # check that the dest is readonly:
        error = None
        try:
            open(dest_ro, "w")
        except IOError, e:
            error = e
        self.assertFalse(error is None)
        self.assertEquals(error.errno,  errno.EACCES)


if __name__ == "__main__":
    unittest.main()
