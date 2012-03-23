## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for handling archives

"""

import os
import sys
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

    def test_zip_extract_ro_dir(self):
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        ro1 = os.path.join(src, "ro1")
        os.mkdir(ro1)
        ro2 = os.path.join(ro1, "ro2")
        os.mkdir(ro2)
        a = os.path.join(ro2, "a")
        with open(a, "w") as fp:
            fp.write("a\n")
        # RO dir inside an other RO dir
        os.chmod(ro2, stat.S_IRUSR | stat.S_IXUSR)
        os.chmod(ro1, stat.S_IRUSR | stat.S_IXUSR)
        archive = qibuild.archive.zip(src)
        dest = os.path.join(self.tmp, "dest")
        os.mkdir(dest)
        qibuild.archive.extract(archive, dest)
        ls_r = qibuild.sh.ls_r(dest)
        self.assertEquals(ls_r, ["src/ro1/ro2/a"])

    def test_extract_change_topdir(self):
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        a_long_dir = os.path.join(src, "a_long_dir")
        os.mkdir(a_long_dir)
        b = os.path.join(a_long_dir, "b")
        with open(b, "w") as fp:
            fp.write("b\n")
        dest = os.path.join(self.tmp, "dest")
        os.mkdir(dest)
        tar_gz = qibuild.archive.zip_unix(a_long_dir)
        qibuild.archive.extract(tar_gz, dest, topdir="a")
        a = os.path.join(dest, "a")
        ls_r = qibuild.sh.ls_r(a)
        self.assertEquals(ls_r, ["b"])
        a_zip = qibuild.archive.zip_win(a_long_dir)
        qibuild.archive.extract(a_zip, dest, topdir="aa")
        aa = os.path.join(dest, "aa")
        ls_r = qibuild.sh.ls_r(aa)
        self.assertEquals(ls_r, ["b"])

    def test_extract_change_topdir_already_correct(self):
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        a_dir = os.path.join(src, "a")
        os.mkdir(a_dir)
        tar_gz = qibuild.archive.zip_unix(a_dir)
        dest = os.path.join(self.tmp, "dest")
        qibuild.archive.extract(tar_gz, dest, topdir="a")
        ls_r = qibuild.sh.ls_r(dest)
        self.assertEquals(ls_r, ["a/"])

    def test_extract_with_symlink(self):
        if sys.platform.startswith("win"):
            return
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        a_dir = os.path.join(src, "a_dir")
        os.mkdir(a_dir)
        a_file = os.path.join(a_dir, "a_file")
        with open(a_file, "w") as fp:
            fp.write("a_file\n")
        a_link = os.path.join(a_dir, "a_link")
        os.symlink("a_file", a_link)
        tar_gz = qibuild.archive.zip_unix(a_dir)
        dest = os.path.join(self.tmp, "dest")
        os.mkdir(dest)
        qibuild.archive.extract(tar_gz, dest)
        ls_r = qibuild.sh.ls_r(dest)
        self.assertEquals(ls_r,
            ['a_dir/a_file', 'a_dir/a_link'])
        dest_link = os.path.join(dest, "a_dir", "a_link")
        self.assertTrue(os.path.islink(dest_link))
        dest_target = os.readlink(dest_link)
        self.assertEquals(dest_target, "a_file")

    def test_extract_with_symlink_and_change_topdir(self):
        if sys.platform.startswith("win"):
            return
        src = os.path.join(self.tmp, "src")
        os.mkdir(src)
        a_long_dir = os.path.join(src, "a_long_dir")
        os.mkdir(a_long_dir)
        a_file = os.path.join(a_long_dir, "a_file")
        with open(a_file, "w") as fp:
            fp.write("a_file\n")
        a_link = os.path.join(a_long_dir, "a_link")
        os.symlink("a_file", a_link)
        tar_gz = qibuild.archive.zip_unix(a_long_dir)
        dest = os.path.join(self.tmp, "dest")
        os.mkdir(dest)
        qibuild.archive.extract(tar_gz, dest, topdir="a_dir")
        ls_r = qibuild.sh.ls_r(dest)
        self.assertEquals(ls_r,
            ['a_dir/a_file', 'a_dir/a_link'])
        dest_link = os.path.join(dest, "a_dir", "a_link")
        self.assertTrue(os.path.islink(dest_link))
        dest_target = os.readlink(dest_link)
        self.assertEquals(dest_target, "a_file")


if __name__ == "__main__":
    unittest.main()
