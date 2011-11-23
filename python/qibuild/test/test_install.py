## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for qibuild.sh.install

"""

import os
import stat
import unittest
import tempfile

import qibuild

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



if __name__ == "__main__":
    unittest.main()

