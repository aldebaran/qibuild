## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
