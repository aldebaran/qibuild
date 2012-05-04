## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import time
import sys
import unittest
import tempfile

import qibuild.sh
import qibuild.command
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

    def test_preserve_mtime(self):
        in_path = os.path.join(self.tmp, "conf.py.in")
        with open(in_path, "w") as fp:
            fp.write("""# Configured by qidoc
version = {version}
""")
        out_path = os.path.join(self.tmp, "conf.py")
        with open(out_path, "w") as fp:
            fp.write("""# Configured by qidoc
version = 1.14
""")
        mtime_before = os.stat(out_path).st_mtime
        # Call `sync` so that we avoid false positives
        # because of filesystem cache
        if not sys.platform.startswith("win32"):
            qibuild.command.call(["sync"])
        qidoc.templates.configure_file(in_path, out_path, {"version" : "1.14"})
        with open(out_path, "r") as fp:
            out_contents = fp.read()
        self.assertEqual(out_contents,  """# Configured by qidoc
version = 1.14
""")
        mtime_after = os.stat(out_path).st_mtime
        self.assertEqual(mtime_before, mtime_after)

        qidoc.templates.configure_file(in_path, out_path, {"version" : "1.16"})
        with open(out_path, "r") as fp:
            out_contents = fp.read()
        self.assertEqual(out_contents,  """# Configured by qidoc
version = 1.16
""")

if __name__ == "__main__":
    unittest.main()

