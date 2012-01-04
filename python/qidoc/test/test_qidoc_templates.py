## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import unittest
import tempfile

import qibuild.sh
import qidoc.templates


class TestQiDocTemplates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(suffix="test-qidoc-templates")

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_configure_file(self):
        in_path = os.path.join(self.tmp, "conf.py.in")
        with open(in_path, "w") as fp:
            fp.write("""# Configured by qidoc
version = {version}
""")
        out_path = os.path.join(self.tmp, "a_dir", "conf.py")
        qidoc.templates.configure_file(in_path, out_path, {"version" : "1.14"})

        with open(out_path, "r") as fp:
            out_contents = fp.read()

        self.assertEqual(out_contents,  """# Configured by qidoc
version = 1.14
""")

if __name__ == "__main__":
    unittest.main()

